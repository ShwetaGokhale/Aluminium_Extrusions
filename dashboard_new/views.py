from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from master.models import CompanyPress
from planning.models import ProductionPlan
from django.db.models import Sum
from production.models import OnlineProductionReport
from raw_data.models import Raw_data
from django.utils import timezone

# ─────────────────────────────────────────────────────────────────────────────
# Views for Order Status - TODAY’S DATA ONLY
# ─────────────────────────────────────────────────────────────────────────────
class DashboardNewView(View):
    """Render the new full-screen dashboard with today's production data only"""

    def get(self, request):
        try:
            # Get today's date
            today = timezone.localdate()

            # Get all presses
            presses = CompanyPress.objects.all().select_related('company')

            # Prepare press data
            press_data = []
            for press in presses:
                # Count all today's reports
                production_count = OnlineProductionReport.objects.filter(
                    press_no=press,
                    date=today
                ).count()

                # Count completed today's reports
                completed_orders = OnlineProductionReport.objects.filter(
                    press_no=press,
                    date=today,
                    status='completed'
                ).count()

                press_data.append({
                    'id': press.id,
                    'name': press.name,
                    'company_name': press.company.name,
                    'production_count': production_count,
                    'completed_orders': completed_orders,
                })

            # JSON Response (AJAX)
            if (
                request.headers.get("Accept") == "application/json"
                or request.GET.get("format") == "json"
            ):
                return JsonResponse({
                    'success': True,
                    'presses': press_data
                })

            # Render HTML
            return render(
                request,
                'Dashboard_New/dashboard_new.html',
                {'presses': press_data}
            )

        except Exception as e:
            print(f"Error in DashboardNewView: {str(e)}")
            if request.headers.get("Accept") == "application/json":
                return JsonResponse({'success': False, 'message': str(e)})
            return render(request, 'Dashboard_New/dashboard_new.html', {'presses': []})


# ─────────────────────────────────────────────────────────────────────────────
# Press Details View - TODAY’S DATA ONLY
# ─────────────────────────────────────────────────────────────────────────────
class PressProductionDataView(View):
    """API endpoint to get today's production data for a specific press"""

    def get(self, request, press_id):
        try:
            # Get today's date
            today = timezone.localdate()

            # Verify press exists
            press = CompanyPress.objects.select_related('company').get(id=press_id)

            # Fetch today's online production reports for that press
            production_reports = OnlineProductionReport.objects.filter(
                press_no=press,
                date=today
            ).select_related(
                'production_plan_id'
            ).order_by('-created_at')

            production_data = []

            for report in production_reports:
                # ✅ Calculate actual production (sum of Raw_data lengths for this die_no)
                actual_length = Raw_data.objects.filter(
                    die_number=report.die_no
                ).aggregate(total=Sum('length'))['total'] or 0

                # ✅ Convert cut_length safely (handles ft, spaces, etc.)
                try:
                    cut_length_value = float(
                        ''.join([c for c in str(report.cut_length) if c.isdigit() or c == '.'])
                    )
                except:
                    cut_length_value = 0

                # ✅ Calculate production_qty = total_length / cut_length
                production_qty = float(actual_length) / cut_length_value if cut_length_value > 0 else 0

                production_data.append({
                    'order_no': (
                        report.production_plan_id.cust_requisition_id.requisition_id
                        if report.production_plan_id and report.production_plan_id.cust_requisition_id
                        else 'N/A'
                    ),
                    'die_no': report.die_no or 'N/A',
                    'cut_length': report.cut_length or 'N/A',
                    'planned_qty': report.production_plan_id.qty if report.production_plan_id else '-',
                    'current_production': float(actual_length),
                    'production_qty': round(production_qty, 2),
                    'status': report.status,
                    'status_display': report.get_status_display(),
                })

            return JsonResponse({
                'success': True,
                'press': {
                    'id': press.id,
                    'name': press.name,
                    'company_name': press.company.name
                },
                'production_data': production_data,
                'total_records': len(production_data)
            })

        except CompanyPress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Press not found'}, status=404)

        except Exception as e:
            print(f"Error in PressProductionDataView: {str(e)}")
            import traceback; traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
