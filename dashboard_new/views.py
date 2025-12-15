from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone

from master.models import CompanyPress
from production.models import OnlineProductionReport
from raw_data.models import Raw_data


# ─────────────────────────────────────────────────────────────
# DASHBOARD VIEW – TODAY’S DATA ONLY
# ─────────────────────────────────────────────────────────────
class DashboardNewView(View):
    """Render the new full-screen dashboard with today's production data only"""

    def get(self, request):
        try:
            today = timezone.localdate()

            # ✅ Get all presses
            presses = CompanyPress.objects.select_related('company').all()

            press_data = []

            for press in presses:
                # ✅ FIXED: press_no → press
                production_count = OnlineProductionReport.objects.filter(
                    press=press,
                    date=today
                ).count()

                completed_orders = OnlineProductionReport.objects.filter(
                    press=press,
                    date=today,
                    status='completed'
                ).count()

                press_data.append({
                    'id': press.id,
                    'name': press.name,
                    'company_name': press.company.name if press.company else 'N/A',
                    'production_count': production_count,
                    'completed_orders': completed_orders,
                })

            # JSON response (AJAX)
            if (
                request.headers.get("Accept") == "application/json"
                or request.GET.get("format") == "json"
            ):
                return JsonResponse({
                    'success': True,
                    'presses': press_data
                })

            # HTML render
            return render(
                request,
                'Dashboard_New/dashboard_new.html',
                {'presses': press_data}
            )

        except Exception as e:
            print("❌ Error in DashboardNewView:", str(e))
            return render(
                request,
                'Dashboard_New/dashboard_new.html',
                {'presses': []}
            )


# ─────────────────────────────────────────────────────────────
# PRESS DETAILS API – TODAY’S DATA ONLY
# ─────────────────────────────────────────────────────────────
class PressProductionDataView(View):
    """API endpoint to get today's production data for a specific press"""

    def get(self, request, press_id):
        try:
            today = timezone.localdate()

            # ✅ Get press
            press = CompanyPress.objects.select_related('company').get(id=press_id)

            # ✅ FIXED: press_no → press
            production_reports = OnlineProductionReport.objects.filter(
                press=press,
                date=today
            ).order_by('-created_at')

            production_data = []

            for report in production_reports:
                # ✅ CORRECT Raw_data mapping
                actual_length = Raw_data.objects.filter(
                    die_number=report.die_no
                ).aggregate(total=Sum('length'))['total'] or 0

                # ✅ Safe cut_length parsing
                try:
                    cut_length_value = float(
                        ''.join(c for c in str(report.cut_length) if c.isdigit() or c == '.')
                    )
                except Exception:
                    cut_length_value = 0

                production_qty = (
                    float(actual_length) / cut_length_value
                    if cut_length_value > 0 else 0
                )

                production_data.append({
                    'order_no': report.production_id or 'N/A',
                    'die_no': report.die_no or 'N/A',
                    'cut_length': report.cut_length or 'N/A',
                    'planned_qty': report.planned_qty or '-',
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
                    'company_name': press.company.name if press.company else 'N/A'
                },
                'production_data': production_data,
                'total_records': len(production_data)
            })

        except CompanyPress.DoesNotExist:
            return JsonResponse(
                {'success': False, 'message': 'Press not found'},
                status=404
            )

        except Exception as e:
            print("❌ Error in PressProductionDataView:", str(e))
            return JsonResponse(
                {'success': False, 'message': str(e)},
                status=500
            )
