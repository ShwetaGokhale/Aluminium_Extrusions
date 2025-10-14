from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from master.models import CompanyPress
from planning.models import ProductionPlan
from django.db.models import Sum


class DashboardNewView(View):
    """Render the new full-screen dashboard with press cards"""
    
    def get(self, request):
        try:
            # Get all presses with their production data
            presses = CompanyPress.objects.all().select_related('company').prefetch_related('production_plans')
            
            # Prepare press data with production counts
            press_data = []
            for press in presses:
                production_count = press.production_plans.count()
                total_qty = press.production_plans.aggregate(
                    total=Sum('qty')
                )['total'] or 0
                
                press_data.append({
                    'id': press.id,
                    'name': press.name,
                    'company_name': press.company.name,
                    'production_count': production_count,
                    'total_qty': total_qty
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
    """API endpoint to get production data for a specific press - Simplified version"""
    
    def get(self, request, press_id):
        try:
            # Verify press exists
            press = CompanyPress.objects.select_related('company').get(id=press_id)
            
            # Get all production plans for this press - only select needed fields
            production_plans = ProductionPlan.objects.filter(
                press=press
            ).select_related(
                'cust_requisition_id'
            ).only(
                'id',
                'die_no',
                'cut_length',
                'qty',
                'cust_requisition_id'
            ).order_by('-created_at')
            
            # Format production data - only 4 fields
            production_data = []
            for plan in production_plans:
                try:
                    production_data.append({
                        'order_no': plan.cust_requisition_id.requisition_id if plan.cust_requisition_id else 'N/A',
                        'die_no': plan.die_no or 'N/A',
                        'cut_length': plan.cut_length or 'N/A',
                        'planned_qty': plan.qty
                    })
                except Exception as e:
                    print(f"Error processing plan {plan.id}: {str(e)}")
                    continue
            
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
            return JsonResponse({
                'success': False,
                'message': 'Press not found'
            }, status=404)
        except Exception as e:
            print(f"Error in PressProductionDataView: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error loading production data: {str(e)}'
            }, status=500)