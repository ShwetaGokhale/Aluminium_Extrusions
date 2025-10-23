from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from planning.models import ProductionPlan
from django.db.models import Sum, Count


class DashboardView(APIView):
    """Render the dashboard with die-wise production data"""
    
    def get(self, request, *args, **kwargs):
        try:
            # Get all production plans and group by die_no
            production_plans = ProductionPlan.objects.select_related(
                'press', 'press__company', 'cust_requisition_id'
            ).exclude(die_no__isnull=True).exclude(die_no='')
            
            # Group by die_no and aggregate data
            die_data_dict = {}
            
            for plan in production_plans:
                die_no = plan.die_no
                if die_no not in die_data_dict:
                    die_data_dict[die_no] = {
                        'die_no': die_no,
                        'production_count': 0,
                        'total_qty': 0,
                        'cut_length': plan.cut_length or 'N/A',  # Take first cut_length
                        'presses': set()
                    }
                
                die_data_dict[die_no]['production_count'] += 1
                die_data_dict[die_no]['total_qty'] += plan.qty or 0
                if plan.press:
                    die_data_dict[die_no]['presses'].add(plan.press.name)
            
            # Convert to list and format
            die_data = []
            for die_no, data in die_data_dict.items():
                die_data.append({
                    'die_no': die_no,
                    'production_count': data['production_count'],
                    'total_qty': data['total_qty'],
                    'cut_length': data['cut_length'],
                    'presses': ', '.join(sorted(data['presses'])) if data['presses'] else 'N/A'
                })
            
            # Sort by production count (descending)
            die_data.sort(key=lambda x: x['production_count'], reverse=True)
            
            context = {
                'dies': die_data
            }
            
            return render(request, "Dashboard/dashboard.html", context)
            
        except Exception as e:
            print(f"Error in DashboardView: {str(e)}")
            import traceback
            traceback.print_exc()
            return render(request, "Dashboard/dashboard.html", {
                'dies': []
            })


class DieProductionDataView(View):
    """API endpoint to get production data for a specific die"""
    
    def get(self, request, die_no):
        try:
            # Get all production plans for this die
            production_plans = ProductionPlan.objects.filter(
                die_no=die_no
            ).select_related(
                'press', 'press__company', 'cust_requisition_id'
            ).order_by('-created_at')
            
            if not production_plans.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Die not found or no production plans'
                }, status=404)
            
            # Format production data
            production_data = []
            for plan in production_plans:
                try:
                    production_data.append({
                        'order_no': plan.cust_requisition_id.requisition_id if plan.cust_requisition_id else 'N/A',
                        'press_name': plan.press.name if plan.press else 'N/A',
                        'die_no': plan.die_no or 'N/A',
                        'cut_length': plan.cut_length or 'N/A',
                        'planned_qty': plan.qty or 0,
                        'status': plan.status if hasattr(plan, 'status') else 'planned',
                        'status_display': plan.get_status_display() if hasattr(plan, 'get_status_display') else 'Planned'
                    })
                except Exception as e:
                    print(f"Error processing plan {plan.id}: {str(e)}")
                    continue
            
            return JsonResponse({
                'success': True,
                'die': {
                    'die_no': die_no,
                    'total_plans': len(production_data)
                },
                'production_data': production_data
            })
            
        except Exception as e:
            print(f"Error in DieProductionDataView: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error loading production data: {str(e)}'
            }, status=500)