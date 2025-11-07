from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from master.models import CompanyPress
from planning.models import ProductionPlan
from django.db.models import Sum
from production.models import OnlineProductionReport

# ─────────────────────────────────────────────────────────────────────────────
# Views for Order Status
# ─────────────────────────────────────────────────────────────────────────────
class DashboardNewView(View):
    """Render the new full-screen dashboard with press cards"""
    
    def get(self, request):
        try:
            # Get all presses with their production data
            presses = CompanyPress.objects.all().select_related('company').prefetch_related('production_plans')
            
            # Prepare press data with production counts
            press_data = []
            for press in presses:
                # Total records in OnlineProductionReport for this press
                production_count = OnlineProductionReport.objects.filter(
                    press_no=press
                ).count()

            # Completed records for this press based on status field in OnlineProductionReport
            completed_orders = OnlineProductionReport.objects.filter(
                press_no=press,
                status='completed'
            ).count()

            press_data.append({
                'id': press.id,
                'name': press.name,
                'company_name': press.company.name,
                'production_count': production_count,
                'completed_orders': completed_orders,
            })

            
            # Check if JSON response is requested (for AJAX)
            if (
                request.headers.get("Accept") == "application/json"
                or request.GET.get("format") == "json"
            ):
                return JsonResponse({
                    'success': True,
                    'presses': press_data
                })
            
            # HTML rendering
            return render(
                request,
                'Dashboard_New/dashboard_new.html',
                {
                    'presses': press_data
                }
            )
        except Exception as e:
            print(f"Error in DashboardNewView: {str(e)}")
            if request.headers.get("Accept") == "application/json":
                return JsonResponse({'success': False, 'message': str(e)})
            return render(request, 'Dashboard_New/dashboard_new.html', {'presses': []})


class PressProductionDataView(View):
    """API endpoint to get production data for a specific press with status from OnlineProductionReport"""

    def get(self, request, press_id):
        try:
            # Verify press exists
            press = CompanyPress.objects.select_related('company').get(id=press_id)

            # Fetch online production records for that press
            production_reports = OnlineProductionReport.objects.filter(
                press_no=press
            ).select_related(
                'production_plan_id'
            ).order_by('-created_at')

            # Prepare response data
            production_data = []
            for report in production_reports:
                production_data.append({
                    'order_no': report.production_plan_id.cust_requisition_id.requisition_id if report.production_plan_id and report.production_plan_id.cust_requisition_id else 'N/A',
                    'die_no': report.die_no or 'N/A',
                    'cut_length': report.cut_length or 'N/A',
                    'planned_qty': report.production_plan_id.qty if report.production_plan_id else '-',
                    'status': report.status,
                    'status_display': report.get_status_display(),  # Human readable version
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
        
