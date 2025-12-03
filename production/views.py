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
from .models import ProductionReport
from .forms import OnlineProductionReportForm
from .forms import ProductionFilterForm
from raw_data.models import Raw_data
from master.models import Die

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
                    'production_plan_id': report.production_plan_id.production_plan_id if report.production_plan_id else '',
                    'customer_name': report.customer_name,
                    'die_requisition_id': report.die_requisition_id,
                    'die_no': report.die_no,
                    'section_no': report.section_no,
                    'section_name': report.section_name,
                    'wt_per_piece': str(report.wt_per_piece) if report.wt_per_piece else '',
                    'press_no': report.press_no.name if report.press_no else '',
                    'date_of_production': report.date_of_production.strftime("%Y-%m-%d") if report.date_of_production else '',
                    'shift': report.shift.name if report.shift else '',
                    'operator': report.operator.get_full_name() if report.operator else '',
                    'planned_qty': report.planned_qty,
                    'start_time': report.start_time.strftime("%H:%M") if report.start_time else '',
                    'end_time': report.end_time.strftime("%H:%M") if report.end_time else '',
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
                plan = ProductionPlan.objects.select_related(
                    'die_requisition',
                    'press',
                    'shift',
                    'operator'
                ).get(id=plan_id)
                
                # Get die requisition ID
                die_requisition_id = ''
                if plan.die_requisition:
                    die_requisition_id = plan.die_requisition.die_requisition_id if hasattr(plan.die_requisition, 'die_requisition_id') else str(plan.die_requisition.id)
                
                return JsonResponse({
                    'success': True,
                    'production_plan': {
                        'customer_name': plan.customer_name,
                        'die_requisition_id': die_requisition_id,
                        'die_no': plan.die_no,
                        'section_no': plan.section_no,
                        'section_name': plan.section_name,
                        'wt_per_piece': str(plan.wt_per_piece) if plan.wt_per_piece else '',
                        'press': plan.press.id if plan.press else '',
                        'date_of_production': plan.date_of_production.strftime("%Y-%m-%d") if plan.date_of_production else '',
                        'shift': plan.shift.id if plan.shift else '',
                        'operator': plan.operator.id if plan.operator else '',
                        'planned_qty': plan.planned_qty if plan.planned_qty else ''
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
                "production_plan_id": report.production_plan_id.production_plan_id if report.production_plan_id else '',
                "customer_name": report.customer_name,
                "die_requisition_id": report.die_requisition_id,
                "die_no": report.die_no,
                "section_no": report.section_no,
                "section_name": report.section_name,
                "wt_per_piece": str(report.wt_per_piece) if report.wt_per_piece else '',
                "press_no": report.press_no.name if report.press_no else '',
                "date_of_production": report.date_of_production.strftime("%Y-%m-%d") if report.date_of_production else '',
                "shift": report.shift.name if report.shift else '',
                "operator": report.operator.get_full_name() if report.operator else '',
                "planned_qty": report.planned_qty,
                "start_time": report.start_time.strftime("%H:%M") if report.start_time else '',
                "end_time": report.end_time.strftime("%H:%M") if report.end_time else '',
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
                production_plan_id_id=data.get('production_plan_id') or None,
                customer_name=data.get('customer_name', ''),
                die_requisition_id=data.get('die_requisition_id', ''),
                die_no=data.get('die_no', ''),
                section_no=data.get('section_no', ''),
                section_name=data.get('section_name', ''),
                wt_per_piece=data.get('wt_per_piece') or None,
                press_no_id=data['press_no'],
                date_of_production=data.get('date_of_production') or None,
                shift_id=data.get('shift') or None,
                operator_id=data.get('operator') or None,
                planned_qty=data.get('planned_qty') or None,
                start_time=data.get('start_time') or None,
                end_time=data.get('end_time') or None,
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
            report.production_plan_id_id = data.get('production_plan_id') or report.production_plan_id_id
            report.customer_name = data.get('customer_name', report.customer_name)
            report.die_requisition_id = data.get('die_requisition_id', report.die_requisition_id)
            report.die_no = data.get('die_no', report.die_no)
            report.section_no = data.get('section_no', report.section_no)
            report.section_name = data.get('section_name', report.section_name)
            report.wt_per_piece = data.get('wt_per_piece') or report.wt_per_piece
            report.press_no_id = data.get('press_no', report.press_no_id)
            report.date_of_production = data.get('date_of_production') or report.date_of_production
            report.shift_id = data.get('shift') or report.shift_id
            report.operator_id = data.get('operator') or report.operator_id
            report.planned_qty = data.get('planned_qty') or report.planned_qty
            report.start_time = data.get('start_time') or report.start_time
            report.end_time = data.get('end_time') or report.end_time
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
        

# ─────────────────────────────────────────────────────────────────────────────
# Views for Total Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class TotalProductionReportView(View):
    """Render and filter Total Production Report"""
    
    def get(self, request):
        # Get unique order numbers from OnlineProductionReport
        order_choices = OnlineProductionReport.objects.values_list(
            'production_id', 'production_id'
        ).distinct()
        
        # Get unique press names from Raw_data
        press_choices = Raw_data.objects.values_list(
            'sensor_name', 'sensor_name'
        ).distinct()
        
        form = ProductionFilterForm()
        form.fields['order_no'].choices = [('', 'Select Order No')] + list(order_choices)
        form.fields['press'].choices = [('', 'Select Press')] + list(press_choices)
        
        return render(request, "Production/Total_Production_Report/total_production_report.html", {"form": form})
    
    def post(self, request):
        try:
            order_no = request.POST.get("order_no")
            press = request.POST.get("press")
            
            # Get the OnlineProductionReport to find die_no
            production_order = OnlineProductionReport.objects.filter(
                production_id=order_no
            ).first()
            
            if not production_order:
                return JsonResponse({
                    "success": False,
                    "message": "Order not found"
                })
            
            # Get matching raw data
            raw_data_entries = Raw_data.objects.filter(
                sensor_name=press,
                die_number=production_order.die_no
            ).order_by("datetime")
            
            if not raw_data_entries.exists():
                return JsonResponse({
                    "success": False,
                    "message": "No records found for the selected filters."
                })
            
            # Get die information to retrieve die_name
            die = Die.objects.filter(die_no=production_order.die_no).first()
            die_name = die.die_name if die and die.die_name else "N/A"
            
            # Calculate total length
            total_length = sum(entry.length for entry in raw_data_entries)
            
            # Prepare data for response
            data = [
                {
                    "s_no": i + 1,
                    "date": entry.datetime.date().strftime("%Y-%m-%d"),
                    "time": entry.datetime.time().strftime("%H:%M:%S"),
                    "press": entry.sensor_name,
                    "die_name": die_name,
                    "order_no": production_order.production_id,
                    "length": float(entry.length),
                }
                for i, entry in enumerate(raw_data_entries)
            ]
            
            return JsonResponse({
                "success": True,
                "records": data,
                "total_records": len(data),
                "total_length": float(total_length),
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False, 
                "message": str(e)
            })


def populate_production_reports():
    """Populate ProductionReport from Raw_data and OnlineProductionReport"""
    from .models import Raw_data, OnlineProductionReport, ProductionReport
    
    ProductionReport.objects.all().delete()  # Clear old data
    
    all_raw_data = Raw_data.objects.all()
    created_count = 0
    
    for raw_entry in all_raw_data:
        production_order = OnlineProductionReport.objects.filter(
            die_no=raw_entry.die_number
        ).first()
        
        if production_order:
            ProductionReport.objects.create(
                date=raw_entry.datetime.date(),
                time=raw_entry.datetime.time(),
                press=raw_entry.sensor_name,
                die_no=raw_entry.die_number,
                order_no=production_order.production_id,
                length=raw_entry.length
            )
            created_count += 1
    
    return created_count