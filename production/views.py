import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import OnlineProductionReport
from master.models import CompanyPress, CompanyShift, Staff
from planning.models import ProductionPlan, DieRequisition
from .models import DailyProductionReport
from .forms import OnlineProductionReportForm
from raw_data.models import Raw_data
from master.models import Die
from datetime import datetime
from django.db.models import Q

# ─────────────────────────────────────────────────────────────────────────────
# Views for Online Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class OnlineProductionReportListView(View):
    """Render the online production report list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            reports = OnlineProductionReport.objects.filter(
                Q(production_id__icontains=search_query) |
                Q(die_no__icontains=search_query) |
                Q(section_no__icontains=search_query)
            ).select_related(
                'press', 'shift', 'die_requisition', 'operator'
            ).order_by("-created_at")
        else:
            reports = OnlineProductionReport.objects.all().select_related(
                'press', 'shift', 'die_requisition', 'operator'
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
                    'date_of_production': report.date_of_production.strftime("%Y-%m-%d") if report.date_of_production else '',
                    'die_requisition_id': report.die_requisition.die_requisition_id if report.die_requisition else '',
                    'die_no': report.die_no,
                    'section_no': report.section_no,
                    'section_name': report.section_name,
                    'wt_per_piece_general': str(report.wt_per_piece_general) if report.wt_per_piece_general else '',
                    'no_of_cavity': report.no_of_cavity,
                    'cut_length': report.cut_length,
                    'press': report.press.name if report.press else '',
                    'shift': report.shift.name if report.shift else '',
                    'operator': report.operator.get_full_name() if report.operator else '',
                    'planned_qty': report.planned_qty,
                    'start_time': report.start_time.strftime("%H:%M") if report.start_time else '',
                    'end_time': report.end_time.strftime("%H:%M") if report.end_time else '',
                    'billet_size': report.billet_size,
                    'no_of_billet': report.no_of_billet,
                    'weight': str(report.weight) if report.weight else '',
                    'input_qty': str(report.input_qty) if report.input_qty else '',
                    'wt_per_piece_output': str(report.wt_per_piece_output) if report.wt_per_piece_output else '',
                    'no_of_pieces': report.no_of_pieces,
                    'total_output': str(report.total_output) if report.total_output else '',
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
        presses = CompanyPress.objects.all().order_by('name')
        shifts = CompanyShift.objects.all().order_by('name')
        staff = Staff.objects.all().order_by('first_name')
        die_requisitions = DieRequisition.objects.all().order_by('-created_at')

        return render(
            request,
            "Production/Online_Production_Report/online_production_report.html",
            {
                "edit_mode": False,
                "next_production_id": next_production_id,
                "presses": presses,
                "shifts": shifts,
                "staff": staff,
                "die_requisitions": die_requisitions,
            },
        )


class OnlineProductionReportEditView(View):
    """Render the online production report edit form page"""
    
    def get(self, request, pk):
        try:
            report = OnlineProductionReport.objects.select_related(
                'press', 'shift', 'die_requisition', 'operator'
            ).get(id=pk)
        except OnlineProductionReport.DoesNotExist:
            return redirect("online_production_report_list")
        
        # Get dropdown data
        presses = CompanyPress.objects.all().order_by('name')
        shifts = CompanyShift.objects.all().order_by('name')
        staff = Staff.objects.all().order_by('first_name')
        die_requisitions = DieRequisition.objects.all().order_by('-created_at')
        
        return render(
            request,
            "Production/Online_Production_Report/online_production_report.html",
            {
                "report": report,
                "edit_mode": True,
                "presses": presses,
                "shifts": shifts,
                "staff": staff,
                "die_requisitions": die_requisitions,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class OnlineProductionReportAPI(View):
    """API for CRUD on Online Production Report"""
    
    def get(self, request):
        """Get all reports, next Production ID, or die requisition details"""
        
        # Check if requesting next Production ID
        if request.GET.get('action') == 'get_next_id':
            next_id = OnlineProductionReport.generate_production_id()
            return JsonResponse({
                'success': True,
                'next_production_id': next_id
            })
        
        # Get die requisitions by date of production
        if request.GET.get('action') == 'get_die_requisitions_by_date':
            date_str = request.GET.get('date_of_production')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Get unique die requisitions from production plans for this date
                production_plans = ProductionPlan.objects.filter(
                    date_of_production=date_obj
                ).select_related('die_requisition').exclude(
                    die_requisition__isnull=True
                )
                
                # Extract unique die requisitions
                seen = set()
                requisitions_list = []
                for plan in production_plans:
                    if plan.die_requisition and plan.die_requisition.id not in seen:
                        seen.add(plan.die_requisition.id)
                        requisitions_list.append({
                            'id': plan.die_requisition.id,
                            'die_requisition_id': plan.die_requisition.die_requisition_id if hasattr(plan.die_requisition, 'die_requisition_id') else str(plan.die_requisition.id)
                        })
                
                return JsonResponse({
                    'success': True,
                    'die_requisitions': requisitions_list
                })
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid date format: {str(e)}'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
        
        # Get die requisition details from production plan
        if request.GET.get('action') == 'get_die_requisition_details':
            die_req_id = request.GET.get('die_requisition_id')
            date_prod = request.GET.get('date_of_production')
            
            try:
                date_obj = datetime.strptime(date_prod, '%Y-%m-%d').date()
                
                # Find production plan with matching die requisition and date
                plan = ProductionPlan.objects.filter(
                    die_requisition_id=die_req_id,
                    date_of_production=date_obj
                ).select_related(
                    'die_requisition',
                    'press',
                    'shift',
                    'operator'
                ).first()
                
                if plan:
                    return JsonResponse({
                        'success': True,
                        'details': {
                            'die_no': plan.die_no,
                            'section_no': plan.section_no,
                            'section_name': plan.section_name,
                            'wt_per_piece': str(plan.wt_per_piece) if plan.wt_per_piece else '',
                            'no_of_cavity': plan.no_of_cavity,
                            'cut_length': plan.cut_length,
                            'press': plan.press.id if plan.press else '',
                            'shift': plan.shift.id if plan.shift else '',
                            'operator': plan.operator.id if plan.operator else '',
                            'planned_qty': plan.planned_qty if plan.planned_qty else '',
                            'billet_size': plan.billet_size,
                            'no_of_billet': plan.no_of_billet if plan.no_of_billet else ''
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Production Plan not found for the selected Die Requisition and Date'
                    })
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid date format: {str(e)}'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
        
        # Otherwise return all reports
        reports = OnlineProductionReport.objects.all().select_related(
            'press', 'shift', 'die_requisition', 'operator'
        ).order_by("-created_at")
        
        formatted = []
        for report in reports:
            formatted.append({
                "id": report.id,
                "production_id": report.production_id,
                "date": report.date.strftime("%Y-%m-%d") if report.date else '',
                "date_of_production": report.date_of_production.strftime("%Y-%m-%d") if report.date_of_production else '',
                "die_requisition_id": report.die_requisition.die_requisition_id if report.die_requisition else '',
                "die_no": report.die_no,
                "section_no": report.section_no,
                "section_name": report.section_name,
                "wt_per_piece_general": str(report.wt_per_piece_general) if report.wt_per_piece_general else '',
                "no_of_cavity": report.no_of_cavity,
                "cut_length": report.cut_length,
                "press": report.press.name if report.press else '',
                "shift": report.shift.name if report.shift else '',
                "operator": report.operator.get_full_name() if report.operator else '',
                "planned_qty": report.planned_qty,
                "start_time": report.start_time.strftime("%H:%M") if report.start_time else '',
                "end_time": report.end_time.strftime("%H:%M") if report.end_time else '',
                "billet_size": report.billet_size,
                "no_of_billet": report.no_of_billet,
                "weight": str(report.weight) if report.weight else '',
                "input_qty": str(report.input_qty) if report.input_qty else '',
                "wt_per_piece_output": str(report.wt_per_piece_output) if report.wt_per_piece_output else '',
                "no_of_pieces": report.no_of_pieces,
                "total_output": str(report.total_output) if report.total_output else '',
                "status": report.status,
                "created_at": report.created_at.strftime("%Y-%m-%d"),
            })
        return JsonResponse({"success": True, "reports": formatted})
    
    def post(self, request):
        """Create a new online production report"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if not data.get('date'):
                return JsonResponse({
                    "success": False,
                    "message": "Date is required."
                })
            
            if not data.get('date_of_production'):
                return JsonResponse({
                    "success": False,
                    "message": "Date of Production is required."
                })
            
            if not data.get('die_requisition'):
                return JsonResponse({
                    "success": False,
                    "message": "Die Requisition ID is required."
                })
            
            if not data.get('press'):
                return JsonResponse({
                    "success": False,
                    "message": "Press is required."
                })
            
            # Create production report
            report = OnlineProductionReport.objects.create(
                date=data.get('date'),
                date_of_production=data.get('date_of_production'),
                die_requisition_id=data.get('die_requisition'),
                die_no=data.get('die_no', ''),
                section_no=data.get('section_no', ''),
                section_name=data.get('section_name', ''),
                wt_per_piece_general=data.get('wt_per_piece_general') or None,
                no_of_cavity=data.get('no_of_cavity', ''),
                cut_length=data.get('cut_length', ''),
                press_id=data['press'],
                shift_id=data.get('shift') or None,
                operator_id=data.get('operator') or None,
                planned_qty=data.get('planned_qty') or None,
                start_time=data.get('start_time') or None,
                end_time=data.get('end_time') or None,
                billet_size=data.get('billet_size', ''),
                no_of_billet=data.get('no_of_billet') or None,
                weight=data.get('weight') or None,
                input_qty=data.get('input_qty') or None,
                wt_per_piece_output=data.get('wt_per_piece_output') or None,
                no_of_pieces=data.get('no_of_pieces') or None,
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
                        "total_output": str(report.total_output) if report.total_output else ''
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class OnlineProductionReportDetailAPI(View):
    """API for get, edit & delete Online Production Report"""
    
    def get(self, request, pk):
        """Get a single production report"""
        try:
            report = get_object_or_404(OnlineProductionReport.objects.select_related(
                'press', 'shift', 'die_requisition', 'operator'
            ), id=pk)
            
            report_data = {
                "id": report.id,
                "production_id": report.production_id,
                "date": report.date.strftime("%Y-%m-%d") if report.date else '',
                "date_of_production": report.date_of_production.strftime("%Y-%m-%d") if report.date_of_production else '',
                "die_requisition_id": report.die_requisition.id if report.die_requisition else None,
                "die_requisition_code": report.die_requisition.die_requisition_id if report.die_requisition else '',
                "die_no": report.die_no,
                "section_no": report.section_no,
                "section_name": report.section_name,
                "wt_per_piece_general": str(report.wt_per_piece_general) if report.wt_per_piece_general else '',
                "no_of_cavity": report.no_of_cavity,
                "cut_length": report.cut_length,
                "press_id": report.press.id if report.press else None,
                "press_name": report.press.name if report.press else '',
                "shift_id": report.shift.id if report.shift else None,
                "shift_name": report.shift.name if report.shift else '',
                "operator_id": report.operator.id if report.operator else None,
                "operator_name": report.operator.get_full_name() if report.operator else '',
                "planned_qty": report.planned_qty,
                "start_time": report.start_time.strftime("%H:%M") if report.start_time else '',
                "end_time": report.end_time.strftime("%H:%M") if report.end_time else '',
                "billet_size": report.billet_size,
                "no_of_billet": report.no_of_billet,
                "weight": str(report.weight) if report.weight else '',
                "input_qty": str(report.input_qty) if report.input_qty else '',
                "wt_per_piece_output": str(report.wt_per_piece_output) if report.wt_per_piece_output else '',
                "no_of_pieces": report.no_of_pieces,
                "total_output": str(report.total_output) if report.total_output else '',
                "status": report.status,
                "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": report.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            return JsonResponse({
                "success": True,
                "report": report_data
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update production report"""
        try:
            report = get_object_or_404(OnlineProductionReport, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            if not data.get('date'):
                return JsonResponse({
                    "success": False,
                    "message": "Date is required."
                })
            
            if not data.get('date_of_production'):
                return JsonResponse({
                    "success": False,
                    "message": "Date of Production is required."
                })
            
            if not data.get('die_requisition'):
                return JsonResponse({
                    "success": False,
                    "message": "Die Requisition ID is required."
                })
            
            if not data.get('press'):
                return JsonResponse({
                    "success": False,
                    "message": "Press is required."
                })
            
            # Update fields
            report.date = data.get('date', report.date)
            report.date_of_production = data.get('date_of_production', report.date_of_production)
            report.die_requisition_id = data.get('die_requisition', report.die_requisition_id)
            report.die_no = data.get('die_no', report.die_no)
            report.section_no = data.get('section_no', report.section_no)
            report.section_name = data.get('section_name', report.section_name)
            report.wt_per_piece_general = data.get('wt_per_piece_general') or report.wt_per_piece_general
            report.no_of_cavity = data.get('no_of_cavity', report.no_of_cavity)
            report.cut_length = data.get('cut_length', report.cut_length)
            report.press_id = data.get('press', report.press_id)
            report.shift_id = data.get('shift') or report.shift_id
            report.operator_id = data.get('operator') or report.operator_id
            report.planned_qty = data.get('planned_qty') or report.planned_qty
            report.start_time = data.get('start_time') or report.start_time
            report.end_time = data.get('end_time') or report.end_time
            report.billet_size = data.get('billet_size', report.billet_size)
            report.no_of_billet = data.get('no_of_billet') or report.no_of_billet
            report.weight = data.get('weight') or report.weight
            report.input_qty = data.get('input_qty') or report.input_qty
            report.wt_per_piece_output = data.get('wt_per_piece_output') or report.wt_per_piece_output
            report.no_of_pieces = data.get('no_of_pieces') or report.no_of_pieces
            report.status = data.get('status', report.status)
            report.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Online Production Report updated successfully!",
                "total_output": str(report.total_output) if report.total_output else ''
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete production report"""
        try:
            report = get_object_or_404(OnlineProductionReport, id=pk)
            production_id = report.production_id
            report.delete()
            return JsonResponse({
                "success": True,
                "message": f"Online Production Report {production_id} deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class OnlineProductionReportDeleteView(View):
    """Delete production report view"""
    
    def post(self, request, pk):
        try:
            report = get_object_or_404(OnlineProductionReport, id=pk)
            production_id = report.production_id
            report.delete()
            return JsonResponse({
                "success": True,
                "message": f"Online Production Report {production_id} deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
        

# ─────────────────────────────────────────────────────────────────────────────
# Views for Daily Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class DailyProductionReportListView(View):
    """Render the daily production report list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            reports = DailyProductionReport.objects.filter(
                Q(report_id__icontains=search_query) |
                Q(die_no__icontains=search_query) |
                Q(section_no__icontains=search_query)
            ).select_related(
                'online_production_report'
            ).order_by("-created_at")
        else:
            reports = DailyProductionReport.objects.all().select_related(
                'online_production_report'
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
                    'report_id': report.report_id,
                    'date': report.date.strftime("%Y-%m-%d") if report.date else '',
                    'die_no': report.die_no,
                    'section_no': report.section_no,
                    'section_name': report.section_name,
                    'input_qty': str(report.input_qty) if report.input_qty else '',
                    'output': str(report.output) if report.output else '',
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
            "Production/Daily_Production_Report_List/daily_production_report_list.html",
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


class DailyProductionReportFormView(View):
    """Render the daily production report form page"""
    
    def get(self, request):
        # Generate preview of next Report ID
        next_report_id = DailyProductionReport.generate_report_id()
        
        # Get ALL online production reports (removed status filter)
        online_reports = OnlineProductionReport.objects.all().order_by('-created_at')

        return render(
            request,
            "Production/Daily_Production_Report/daily_production_report.html",
            {
                "edit_mode": False,
                "next_report_id": next_report_id,
                "online_reports": online_reports,
            },
        )


class DailyProductionReportEditView(View):
    """Render the daily production report edit form page"""
    
    def get(self, request, pk):
        try:
            report = DailyProductionReport.objects.select_related(
                'online_production_report'
            ).get(id=pk)
        except DailyProductionReport.DoesNotExist:
            return redirect("daily_production_report_list")
        
        # Get ALL online production reports (removed status filter)
        online_reports = OnlineProductionReport.objects.all().order_by('-created_at')
        
        return render(
            request,
            "Production/Daily_Production_Report/daily_production_report.html",
            {
                "report": report,
                "edit_mode": True,
                "online_reports": online_reports,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class DailyProductionReportAPI(View):
    """API for CRUD on Daily Production Report"""
    
    def get(self, request):
        """Get all reports, next Report ID, or online production report details"""
        
        # Check if requesting next Report ID
        if request.GET.get('action') == 'get_next_id':
            next_id = DailyProductionReport.generate_report_id()
            return JsonResponse({
                'success': True,
                'next_report_id': next_id
            })
        
        # Get online production report details
        if request.GET.get('action') == 'get_online_report_details':
            online_report_id = request.GET.get('online_report_id')
            
            try:
                online_report = OnlineProductionReport.objects.select_related(
                    'die_requisition'
                ).get(id=online_report_id)
                
                # Get NOP BP from production plan
                nop_bp_value = None
                if online_report.die_requisition and online_report.date_of_production:
                    production_plan = ProductionPlan.objects.filter(
                        die_requisition=online_report.die_requisition,
                        date_of_production=online_report.date_of_production
                    ).first()
                    
                    if production_plan and production_plan.no_of_billet:
                        nop_bp_value = production_plan.no_of_billet
                
                return JsonResponse({
                    'success': True,
                    'details': {
                        'die_no': online_report.die_no,
                        'section_no': online_report.section_no,
                        'section_name': online_report.section_name,
                        'cavity': online_report.no_of_cavity,
                        'start_time': online_report.start_time.strftime("%H:%M") if online_report.start_time else '',
                        'end_time': online_report.end_time.strftime("%H:%M") if online_report.end_time else '',
                        'billet_size': online_report.billet_size,
                        'no_of_billet': online_report.no_of_billet if online_report.no_of_billet else '',
                        'input_qty': str(online_report.input_qty) if online_report.input_qty else '',
                        'cut_length': online_report.cut_length,
                        'wt_per_piece': str(online_report.wt_per_piece_output) if online_report.wt_per_piece_output else '',
                        'no_of_ok_pcs': online_report.no_of_pieces if online_report.no_of_pieces else '',
                        'output': str(online_report.total_output) if online_report.total_output else '',
                        'nop_bp': nop_bp_value if nop_bp_value else '',
                        'nop_ba': online_report.no_of_billet if online_report.no_of_billet else ''
                    }
                })
            except OnlineProductionReport.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Online Production Report not found'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
        
        # Otherwise return all reports
        reports = DailyProductionReport.objects.all().select_related(
            'online_production_report'
        ).order_by("-created_at")
        
        formatted = []
        for report in reports:
            formatted.append({
                "id": report.id,
                "report_id": report.report_id,
                "date": report.date.strftime("%Y-%m-%d") if report.date else '',
                "die_no": report.die_no,
                "section_no": report.section_no,
                "section_name": report.section_name,
                "cavity": report.cavity,
                "start_time": report.start_time.strftime("%H:%M") if report.start_time else '',
                "end_time": report.end_time.strftime("%H:%M") if report.end_time else '',
                "billet_size": report.billet_size,
                "no_of_billet": report.no_of_billet,
                "input_qty": str(report.input_qty) if report.input_qty else '',
                "cut_length": report.cut_length,
                "wt_per_piece": str(report.wt_per_piece) if report.wt_per_piece else '',
                "no_of_ok_pcs": report.no_of_ok_pcs,
                "output": str(report.output) if report.output else '',
                "recovery": str(report.recovery) if report.recovery else '',
                "nop_bp": report.nop_bp,
                "nop_ba": report.nop_ba,
                "nrt": str(report.nrt) if report.nrt else '',
                "created_at": report.created_at.strftime("%Y-%m-%d"),
            })
        return JsonResponse({"success": True, "reports": formatted})
    
    def post(self, request):
        """Create a new daily production report"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if not data.get('date'):
                return JsonResponse({
                    "success": False,
                    "message": "Date is required."
                })
            
            if not data.get('online_production_report'):
                return JsonResponse({
                    "success": False,
                    "message": "Die No (Online Production Report) is required."
                })
            
            # Parse time fields if they are strings
            from datetime import datetime, time
            
            start_time_value = data.get('start_time')
            end_time_value = data.get('end_time')
            
            # Convert string time to time object if needed
            if start_time_value and isinstance(start_time_value, str):
                try:
                    start_time_value = datetime.strptime(start_time_value, '%H:%M').time()
                except (ValueError, TypeError):
                    start_time_value = None
            
            if end_time_value and isinstance(end_time_value, str):
                try:
                    end_time_value = datetime.strptime(end_time_value, '%H:%M').time()
                except (ValueError, TypeError):
                    end_time_value = None
            
            # Create daily production report
            report = DailyProductionReport.objects.create(
                date=data.get('date'),
                online_production_report_id=data.get('online_production_report'),
                die_no=data.get('die_no', ''),
                section_no=data.get('section_no', ''),
                section_name=data.get('section_name', ''),
                cavity=data.get('cavity', ''),
                start_time=start_time_value,
                end_time=end_time_value,
                billet_size=data.get('billet_size', ''),
                no_of_billet=data.get('no_of_billet') or None,
                input_qty=data.get('input_qty') or None,
                cut_length=data.get('cut_length', ''),
                wt_per_piece=data.get('wt_per_piece') or None,
                no_of_ok_pcs=data.get('no_of_ok_pcs') or None,
                output=data.get('output') or None,
                nop_bp=data.get('nop_bp') or None,
                nop_ba=data.get('nop_ba') or None
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Daily Production Report created successfully!",
                    "report": {
                        "id": report.id,
                        "report_id": report.report_id,
                        "recovery": str(report.recovery) if report.recovery else '',
                        "nrt": str(report.nrt) if report.nrt else ''
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class DailyProductionReportDetailAPI(View):
    """API for get, edit & delete Daily Production Report"""
    
    def get(self, request, pk):
        """Get a single daily production report"""
        try:
            report = get_object_or_404(DailyProductionReport.objects.select_related(
                'online_production_report'
            ), id=pk)
            
            report_data = {
                "id": report.id,
                "report_id": report.report_id,
                "date": report.date.strftime("%Y-%m-%d") if report.date else '',
                "online_production_report_id": report.online_production_report.id if report.online_production_report else None,
                "die_no": report.die_no,
                "section_no": report.section_no,
                "section_name": report.section_name,
                "cavity": report.cavity,
                "start_time": report.start_time.strftime("%H:%M") if report.start_time else '',
                "end_time": report.end_time.strftime("%H:%M") if report.end_time else '',
                "billet_size": report.billet_size,
                "no_of_billet": report.no_of_billet,
                "input_qty": str(report.input_qty) if report.input_qty else '',
                "cut_length": report.cut_length,
                "wt_per_piece": str(report.wt_per_piece) if report.wt_per_piece else '',
                "no_of_ok_pcs": report.no_of_ok_pcs,
                "output": str(report.output) if report.output else '',
                "recovery": str(report.recovery) if report.recovery else '',
                "nop_bp": report.nop_bp,
                "nop_ba": report.nop_ba,
                "nrt": str(report.nrt) if report.nrt else '',
                "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": report.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            return JsonResponse({
                "success": True,
                "report": report_data
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update daily production report"""
        try:
            report = get_object_or_404(DailyProductionReport, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            if not data.get('date'):
                return JsonResponse({
                    "success": False,
                    "message": "Date is required."
                })
            
            if not data.get('online_production_report'):
                return JsonResponse({
                    "success": False,
                    "message": "Die No (Online Production Report) is required."
                })
            
            # Parse time fields if they are strings
            from datetime import datetime, time
            
            start_time_value = data.get('start_time')
            end_time_value = data.get('end_time')
            
            # Convert string time to time object if needed
            if start_time_value and isinstance(start_time_value, str):
                try:
                    start_time_value = datetime.strptime(start_time_value, '%H:%M').time()
                except (ValueError, TypeError):
                    start_time_value = None
            elif not start_time_value:
                start_time_value = report.start_time
            
            if end_time_value and isinstance(end_time_value, str):
                try:
                    end_time_value = datetime.strptime(end_time_value, '%H:%M').time()
                except (ValueError, TypeError):
                    end_time_value = None
            elif not end_time_value:
                end_time_value = report.end_time
            
            # Update fields
            report.date = data.get('date', report.date)
            report.online_production_report_id = data.get('online_production_report', report.online_production_report_id)
            report.die_no = data.get('die_no', report.die_no)
            report.section_no = data.get('section_no', report.section_no)
            report.section_name = data.get('section_name', report.section_name)
            report.cavity = data.get('cavity', report.cavity)
            report.start_time = start_time_value
            report.end_time = end_time_value
            report.billet_size = data.get('billet_size', report.billet_size)
            report.no_of_billet = data.get('no_of_billet') or report.no_of_billet
            report.input_qty = data.get('input_qty') or report.input_qty
            report.cut_length = data.get('cut_length', report.cut_length)
            report.wt_per_piece = data.get('wt_per_piece') or report.wt_per_piece
            report.no_of_ok_pcs = data.get('no_of_ok_pcs') or report.no_of_ok_pcs
            report.output = data.get('output') or report.output
            report.nop_bp = data.get('nop_bp') or report.nop_bp
            report.nop_ba = data.get('nop_ba') or report.nop_ba
            report.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Daily Production Report updated successfully!",
                "recovery": str(report.recovery) if report.recovery else '',
                "nrt": str(report.nrt) if report.nrt else ''
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete daily production report"""
        try:
            report = get_object_or_404(DailyProductionReport, id=pk)
            report_id = report.report_id
            report.delete()
            return JsonResponse({
                "success": True,
                "message": f"Daily Production Report {report_id} deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class DailyProductionReportDeleteView(View):
    """Delete daily production report view"""
    
    def post(self, request, pk):
        try:
            report = get_object_or_404(DailyProductionReport, id=pk)
            report_id = report.report_id
            report.delete()
            return JsonResponse({
                "success": True,
                "message": f"Daily Production Report {report_id} deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})















# class TotalProductionReportView(View):
#     """Render and filter Total Production Report"""
    
#     def get(self, request):
#         # Get unique order numbers from OnlineProductionReport
#         order_choices = OnlineProductionReport.objects.values_list(
#             'production_id', 'production_id'
#         ).distinct()
        
#         # Get unique press names from Raw_data
#         press_choices = Raw_data.objects.values_list(
#             'sensor_name', 'sensor_name'
#         ).distinct()
        
#         form = ProductionFilterForm()
#         form.fields['order_no'].choices = [('', 'Select Order No')] + list(order_choices)
#         form.fields['press'].choices = [('', 'Select Press')] + list(press_choices)
        
#         return render(request, "Production/Total_Production_Report/total_production_report.html", {"form": form})
    
#     def post(self, request):
#         try:
#             order_no = request.POST.get("order_no")
#             press = request.POST.get("press")
            
#             # Get the OnlineProductionReport to find die_no
#             production_order = OnlineProductionReport.objects.filter(
#                 production_id=order_no
#             ).first()
            
#             if not production_order:
#                 return JsonResponse({
#                     "success": False,
#                     "message": "Order not found"
#                 })
            
#             # Get matching raw data
#             raw_data_entries = Raw_data.objects.filter(
#                 sensor_name=press,
#                 die_number=production_order.die_no
#             ).order_by("datetime")
            
#             if not raw_data_entries.exists():
#                 return JsonResponse({
#                     "success": False,
#                     "message": "No records found for the selected filters."
#                 })
            
#             # Get die information to retrieve die_name
#             die = Die.objects.filter(die_no=production_order.die_no).first()
#             die_name = die.die_name if die and die.die_name else "N/A"
            
#             # Calculate total length
#             total_length = sum(entry.length for entry in raw_data_entries)
            
#             # Prepare data for response
#             data = [
#                 {
#                     "s_no": i + 1,
#                     "date": entry.datetime.date().strftime("%Y-%m-%d"),
#                     "time": entry.datetime.time().strftime("%H:%M:%S"),
#                     "press": entry.sensor_name,
#                     "die_name": die_name,
#                     "order_no": production_order.production_id,
#                     "length": float(entry.length),
#                 }
#                 for i, entry in enumerate(raw_data_entries)
#             ]
            
#             return JsonResponse({
#                 "success": True,
#                 "records": data,
#                 "total_records": len(data),
#                 "total_length": float(total_length),
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 "success": False, 
#                 "message": str(e)
#             })


# def populate_production_reports():
#     """Populate ProductionReport from Raw_data and OnlineProductionReport"""
#     from .models import Raw_data, OnlineProductionReport, ProductionReport
    
#     ProductionReport.objects.all().delete()  # Clear old data
    
#     all_raw_data = Raw_data.objects.all()
#     created_count = 0
    
#     for raw_entry in all_raw_data:
#         production_order = OnlineProductionReport.objects.filter(
#             die_no=raw_entry.die_number
#         ).first()
        
#         if production_order:
#             ProductionReport.objects.create(
#                 date=raw_entry.datetime.date(),
#                 time=raw_entry.datetime.time(),
#                 press=raw_entry.sensor_name,
#                 die_no=raw_entry.die_number,
#                 order_no=production_order.production_id,
#                 length=raw_entry.length
#             )
#             created_count += 1
    
#     return created_count