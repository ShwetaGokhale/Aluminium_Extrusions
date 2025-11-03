import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import OnlineProductionReport
from master.models import CompanyPress, CompanyShift, Staff
from planning.models import ProductionPlan


class OnlineProductionReportListView(View):
    """Render the online production report list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            reports = OnlineProductionReport.objects.filter(
                production_id__icontains=search_query
            ).select_related(
                'press_no', 'shift', 'production_plan_id', 'operator'
            ).order_by("-created_at")
        else:
            reports = OnlineProductionReport.objects.all().select_related(
                'press_no', 'shift', 'production_plan_id', 'operator'
            ).order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(reports, 10)  # 10 per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        start_page = max(page_obj.number - 2, 1)
        end_page = min(page_obj.number + 2, paginator.num_pages)
        page_range = range(start_page, end_page + 1)
        
        # ---------------- JSON Response for API/Postman ----------------
        if (
            request.headers.get("Accept") == "application/json"
            or request.GET.get("format") == "json"
        ):
            reports_list = []
            for report in page_obj:
                reports_list.append({
                    'id': report.id,
                    'production_id': report.production_id,
                    'date': report.date.strftime("%Y-%m-%d") if report.date else '',
                    'cast_no': report.cast_no or '',
                    'press_no': report.press_no.name if report.press_no else '',
                    'shift': report.shift.name if report.shift else '',
                    'start_time': report.start_time.strftime("%H:%M") if report.start_time else '',
                    'end_time': report.end_time.strftime("%H:%M") if report.end_time else '',
                    'operator': report.operator.get_full_name() if report.operator else '',
                    'die_no': report.die_no,
                    'cut_length': report.cut_length,
                    'section_no': report.section_no,
                    'section_name': report.section_name,
                    'wt_per_piece': str(report.wt_per_piece) if report.wt_per_piece else '',
                    'billet_size': str(report.billet_size) if report.billet_size else '',
                    'no_of_billet': report.no_of_billet,
                    'status': report.status,
                })
            
            return JsonResponse(
                {
                    "reports": reports_list,
                    "current_page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "start_page": start_page,
                    "end_page": end_page,
                    "global_search": search_query,
                }
            )
        
        # ---------------- HTML Rendering ----------------
        return render(
            request,
            "Production/Online_Production_Report_List/online_production_report_list.html",
            {
                "page_obj": page_obj,
                "page_range": page_range,
                "current_page": page_obj.number,
                "start_page": start_page,
                "end_page": end_page,
                "total_pages": paginator.num_pages,
                "global_search": search_query,
            },
        )


class OnlineProductionReportFormView(View):
    """Render the online production report form page"""
    
    def get(self, request):
        # Generate preview of next Production ID
        next_production_id = OnlineProductionReport.generate_production_id()
        
        # Get dropdown data
        presses = CompanyPress.objects.all()
        shifts = CompanyShift.objects.all()
        production_plans = ProductionPlan.objects.all()
        staff = Staff.objects.all().order_by('first_name')

        return render(
            request,
            "Production/Online_Production_Report/online_production_report.html",
            {
                "edit_mode": False,
                "next_production_id": next_production_id,
                "presses": presses,
                "shifts": shifts,
                "production_plans": production_plans,
                "staff": staff,
            },
        )


class OnlineProductionReportEditView(View):
    """Render the online production report edit form page"""
    
    def get(self, request, pk):
        try:
            report = OnlineProductionReport.objects.select_related(
                'press_no', 'shift', 'production_plan_id', 'operator'
            ).get(id=pk)
        except OnlineProductionReport.DoesNotExist:
            return redirect("online_production_report_list")
        
        # Get dropdown data
        presses = CompanyPress.objects.all()
        shifts = CompanyShift.objects.all()
        production_plans = ProductionPlan.objects.all()
        staff = Staff.objects.all().order_by('first_name')
        
        return render(
            request,
            "Production/Online_Production_Report/online_production_report.html",
            {
                "report": report,
                "edit_mode": True,
                "presses": presses,
                "shifts": shifts,
                "production_plans": production_plans,
                "staff": staff,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class OnlineProductionReportAPI(View):
    """API for CRUD on Online Production Report"""
    
    def get(self, request):
        """Get all reports or get next Production ID"""
        # Check if requesting next Production ID
        if request.GET.get('action') == 'get_next_id':
            next_id = OnlineProductionReport.generate_production_id()
            return JsonResponse({
                'success': True,
                'next_production_id': next_id
            })
        
        # Get production plan details
        if request.GET.get('action') == 'get_production_plan_details':
            plan_id = request.GET.get('production_plan_id')
            try:
                plan = ProductionPlan.objects.select_related('die_requisition').get(id=plan_id)
                
                # Get die requisition details for section info
                section_no_value = ''
                section_name_value = ''
                
                # Get section info from die_requisition
                if plan.die_requisition:
                    die_req = plan.die_requisition
                    if die_req.section_no:
                        section_no_value = str(die_req.section_no.section_no) if hasattr(die_req.section_no, 'section_no') else str(die_req.section_no)
                    if die_req.section_name:
                        section_name_value = die_req.section_name
                
                return JsonResponse({
                    'success': True,
                    'production_plan': {
                        'die_no': plan.die_no,
                        'cut_length': plan.cut_length,
                        'wt_per_piece': str(plan.wt_per_piece),
                        'section_no': section_no_value,
                        'section_name': section_name_value
                    }
                })
            except ProductionPlan.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Production Plan not found'
                })
        
        # Otherwise return all reports
        reports = OnlineProductionReport.objects.all().select_related(
            'press_no', 'shift', 'production_plan_id', 'operator'
        ).order_by("-created_at")
        
        formatted = []
        for report in reports:
            formatted.append({
                "id": report.id,
                "production_id": report.production_id,
                "date": report.date.strftime("%Y-%m-%d") if report.date else '',
                "cast_no": report.cast_no or '',
                "press_no": report.press_no.name if report.press_no else '',
                "shift": report.shift.name if report.shift else '',
                "start_time": report.start_time.strftime("%H:%M") if report.start_time else '',
                "end_time": report.end_time.strftime("%H:%M") if report.end_time else '',
                "operator": report.operator.get_full_name() if report.operator else '',
                "production_plan_id": report.production_plan_id.production_plan_id if report.production_plan_id else '',
                "die_no": report.die_no,
                "cut_length": report.cut_length,
                "section_no": report.section_no,
                "section_name": report.section_name,
                "wt_per_piece": str(report.wt_per_piece) if report.wt_per_piece else '',
                "billet_size": str(report.billet_size) if report.billet_size else '',
                "no_of_billet": report.no_of_billet,
                "status": report.status,
                "created_at": report.created_at.strftime("%Y-%m-%d"),
            })
        return JsonResponse({"success": True, "reports": formatted})
    
    def post(self, request):
        """Create a new online production report"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if not data.get('press_no'):
                return JsonResponse({
                    "success": False,
                    "message": "Press No is required."
                })
            
            # Create production report
            report = OnlineProductionReport.objects.create(
                date=data.get('date') or None,
                cast_no=data.get('cast_no', ''),
                press_no_id=data['press_no'],
                shift_id=data.get('shift') or None,
                start_time=data.get('start_time') or None,
                end_time=data.get('end_time') or None,
                operator_id=data.get('operator') or None,
                production_plan_id_id=data.get('production_plan_id') or None,
                die_no=data.get('die_no', ''),
                cut_length=data.get('cut_length', ''),
                section_no=data.get('section_no', ''),
                section_name=data.get('section_name', ''),
                wt_per_piece=data.get('wt_per_piece') or None,
                billet_size=data.get('billet_size') or None,
                no_of_billet=data.get('no_of_billet') or None,
                status=data.get('status', 'in_progress')
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Online Production Report created successfully!",
                    "report": {
                        "id": report.id,
                        "production_id": report.production_id,
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class OnlineProductionReportDetailAPI(View):
    """API for get, edit & delete Online Production Report"""
    
    def post(self, request, pk):
        """Update production report"""
        try:
            report = get_object_or_404(OnlineProductionReport, id=pk)
            data = json.loads(request.body)
            
            # Update fields
            report.date = data.get('date') or report.date
            report.cast_no = data.get('cast_no', report.cast_no)
            report.press_no_id = data.get('press_no', report.press_no_id)
            report.shift_id = data.get('shift') or report.shift_id
            report.start_time = data.get('start_time') or report.start_time
            report.end_time = data.get('end_time') or report.end_time
            report.operator_id = data.get('operator') or report.operator_id
            report.production_plan_id_id = data.get('production_plan_id') or report.production_plan_id_id
            report.die_no = data.get('die_no', report.die_no)
            report.cut_length = data.get('cut_length', report.cut_length)
            report.section_no = data.get('section_no', report.section_no)
            report.section_name = data.get('section_name', report.section_name)
            report.wt_per_piece = data.get('wt_per_piece') or report.wt_per_piece
            report.billet_size = data.get('billet_size') or report.billet_size
            report.no_of_billet = data.get('no_of_billet') or report.no_of_billet
            report.status = data.get('status', report.status)
            report.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Online Production Report updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete production report"""
        try:
            report = get_object_or_404(OnlineProductionReport, id=pk)
            report.delete()
            return JsonResponse({
                "success": True,
                "message": "Online Production Report deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class OnlineProductionReportDeleteView(View):
    """Delete production report view"""
    
    def post(self, request, pk):
        try:
            report = get_object_or_404(OnlineProductionReport, id=pk)
            report.delete()
            return JsonResponse({"success": True, "message": "Online Production Report deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})