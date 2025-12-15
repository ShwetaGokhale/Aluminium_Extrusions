from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime

from production.models import OnlineProductionReport
from order_management.models import Requisition


# ==================== DASHBOARD VIEWS ====================

class DashboardView(View):
    """Render the production dashboard with real data"""
    
    def get(self, request):
        filter_type = request.GET.get('filter', 'today')
        selected_date = request.GET.get('date', None)
        recovery_stats = self.get_recovery_stats(filter_type, selected_date)
        order_stats = self.get_order_stats(filter_type, selected_date)
        
        context = {
            'recovery_stats': recovery_stats,
            'order_stats': order_stats,
            'filter_type': filter_type,
            'selected_date': selected_date
        }
        
        return render(request, 'Dashboard/dashboard.html', context)
    
    def get_recovery_stats(self, filter_type, selected_date=None):
        """Calculate recovery statistics based on filter type or selected date"""
        
        if selected_date:
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                start_date = date_obj
                end_date = date_obj
            except ValueError:
                today = timezone.now().date()
                start_date = today
                end_date = today
        else:
            today = timezone.now().date()
            
            if filter_type == 'today':
                start_date = today
                end_date = today
            elif filter_type == 'weekly':
                start_date = today - timedelta(days=7)
                end_date = today
            elif filter_type == 'monthly':
                start_date = today - timedelta(days=30)
                end_date = today
            else:
                start_date = today
                end_date = today
        
        reports = OnlineProductionReport.objects.filter(
            date_of_production__gte=start_date,
            date_of_production__lte=end_date
        ).select_related('press')
        
        total_input = reports.aggregate(total=Sum('input_qty'))['total'] or 0
        total_output = reports.aggregate(total=Sum('total_output'))['total'] or 0
        unique_presses = reports.values('press').distinct().count()
        
        if total_output > 0:
            recovery_percent = round((total_input / total_output) * 100)
        else:
            recovery_percent = 0
        
        return {
            'recovery_percent': recovery_percent,
            'press_count': unique_presses,
            'total_input': round(total_input, 2),
            'total_output': round(total_output, 2)
        }
    
    def get_order_stats(self, filter_type, selected_date=None):
        """Calculate order statistics from OnlineProductionReport"""
        
        if selected_date:
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                start_date = date_obj
                end_date = date_obj
            except ValueError:
                today = timezone.now().date()
                start_date = today
                end_date = today
        else:
            today = timezone.now().date()
            
            if filter_type == 'today':
                start_date = today
                end_date = today
            elif filter_type == 'weekly':
                start_date = today - timedelta(days=7)
                end_date = today
            elif filter_type == 'monthly':
                start_date = today - timedelta(days=30)
                end_date = today
            else:
                start_date = today
                end_date = today
        
        reports = OnlineProductionReport.objects.filter(
            date_of_production__gte=start_date,
            date_of_production__lte=end_date
        )
        
        total_orders = reports.count()
        completed = reports.filter(status='completed').count()
        in_progress = reports.filter(status='in_progress').count()
        cancelled = reports.filter(status='cancelled').count()
        
        return {
            'total_orders': total_orders,
            'completed': completed,
            'in_progress': in_progress,
            'cancelled': cancelled
        }


@method_decorator(csrf_exempt, name="dispatch")
class DashboardRecoveryTableAPI(View):
    """API to fetch recovery table data for dashboard"""
    
    def get(self, request):
        filter_type = request.GET.get('filter', 'today')
        selected_date = request.GET.get('date', None)
        
        if selected_date:
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                start_date = date_obj
                end_date = date_obj
            except ValueError:
                today = timezone.now().date()
                start_date = today
                end_date = today
        else:
            today = timezone.now().date()
            
            if filter_type == 'today':
                start_date = today
                end_date = today
            elif filter_type == 'weekly':
                start_date = today - timedelta(days=7)
                end_date = today
            elif filter_type == 'monthly':
                start_date = today - timedelta(days=30)
                end_date = today
            else:
                start_date = today
                end_date = today
        
        reports = OnlineProductionReport.objects.filter(
            date_of_production__gte=start_date,
            date_of_production__lte=end_date
        ).select_related('press').order_by('-date_of_production')[:10]
        
        reports_list = []
        for report in reports:
            reports_list.append({
                'die_no': report.die_no,
                'no_of_cavity': report.no_of_cavity,
                'press': report.press.name if report.press else '',
                'input_qty': float(report.input_qty) if report.input_qty else 0,
                'total_output': float(report.total_output) if report.total_output else 0
            })
        
        return JsonResponse({
            'success': True,
            'reports': reports_list
        })


@method_decorator(csrf_exempt, name="dispatch")
class DashboardOrderTableAPI(View):
    """API to fetch order table data from OnlineProductionReport for dashboard"""
    
    def get(self, request):
        filter_type = request.GET.get('filter', 'today')
        selected_date = request.GET.get('date', None)
        
        if selected_date:
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                start_date = date_obj
                end_date = date_obj
            except ValueError:
                today = timezone.now().date()
                start_date = today
                end_date = today
        else:
            today = timezone.now().date()
            
            if filter_type == 'today':
                start_date = today
                end_date = today
            elif filter_type == 'weekly':
                start_date = today - timedelta(days=7)
                end_date = today
            elif filter_type == 'monthly':
                start_date = today - timedelta(days=30)
                end_date = today
            else:
                start_date = today
                end_date = today
        
        # Fetch from OnlineProductionReport instead of Requisition
        reports = OnlineProductionReport.objects.filter(
            date_of_production__gte=start_date,
            date_of_production__lte=end_date
        ).order_by('-date_of_production')[:10]
        
        orders_list = []
        for report in reports:
            orders_list.append({
                'production_id': report.production_id,
                'status': report.status
            })
        
        return JsonResponse({
            'success': True,
            'orders': orders_list
        })


@method_decorator(csrf_exempt, name="dispatch")
class DashboardProductionTableAPI(View):
    """API to fetch production table data for dashboard"""
    
    def get(self, request):
        filter_type = request.GET.get('filter', 'today')
        selected_date = request.GET.get('date', None)
        
        if selected_date:
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                start_date = date_obj
                end_date = date_obj
            except ValueError:
                today = timezone.now().date()
                start_date = today
                end_date = today
        else:
            today = timezone.now().date()
            
            if filter_type == 'today':
                start_date = today
                end_date = today
            elif filter_type == 'weekly':
                start_date = today - timedelta(days=7)
                end_date = today
            elif filter_type == 'monthly':
                start_date = today - timedelta(days=30)
                end_date = today
            else:
                start_date = today
                end_date = today
        
        reports = OnlineProductionReport.objects.filter(
            date_of_production__gte=start_date,
            date_of_production__lte=end_date
        ).select_related('press', 'operator').order_by('-date_of_production')[:10]
        
        reports_list = []
        for report in reports:
            reports_list.append({
                'die_no': report.die_no,
                'cut_length': report.cut_length,
                'operator': report.operator.get_full_name() if report.operator else '',
                'status': report.status
            })
        
        return JsonResponse({
            'success': True,
            'reports': reports_list
        })