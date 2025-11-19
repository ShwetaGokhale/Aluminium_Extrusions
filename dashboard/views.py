from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from production.models import OnlineProductionReport
from raw_data.models import Raw_data
from master.models import Die
from django.utils import timezone
from datetime import datetime, time, timedelta


# ─────────────────────────────────────────────────────────────────────────────
# Views for Dashboard - with Daily/Weekly/Monthly filtering
# ─────────────────────────────────────────────────────────────────────────────
class DashboardView(View):
    """Render the IOT Dashboard with die cards - with date range filtering"""

    def get(self, request):
        try:
            # ✅ Get the filter type from query parameter (default: daily)
            filter_type = request.GET.get('filter', 'daily')
            
            # ✅ Calculate date range based on filter type
            today = timezone.now().date()
            
            if filter_type == 'weekly':
                # Get start of current week (Monday)
                start_date = today - timedelta(days=today.weekday())
                end_date = today
            elif filter_type == 'monthly':
                # Get start of current month
                start_date = today.replace(day=1)
                end_date = today
            else:  # daily (default)
                start_date = today
                end_date = today

            # Get die card data
            die_data = self.get_die_cards_data(start_date, end_date)

            # ✅ Get order status counts - Filter by date range
            total_ordered = OnlineProductionReport.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            ).count()

            completed_orders = OnlineProductionReport.objects.filter(
                status='completed',
                date__gte=start_date,
                date__lte=end_date
            ).count()

            in_progress_orders = OnlineProductionReport.objects.filter(
                status='in_progress',
                date__gte=start_date,
                date__lte=end_date
            ).count()

            # Get shift information from latest production report in date range
            latest_report = OnlineProductionReport.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            ).select_related('shift', 'press_no').order_by('-created_at').first()

            shift_number = 1
            shift_start = None
            shift_end = None
            shift_date = today
            machine_state = "RUN"

            if latest_report:
                # Get shift info
                if latest_report.shift:
                    shift_number = latest_report.shift.name if hasattr(latest_report.shift, 'name') else 1
                
                # Combine date with start_time and end_time
                if latest_report.start_time:
                    shift_start = datetime.combine(latest_report.date, latest_report.start_time)
                if latest_report.end_time:
                    shift_end = datetime.combine(latest_report.date, latest_report.end_time)
                
                # Get the date from the report
                shift_date = latest_report.date

            context = {
                'die_cards': die_data,
                'total_ordered': total_ordered,
                'completed_orders': completed_orders,
                'in_progress_orders': in_progress_orders,
                'shift_number': shift_number,
                'shift_start': shift_start,
                'shift_end': shift_end,
                'shift_date': shift_date,
                'machine_state': machine_state,
                'today_date': timezone.now(),
                'filter_type': filter_type,  # Pass filter type to template
                'start_date': start_date,
                'end_date': end_date,
            }

            # Check for JSON (AJAX) requests
            if (
                request.headers.get("Accept") == "application/json"
                or request.GET.get("format") == "json"
            ):
                return JsonResponse({
                    'success': True,
                    'die_cards': die_data,
                    'order_stats': {
                        'total_ordered': total_ordered,
                        'completed_orders': completed_orders,
                        'in_progress_orders': in_progress_orders,
                    },
                    'filter_type': filter_type,
                })

            return render(request, 'dashboard/dashboard.html', context)

        except Exception as e:
            print(f"Error in DashboardView: {str(e)}")
            import traceback
            traceback.print_exc()

            if request.headers.get("Accept") == "application/json":
                return JsonResponse({'success': False, 'message': str(e)})
            return render(request, 'dashboard/dashboard.html', {
                'die_cards': [],
                'total_ordered': 0,
                'completed_orders': 0,
                'in_progress_orders': 0,
                'filter_type': 'daily',
            })

    # ────────────────────────────────────────────────────────────────
    # Helper Method: Get Die Card Data
    # ────────────────────────────────────────────────────────────────
    def get_die_cards_data(self, start_date, end_date):
        """Get die card data with die names, order counts, and cut lengths - with date range"""
        try:
            # ✅ Fetch unique dies - Filter by date range
            dies = OnlineProductionReport.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            ).values('die_no').annotate(
                order_count=Count('id'),
                total_production=Sum('production_plan_id__qty')
            ).order_by('-order_count')[:4]

            die_cards = []
            colors = ['green', 'orange', 'yellow', 'blue']

            for idx, die in enumerate(dies):
                die_no = die['die_no']

                # Get die name from Die model
                try:
                    die_obj = Die.objects.get(die_no=die_no)
                    die_name = die_obj.die_name if die_obj.die_name else die_no
                except Die.DoesNotExist:
                    die_name = die_no

                order_count = die['order_count']

                # ✅ Get cut length for this die - within date range
                cut_length_data = OnlineProductionReport.objects.filter(
                    die_no=die_no,
                    date__gte=start_date,
                    date__lte=end_date
                ).values_list('cut_length', flat=True).first()

                # Extract numeric value from cut length (e.g., "16ft" -> 16)
                cut_length_value = 0
                if cut_length_data:
                    try:
                        cut_length_value = int(float(
                            ''.join([c for c in str(cut_length_data) if c.isdigit() or c == '.'])
                        ))
                    except:
                        cut_length_value = 0

                # ✅ Calculate total current production length - within date range
                # If Raw_data has a date field, filter by it
                # Otherwise, this gets ALL production for this die number
                actual_length = Raw_data.objects.filter(
                    die_number=die_no
                    # If Raw_data has a date field, add: date__gte=start_date, date__lte=end_date
                    # If it has created_at, use: created_at__date__gte=start_date, created_at__date__lte=end_date
                ).aggregate(total=Sum('length'))['total'] or 0

                # Planned quantity (from production plan) - within date range
                planned_qty = die['total_production'] or 0

                # Production quantity = total length / cut length (keep as decimal)
                production_qty = 0
                if cut_length_value > 0:
                    production_qty = float(actual_length) / float(cut_length_value)

                # ✅ Current Production as Percentage (Production Qty / Planned Qty * 100)
                current_production_percent = 0
                if planned_qty > 0:
                    current_production_percent = round((production_qty / planned_qty) * 100, 2)

                # Append final card data
                die_cards.append({
                    'die_no': die_name,
                    'order_count': order_count,
                    'planned_qty': planned_qty,
                    'cut_length': f"{cut_length_value}ft" if cut_length_value > 0 else "N/A",
                    'current_production': round(current_production_percent, 2),
                    'production_qty': round(production_qty, 2),  # Keep as decimal with 2 places
                    'color': colors[idx % 4],
                })

            # Fill up to 4 cards (if less data)
            while len(die_cards) < 4:
                die_cards.append({
                    'die_no': 'No Data',
                    'order_count': 0,
                    'planned_qty': 0,
                    'cut_length': 'N/A',
                    'current_production': 0,
                    'production_qty': 0,
                    'color': colors[len(die_cards) % 4],
                })

            return die_cards

        except Exception as e:
            print(f"Error in get_die_cards_data: {str(e)}")
            import traceback
            traceback.print_exc()
            return []