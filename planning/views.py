from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


from .models import *
from .forms import *
from master.models import *
from order_management.models import *


# Create your views here.
# ─────────────────────────────────────────────────────────────────────────────
# Views for Die Requisition functionality
# ─────────────────────────────────────────────────────────────────────────────
class DieRequisitionListView(View):
    """Render the die requisition list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            requisitions = DieRequisition.objects.filter(
                die_requisition_id__icontains=search_query
            ).select_related(
                'customer_requisition_no', 'section_no', 'die_no'
            ).order_by("-created_at")
        else:
            requisitions = DieRequisition.objects.all().select_related(
                'customer_requisition_no', 'section_no', 'die_no'
            ).order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(requisitions, 10)
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
            requisitions_list = []
            for req in page_obj:
                requisitions_list.append({
                    'id': req.id,
                    'die_requisition_id': req.die_requisition_id,
                    'date': req.date.strftime("%Y-%m-%d"),
                    'customer_requisition_no': req.customer_requisition_no.requisition_no,
                    'section_no': req.section_no.section_no if req.section_no else '',
                    'die_no': req.die_no.die_no if req.die_no else '',
                    'wt_range': req.wt_range,
                    'cut_length': req.cut_length or '',
                })
            
            return JsonResponse(
                {
                    "requisitions": requisitions_list,
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
            "Planning/Die_Requisition_List/die_requisition_list.html",
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


class DieRequisitionFormView(View):
    """Render the die requisition form page"""
    
    def get(self, request):
        # Generate preview of next Die Requisition ID
        next_die_requisition_id = DieRequisition.generate_die_requisition_id()
        
        # Get dropdown data
        requisitions = Requisition.objects.all()
        dies = Die.objects.all()
        cut_lengths = DieRequisition.CUT_LENGTH_CHOICES

        return render(
            request,
            "Planning/Die_Requisition/die_requisition.html",
            {
                "edit_mode": False,
                "next_die_requisition_id": next_die_requisition_id,
                "requisitions": requisitions,
                "dies": dies,
                "cut_lengths": cut_lengths,
            },
        )


class DieRequisitionEditView(View):
    """Render the die requisition edit form page"""
    
    def get(self, request, pk):
        try:
            requisition = DieRequisition.objects.select_related(
                'customer_requisition_no', 'section_no', 'die_no'
            ).get(id=pk)
        except DieRequisition.DoesNotExist:
            return redirect("die_requisition_list")
        
        # Get dropdown data
        requisitions = Requisition.objects.all()
        dies = Die.objects.all()
        cut_lengths = DieRequisition.CUT_LENGTH_CHOICES
        
        return render(
            request,
            "Planning/Die_Requisition/die_requisition.html",
            {
                "requisition": requisition,
                "edit_mode": True,
                "requisitions": requisitions,
                "dies": dies,
                "cut_lengths": cut_lengths,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class DieRequisitionAPI(View):
    """API for CRUD on Die Requisition"""
    
    def get(self, request):
        """Get all requisitions or get next Die Requisition ID"""
        # Check if requesting next Die Requisition ID
        if request.GET.get('action') == 'get_next_id':
            next_id = DieRequisition.generate_die_requisition_id()
            return JsonResponse({
                'success': True,
                'next_die_requisition_id': next_id
            })
        
        # Get requisition orders for a specific requisition
        if request.GET.get('action') == 'get_requisition_orders':
            requisition_id = request.GET.get('requisition_id')
            try:
                orders = RequisitionOrder.objects.filter(
                    requisition_id=requisition_id
                ).select_related('section_no')
                
                orders_data = [{
                    'id': order.id,
                    'section_no_id': order.section_no.id,
                    'section_no': order.section_no.section_no,
                    'section_name': order.section_no.section_name,
                    'wt_range': order.wt_range
                } for order in orders]
                
                return JsonResponse({
                    'success': True,
                    'orders': orders_data
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
        
        # Get die details
        if request.GET.get('action') == 'get_die_details':
            die_id = request.GET.get('die_id')
            try:
                die = Die.objects.get(id=die_id)
                return JsonResponse({
                    'success': True,
                    'die': {
                        'die_name': die.die_name,
                        'req_weight': str(die.req_weight),
                        'no_of_cavity': die.no_of_cavity
                    }
                })
            except Die.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Die not found'
                })
        
        # Otherwise return all requisitions
        requisitions = DieRequisition.objects.all().select_related(
            'customer_requisition_no', 'section_no', 'die_no'
        ).order_by("-created_at")
        
        formatted = []
        for req in requisitions:
            formatted.append({
                "id": req.id,
                "die_requisition_id": req.die_requisition_id,
                "date": req.date.strftime("%Y-%m-%d"),
                "customer_requisition_no": req.customer_requisition_no.requisition_no,
                "section_no": req.section_no.section_no if req.section_no else '',
                "section_name": req.section_name,
                "wt_range": req.wt_range,
                "die_no": req.die_no.die_no if req.die_no else '',
                "die_name": req.die_name,
                "present_wt": str(req.present_wt),
                "no_of_cavity": req.no_of_cavity,
                "cut_length": req.cut_length or '',
                "created_at": req.created_at.strftime("%Y-%m-%d"),
            })
        return JsonResponse({"success": True, "requisitions": formatted})
    
    def post(self, request):
        """Create a new die requisition"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = [
                'customer_requisition_no', 'section_no', 'die_no', 'wt_range'
            ]
            
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        "success": False,
                        "message": f"{field.replace('_', ' ').title()} is required."
                    })
            
            # Use today's date if not provided
            requisition_date = data.get("date") or date.today().strftime("%Y-%m-%d")
            
            # Create die requisition
            requisition = DieRequisition.objects.create(
                date=requisition_date,
                customer_requisition_no_id=data['customer_requisition_no'],
                section_no_id=data['section_no'],
                section_name=data.get('section_name', ''),
                wt_range=data.get('wt_range', ''),
                die_no_id=data['die_no'],
                die_name=data.get('die_name', ''),
                present_wt=data.get('present_wt', 0),
                no_of_cavity=data.get('no_of_cavity', ''),
                cut_length=data.get('cut_length') or None
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Die Requisition created successfully!",
                    "requisition": {
                        "id": requisition.id,
                        "die_requisition_id": requisition.die_requisition_id,
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class DieRequisitionDetailAPI(View):
    """API for get, edit & delete Die Requisition"""
    
    def get(self, request, pk):
        """Get die requisition details"""
        try:
            requisition = get_object_or_404(DieRequisition, id=pk)
            
            return JsonResponse(
                {
                    "success": True,
                    "requisition": {
                        "id": requisition.id,
                        "die_requisition_id": requisition.die_requisition_id,
                        "date": requisition.date.strftime("%Y-%m-%d"),
                        "customer_requisition_no": requisition.customer_requisition_no.id,
                        "section_no": requisition.section_no.id if requisition.section_no else None,
                        "section_name": requisition.section_name,
                        "wt_range": requisition.wt_range,
                        "die_no": requisition.die_no.id if requisition.die_no else None,
                        "die_name": requisition.die_name,
                        "present_wt": str(requisition.present_wt),
                        "no_of_cavity": requisition.no_of_cavity,
                        "cut_length": requisition.cut_length or '',
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update die requisition"""
        try:
            requisition = get_object_or_404(DieRequisition, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = [
                'customer_requisition_no', 'section_no', 'die_no', 'wt_range'
            ]
            
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        "success": False,
                        "message": f"{field.replace('_', ' ').title()} is required."
                    })
            
            # Use existing date if not provided
            requisition_date = data.get("date") or requisition.date
            
            # Update fields
            requisition.date = requisition_date
            requisition.customer_requisition_no_id = data.get('customer_requisition_no', requisition.customer_requisition_no_id)
            requisition.section_no_id = data.get('section_no', requisition.section_no_id)
            requisition.section_name = data.get('section_name', requisition.section_name)
            requisition.wt_range = data.get('wt_range', requisition.wt_range)
            requisition.die_no_id = data.get('die_no', requisition.die_no_id)
            requisition.die_name = data.get('die_name', requisition.die_name)
            requisition.present_wt = data.get('present_wt', requisition.present_wt)
            requisition.no_of_cavity = data.get('no_of_cavity', requisition.no_of_cavity)
            requisition.cut_length = data.get('cut_length') or None
            requisition.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Die Requisition updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete die requisition"""
        try:
            requisition = get_object_or_404(DieRequisition, id=pk)
            requisition.delete()
            return JsonResponse({
                "success": True,
                "message": "Die Requisition deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class DieRequisitionDeleteView(View):
    """Delete die requisition view"""
    
    def post(self, request, pk):
        try:
            requisition = get_object_or_404(DieRequisition, id=pk)
            requisition.delete()
            return JsonResponse({"success": True, "message": "Die Requisition deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


# ==============================================================================================

# ─────────────────────────────────────────────────────────────────────────────
# Views for Production Planning functionality
# ─────────────────────────────────────────────────────────────────────────────
class ProductionPlanListView(View):
    """Render the production plan list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            plans = ProductionPlan.objects.filter(
                production_plan_id__icontains=search_query
            ).select_related(
                'cust_requisition_id', 'die_requisition', 'press', 
                'shift', 'operator'
            ).order_by("-created_at")
        else:
            plans = ProductionPlan.objects.all().select_related(
                'cust_requisition_id', 'die_requisition', 'press', 
                'shift', 'operator'
            ).order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(plans, 10)
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
            plans_list = []
            for plan in page_obj:
                plans_list.append({
                    'id': plan.id,
                    'production_plan_id': plan.production_plan_id,
                    'date': plan.date.strftime("%Y-%m-%d"),
                    'cust_requisition_id': plan.cust_requisition_id.requisition_id if plan.cust_requisition_id else '',
                    'customer_name': plan.customer_name,
                    'die_requisition_id': plan.die_requisition.die_requisition_id if plan.die_requisition else '',
                    'die_no': plan.die_no,
                    'section_no': plan.section_no,
                    'wt_per_piece': str(plan.wt_per_piece),
                    'press': plan.press.name if plan.press else '',
                    'date_of_production': plan.date_of_production.strftime("%Y-%m-%d") if plan.date_of_production else '',
                    'shift': plan.shift.name if plan.shift else '',
                    'operator': plan.operator.get_full_name() if plan.operator else '',
                    'planned_qty': plan.planned_qty,
                })
            
            return JsonResponse(
                {
                    "plans": plans_list,
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
            "Planning/Production_Plan_List/production_plan_list.html",
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


class ProductionPlanFormView(View):
    """Render the production plan form page"""
    
    def get(self, request):
        # Generate preview of next Production Plan ID
        next_production_plan_id = ProductionPlan.generate_production_plan_id()
        
        # Get dropdown data
        requisitions = Requisition.objects.all()
        die_requisitions = DieRequisition.objects.all()
        presses = CompanyPress.objects.all()
        shifts = CompanyShift.objects.all()
        staff_list = Staff.objects.all()

        return render(
            request,
            "Planning/Production_Plan/production_plan.html",
            {
                "edit_mode": False,
                "next_production_plan_id": next_production_plan_id,
                "requisitions": requisitions,
                "die_requisitions": die_requisitions,
                "presses": presses,
                "shifts": shifts,
                "staff_list": staff_list,
            },
        )


class ProductionPlanEditView(View):
    """Render the production plan edit form page"""
    
    def get(self, request, pk):
        try:
            plan = ProductionPlan.objects.select_related(
                'cust_requisition_id', 'die_requisition', 'press',
                'shift', 'operator'
            ).get(id=pk)
        except ProductionPlan.DoesNotExist:
            return redirect("production_plan_list")
        
        # Get dropdown data
        requisitions = Requisition.objects.all()
        die_requisitions = DieRequisition.objects.all()
        presses = CompanyPress.objects.all()
        shifts = CompanyShift.objects.all()
        staff_list = Staff.objects.all()
        
        return render(
            request,
            "Planning/Production_Plan/production_plan.html",
            {
                "plan": plan,
                "edit_mode": True,
                "requisitions": requisitions,
                "die_requisitions": die_requisitions,
                "presses": presses,
                "shifts": shifts,
                "staff_list": staff_list,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProductionPlanAPI(View):
    """API for CRUD on Production Plan"""
    
    def get(self, request):
        """Get all plans or get next Production Plan ID"""
        # Check if requesting next Production Plan ID
        if request.GET.get('action') == 'get_next_id':
            next_id = ProductionPlan.generate_production_plan_id()
            return JsonResponse({
                'success': True,
                'next_production_plan_id': next_id
            })
        
        # Get customer name
        if request.GET.get('action') == 'get_customer_name':
            requisition_id = request.GET.get('requisition_id')
            try:
                requisition = Requisition.objects.select_related('customer').get(id=requisition_id)
                return JsonResponse({
                    'success': True,
                    'customer_name': requisition.customer.name
                })
            except Requisition.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Requisition not found'
                })
        
        # Get die requisition details including no_of_cavity
        if request.GET.get('action') == 'get_die_requisition_details':
            die_req_id = request.GET.get('die_requisition_id')
            try:
                die_req = DieRequisition.objects.select_related('die_no', 'section_no').get(id=die_req_id)
                return JsonResponse({
                    'success': True,
                    'die_requisition': {
                        'die_no': die_req.die_no.die_no if die_req.die_no else '',
                        'section_no': die_req.section_no.section_no if die_req.section_no else '',
                        'section_name': die_req.section_name,
                        'present_wt': str(die_req.present_wt),
                        'no_of_cavity': die_req.die_no.no_of_cavity if die_req.die_no else ''
                    }
                })
            except DieRequisition.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Die Requisition not found'
                })
        
        # Get cut length options for selected requisition
        if request.GET.get('action') == 'get_cut_length_options':
            requisition_id = request.GET.get('requisition_id')
            try:
                from order_management.models import RequisitionOrder
                cut_lengths = RequisitionOrder.objects.filter(
                    requisition_id=requisition_id
                ).values_list('cut_length', flat=True).distinct()
                return JsonResponse({
                    'success': True,
                    'cut_lengths': list(cut_lengths)
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })

        # Otherwise return all plans
        plans = ProductionPlan.objects.all().select_related(
            'cust_requisition_id', 'die_requisition', 'press', 
            'shift', 'operator'
        ).order_by("-created_at")
        
        formatted = []
        for plan in plans:
            formatted.append({
                "id": plan.id,
                "production_plan_id": plan.production_plan_id,
                "date": plan.date.strftime("%Y-%m-%d"),
                "cust_requisition_id": plan.cust_requisition_id.requisition_id if plan.cust_requisition_id else '',
                "customer_name": plan.customer_name,
                "die_requisition": plan.die_requisition.die_requisition_id if plan.die_requisition else '',
                "die_no": plan.die_no,
                "section_no": plan.section_no,
                "section_name": plan.section_name,
                "wt_per_piece": str(plan.wt_per_piece),
                "press": plan.press.name if plan.press else '',
                "date_of_production": plan.date_of_production.strftime("%Y-%m-%d") if plan.date_of_production else '',
                "shift": plan.shift.name if plan.shift else '',
                "operator": plan.operator.get_full_name() if plan.operator else '',
                "planned_qty": plan.planned_qty,
                "created_at": plan.created_at.strftime("%Y-%m-%d"),
            })
        return JsonResponse({"success": True, "plans": formatted})
    
    def post(self, request):
        """Create a new production plan"""
        try:
            data = json.loads(request.body)
            
            # Use today's date if not provided
            if not data.get('date'):
                data['date'] = timezone.now().date().isoformat()

            plan = ProductionPlan.objects.create(
                date=data['date'],
                cust_requisition_id_id=data.get('cust_requisition_id') or None,
                customer_name=data.get('customer_name', ''),
                die_requisition_id=data.get('die_requisition') or None,
                die_no=data.get('die_no', ''),
                section_no=data.get('section_no', ''),
                section_name=data.get('section_name', ''),
                wt_per_piece=data.get('wt_per_piece', 0),
                no_of_cavity=data.get('no_of_cavity', ''),
                cut_length=data.get('cut_length', ''),
                press_id=data.get('press') or None,
                date_of_production=data.get('date_of_production') or None,
                shift_id=data.get('shift') or None,
                operator_id=data.get('operator') or None,
                planned_qty=data.get('planned_qty') or None,
                billet_size=data.get('billet_size', ''),
                no_of_billet=data.get('no_of_billet') or None,
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Production Plan created successfully!",
                    "plan": {
                        "id": plan.id,
                        "production_plan_id": plan.production_plan_id,
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class ProductionPlanDetailAPI(View):
    """API for get, edit & delete Production Plan"""
    
    def get(self, request, pk):
        """Get production plan details"""
        try:
            plan = get_object_or_404(ProductionPlan, id=pk)
            
            return JsonResponse(
                {
                    "success": True,
                    "plan": {
                        "id": plan.id,
                        "production_plan_id": plan.production_plan_id,
                        "date": plan.date.strftime("%Y-%m-%d"),
                        "cust_requisition_id": plan.cust_requisition_id.id if plan.cust_requisition_id else None,
                        "customer_name": plan.customer_name,
                        "die_requisition": plan.die_requisition.id if plan.die_requisition else None,
                        "die_no": plan.die_no,
                        "section_no": plan.section_no,
                        "section_name": plan.section_name,
                        "wt_per_piece": str(plan.wt_per_piece),
                        "no_of_cavity": plan.no_of_cavity,
                        "cut_length": plan.cut_length,
                        "press": plan.press.id if plan.press else None,
                        "date_of_production": plan.date_of_production.strftime("%Y-%m-%d") if plan.date_of_production else '',
                        "shift": plan.shift.id if plan.shift else None,
                        "operator": plan.operator.id if plan.operator else None,
                        "planned_qty": plan.planned_qty,
                        "billet_size": plan.billet_size,
                        "no_of_billet": plan.no_of_billet,
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update production plan"""
        try:
            plan = get_object_or_404(ProductionPlan, id=pk)
            data = json.loads(request.body)
            
            # Update fields
            plan.date = data.get('date', plan.date)
            plan.cust_requisition_id_id = data.get('cust_requisition_id') or None
            plan.customer_name = data.get('customer_name', plan.customer_name)
            plan.die_requisition_id = data.get('die_requisition') or None
            plan.die_no = data.get('die_no', plan.die_no)
            plan.section_no = data.get('section_no', plan.section_no)
            plan.section_name = data.get('section_name', plan.section_name)
            plan.wt_per_piece = data.get('wt_per_piece', plan.wt_per_piece)
            plan.no_of_cavity = data.get('no_of_cavity', plan.no_of_cavity)
            plan.cut_length = data.get('cut_length', plan.cut_length)
            plan.press_id = data.get('press') or None
            plan.date_of_production = data.get('date_of_production') or None
            plan.shift_id = data.get('shift') or None
            plan.operator_id = data.get('operator') or None
            plan.planned_qty = data.get('planned_qty') or None
            plan.billet_size = data.get('billet_size', plan.billet_size)
            plan.no_of_billet = data.get('no_of_billet') or None

            plan.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Production Plan updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete production plan"""
        try:
            plan = get_object_or_404(ProductionPlan, id=pk)
            plan.delete()
            return JsonResponse({
                "success": True,
                "message": "Production Plan deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class ProductionPlanDeleteView(View):
    """Delete production plan view"""
    
    def post(self, request, pk):
        try:
            plan = get_object_or_404(ProductionPlan, id=pk)
            plan.delete()
            return JsonResponse({"success": True, "message": "Production Plan deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})