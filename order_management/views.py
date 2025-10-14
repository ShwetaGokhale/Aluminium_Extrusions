# import necessary modules and decorators
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, QueryDict
from django.views import View
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.forms.models import model_to_dict

from .models import *
from .forms import *


# Create your views here.
# ─────────────────────────────────────────────────────────────────────────────
# Views for Customer Requisition functionality
# ─────────────────────────────────────────────────────────────────────────────
class RequisitionListView(View):
    """Render the requisition list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            requisitions = Requisition.objects.filter(
                models.Q(requisition_no__icontains=search_query) |
                models.Q(customer__name__icontains=search_query)
            ).select_related('customer', 'sales_manager').order_by("-created_at")
        else:
            requisitions = Requisition.objects.select_related(
                'customer', 'sales_manager'
            ).all().order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(requisitions, 10)  # 10 per page
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
            requisition_list = []
            for req in page_obj:
                req_dict = model_to_dict(req)
                req_dict['customer_name'] = req.customer.name
                req_dict['orders'] = list(
                    req.orders.values(
                        'section_no__section_no',
                        'wt_range',
                        'cut_length',
                        'qty_in_no'
                    )
                )
                requisition_list.append(req_dict)
            
            return JsonResponse(
                {
                    "requisitions": requisition_list,
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
            "Order_Management/Customer_Requisition_List/customer_requisition_list.html",
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


class RequisitionFormView(View):
    """Render the requisition form page"""
    
    def get(self, request):
        # Generate preview of next Requisition ID
        next_requisition_id = Requisition.generate_requisition_id()
        
        # Convert QuerySets to lists of dictionaries
        customers = list(Customer.objects.values("id", "name", "contact_no", "address"))
        staff = list(Staff.objects.values("id", "first_name", "last_name"))
        sections = list(Section.objects.values("id", "section_no", "section_name"))
        
        return render(
            request,
            "Order_Management/Customer_Requisition/customer_requisition.html",
            {
                "edit_mode": False,
                "next_requisition_id": next_requisition_id,
                "customers": customers,
                "staff": staff,
                "sections": sections,
            },
        )


class RequisitionEditView(View):
    """Render the requisition edit form page"""
    
    def get(self, request, pk):
        try:
            requisition = Requisition.objects.select_related(
                'customer', 'sales_manager'
            ).get(id=pk)
        except Requisition.DoesNotExist:
            return redirect("requisition_list")
        
        # Convert QuerySets to lists of dictionaries (like in RequisitionFormView)
        customers = list(Customer.objects.values("id", "name", "contact_no", "address"))
        staff = list(Staff.objects.values("id", "first_name", "last_name"))
        sections = list(Section.objects.values("id", "section_no", "section_name"))
        
        # Get orders and convert to list of dictionaries
        orders = list(
            RequisitionOrder.objects.filter(requisition=requisition)
            .select_related('section_no')
            .values(
                'id',
                'section_no__id',
                'section_no__section_no',
                'section_no__section_name',
                'wt_range',
                'cut_length',
                'qty_in_no'
            )
        )
        
        return render(
            request,
            "Order_Management/Customer_Requisition/customer_requisition.html",
            {
                "requisition": requisition,
                "edit_mode": True,
                "customers": customers,
                "staff": staff,
                "sections": sections,
                "orders": orders,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class RequisitionAPI(View):
    """API for CRUD on Requisition"""
    
    def get(self, request):
        """Get all requisitions or get next Requisition ID"""
        # Check if requesting next Requisition ID
        if request.GET.get('action') == 'get_next_id':
            next_requisition_id = Requisition.generate_requisition_id()
            return JsonResponse({
                'success': True,
                'next_requisition_id': next_requisition_id
            })
        
        # Get customers for dropdown
        if request.GET.get('action') == 'get_customers':
            customers = Customer.objects.all()
            customer_list = [
                {
                    'id': c.id,
                    'name': c.name,
                    'contact_no': c.contact_no,
                    'address': c.address
                }
                for c in customers
            ]
            return JsonResponse({
                'success': True,
                'customers': customer_list
            })
        
        # Get staff for dropdown
        if request.GET.get('action') == 'get_staff':
            staff = Staff.objects.all()
            staff_list = [
                {
                    'id': s.id,
                    'name': f"{s.first_name} {s.last_name}"
                }
                for s in staff
            ]
            return JsonResponse({
                'success': True,
                'staff': staff_list
            })
        
        # Get sections for dropdown
        if request.GET.get('action') == 'get_sections':
            sections = Section.objects.all()
            section_list = [
                {
                    'id': s.id,
                    'section_no': s.section_no,
                    'section_name': s.section_name
                }
                for s in sections
            ]
            return JsonResponse({
                'success': True,
                'sections': section_list
            })
        
        # Otherwise return all requisitions
        requisitions = Requisition.objects.select_related(
            'customer', 'sales_manager'
        ).all().order_by("-created_at")
        
        formatted = []
        for req in requisitions:
            req_data = {
                "id": req.id,
                "requisition_id": req.requisition_id,
                "date": req.date.strftime("%Y-%m-%d"),
                "requisition_no": req.requisition_no,
                "customer": req.customer.id,
                "customer_name": req.customer.name,
                "contact_no": req.contact_no,
                "address": req.address,
                "sales_manager": req.sales_manager.id if req.sales_manager else None,
                "sales_manager_name": f"{req.sales_manager.first_name} {req.sales_manager.last_name}" if req.sales_manager else "",
                "expiry_date": req.expiry_date.strftime("%Y-%m-%d") if req.expiry_date else "",
                "dispatch_date": req.dispatch_date.strftime("%Y-%m-%d") if req.dispatch_date else "",
                "created_at": req.created_at.strftime("%Y-%m-%d"),
            }
            formatted.append(req_data)
        
        return JsonResponse({"success": True, "requisitions": formatted})
    
    def post(self, request):
        """Create a new requisition"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            requisition_no = data.get("requisition_no", "").strip()
            customer_id = data.get("customer")
            contact_no = data.get("contact_no", "").strip()
            address = data.get("address", "").strip()
            sales_manager_id = data.get("sales_manager")
            
            if not all([date, requisition_no, customer_id, sales_manager_id]):
                return JsonResponse({
                    "success": False,
                    "message": "Date, Requisition No, Customer, and Sales Manager are required."
                })
            
            # Check if requisition_no already exists
            if Requisition.objects.filter(requisition_no=requisition_no).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Requisition No already exists."
                })
            
            # Get customer and sales manager
            try:
                customer = Customer.objects.get(id=customer_id)
                sales_manager = Staff.objects.get(id=sales_manager_id)
            except (Customer.DoesNotExist, Staff.DoesNotExist):
                return JsonResponse({
                    "success": False,
                    "message": "Invalid customer or sales manager."
                })
            
            # Create requisition (requisition_id will be auto-generated)
            requisition = Requisition.objects.create(
                date=date,
                requisition_no=requisition_no,
                customer=customer,
                contact_no=contact_no,
                address=address,
                sales_manager=sales_manager,
                expiry_date=data.get("expiry_date") or None,
                dispatch_date=data.get("dispatch_date") or None
            )
            
            # Create orders
            orders = data.get("orders", [])
            for order_data in orders:
                section_id = order_data.get("section_no")
                if section_id:
                    try:
                        section = Section.objects.get(id=section_id)
                        RequisitionOrder.objects.create(
                            requisition=requisition,
                            section_no=section,
                            wt_range=order_data.get("wt_range", ""),
                            cut_length=order_data.get("cut_length", ""),
                            qty_in_no=int(order_data.get("qty_in_no", 0))
                        )
                    except Section.DoesNotExist:
                        pass
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Requisition created successfully!",
                    "requisition": {
                        "id": requisition.id,
                        "requisition_id": requisition.requisition_id,
                        "requisition_no": requisition.requisition_no,
                        "created_at": requisition.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class RequisitionDetailAPI(View):
    """API for get, edit & delete Requisition"""
    
    def get(self, request, pk):
        """Get requisition details"""
        try:
            requisition = get_object_or_404(Requisition, id=pk)
            orders = RequisitionOrder.objects.filter(requisition=requisition)
            
            orders_data = [
                {
                    "id": order.id,
                    "section_no": order.section_no.id,
                    "section_no_name": order.section_no.section_no,
                    "section_name": order.section_no.section_name,
                    "wt_range": order.wt_range,
                    "cut_length": order.cut_length,
                    "qty_in_no": order.qty_in_no
                }
                for order in orders
            ]
            
            return JsonResponse(
                {
                    "success": True,
                    "requisition": {
                        "id": requisition.id,
                        "requisition_id": requisition.requisition_id,
                        "date": requisition.date.strftime("%Y-%m-%d"),
                        "requisition_no": requisition.requisition_no,
                        "customer": requisition.customer.id,
                        "contact_no": requisition.contact_no,
                        "address": requisition.address,
                        "sales_manager": requisition.sales_manager.id if requisition.sales_manager else None,
                        "expiry_date": requisition.expiry_date.strftime("%Y-%m-%d") if requisition.expiry_date else "",
                        "dispatch_date": requisition.dispatch_date.strftime("%Y-%m-%d") if requisition.dispatch_date else "",
                        "orders": orders_data
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update requisition"""
        try:
            requisition = get_object_or_404(Requisition, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            requisition_no = data.get("requisition_no", "").strip()
            customer_id = data.get("customer")
            contact_no = data.get("contact_no", "").strip()
            address = data.get("address", "").strip()
            sales_manager_id = data.get("sales_manager")
            
            if not all([date, requisition_no, customer_id, sales_manager_id]):
                return JsonResponse({
                    "success": False,
                    "message": "Date, Requisition No, Customer, and Sales Manager are required."
                })
            
            # Check if requisition_no already exists (excluding current requisition)
            if Requisition.objects.filter(requisition_no=requisition_no).exclude(id=pk).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Requisition No already exists."
                })
            
            # Get customer and sales manager
            try:
                customer = Customer.objects.get(id=customer_id)
                sales_manager = Staff.objects.get(id=sales_manager_id)
            except (Customer.DoesNotExist, Staff.DoesNotExist):
                return JsonResponse({
                    "success": False,
                    "message": "Invalid customer or sales manager."
                })
            
            # Update requisition (requisition_id remains unchanged)
            requisition.date = date
            requisition.requisition_no = requisition_no
            requisition.customer = customer
            requisition.contact_no = contact_no
            requisition.address = address
            requisition.sales_manager = sales_manager
            requisition.expiry_date = data.get("expiry_date") or None
            requisition.dispatch_date = data.get("dispatch_date") or None
            requisition.save()
            
            # Handle orders (update/create/delete)
            incoming_orders = data.get("orders", [])
            kept_order_ids = []
            
            for order_data in incoming_orders:
                order_id = order_data.get("id")
                section_id = order_data.get("section_no")
                
                if section_id:
                    try:
                        section = Section.objects.get(id=section_id)
                        
                        if order_id:  # Update existing
                            try:
                                order = RequisitionOrder.objects.get(id=order_id, requisition=requisition)
                                order.section_no = section
                                order.wt_range = order_data.get("wt_range", "")
                                order.cut_length = order_data.get("cut_length", "")
                                order.qty_in_no = int(order_data.get("qty_in_no", 0))
                                order.save()
                                kept_order_ids.append(order.id)
                            except RequisitionOrder.DoesNotExist:
                                pass
                        else:  # Create new
                            new_order = RequisitionOrder.objects.create(
                                requisition=requisition,
                                section_no=section,
                                wt_range=order_data.get("wt_range", ""),
                                cut_length=order_data.get("cut_length", ""),
                                qty_in_no=int(order_data.get("qty_in_no", 0))
                            )
                            kept_order_ids.append(new_order.id)
                    except Section.DoesNotExist:
                        pass
            
            # Delete removed orders
            RequisitionOrder.objects.filter(requisition=requisition).exclude(id__in=kept_order_ids).delete()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Requisition updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete requisition"""
        try:
            requisition = get_object_or_404(Requisition, id=pk)
            requisition.delete()
            return JsonResponse({
                "success": True,
                "message": "Requisition deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class RequisitionDeleteView(View):
    """Delete requisition view"""
    
    def post(self, request, pk):
        try:
            requisition = get_object_or_404(Requisition, id=pk)
            requisition.delete()
            return JsonResponse({"success": True, "message": "Requisition deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
        

class PrintRequisitionView(View):
    """Print single or multiple requisitions"""
    
    def get(self, request, pk=None):
        # If pk is provided, print single requisition
        if pk:
            try:
                requisition = Requisition.objects.select_related(
                    'customer', 'sales_manager'
                ).get(id=pk)
                requisitions = [requisition]
            except Requisition.DoesNotExist:
                return redirect("requisition_list")
        else:
            # Multiple requisitions via query params
            ids = request.GET.get('ids', '')
            if ids:
                id_list = [int(x.strip()) for x in ids.split(',') if x.strip().isdigit()]
                requisitions = Requisition.objects.filter(
                    id__in=id_list
                ).select_related('customer', 'sales_manager')
            else:
                return redirect("requisition_list")
        
        return render(
            request,
            "Order_Management/Print_Requisition/print_requisition.html",
            {
                "requisitions": requisitions
            }
        )


# ==============================================================================================


# ─────────────────────────────────────────────────────────────────────────────
# Views for Work Order functionality
# ─────────────────────────────────────────────────────────────────────────────
class WorkOrderView(View):
    def get(self, request):
        customers = list(
            Customer.objects.values("id", "customer_name", "contact_number", "address")
        )
        sections = list(Profile.objects.values_list("id", "section_no"))
        alloys = list(Alloy.objects.values("id", "alloy_name"))  # ✅ FIXED
        workorders = WorkOrder.objects.all().order_by("-created_at")
        return render(
            request,
            "Order_Management/Work_Order/work_order.html",
            {
                "customers": customers,
                "sections": sections,
                "alloys": alloys,
                "workorders": workorders,
            },
        )


# API View to handle AJAX POST request for saving Work Order
@method_decorator(csrf_exempt, name="dispatch")
class WorkOrderAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            # ---- Save WorkOrder ----
            work_order = WorkOrder.objects.create(
                customer_id=data.get("customer"),
                contact_no=data.get("contact_no"),
                address=data.get("address"),
                sales_manager=data.get("sales_manager"),
                payment_terms=data.get("payment_terms"),
                expiry_date=data.get("expiry_date") or None,
                dispatch_date=data.get("dispatch_date") or None,
                delivery_date=data.get("delivery_date") or None,
                delivery_address=data.get("delivery_address") or "",
            )

            # ---- Save Goods ----
            for g in data.get("goods", []):
                WorkOrderGoods.objects.create(
                    work_order=work_order,
                    section_no_id=int(g.get("section_no") or 0),
                    wt_range=g.get("wt_range") or "",
                    cut_length=float(g.get("cut_length") or 0),
                    alloy_temper_id=int(g.get("alloy_temper") or 0),
                    pack=g.get("pack") or "",
                    qty=int(g.get("qty") or 0),
                    total_pack=int(g.get("total_pack") or 0),
                    total_no=int(g.get("total_no") or 0),
                    amount=float(g.get("amount") or 0),
                )

            # ---- Save Finance ----
            for f in data.get("finance", []):
                Finance.objects.create(
                    work_order=work_order,
                    amount=float(f.get("amount") or 0),
                    tax_type=f.get("tax_type") or "SGST",
                )

            return JsonResponse({"success": True, "id": work_order.id})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


# ─────────────────────────────────────────────────────────────────────────────
# Views for Work Order List functionality
# ─────────────────────────────────────────────────────────────────────────────
class WorkOrderListView(View):
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            # Replace 'title' with a field that exists in your model
            workorders = WorkOrder.objects.filter(
                customer__customer_name__icontains=search_query  # search by related Customer name
            ).order_by("-id")
        else:
            workorders = WorkOrder.objects.all().order_by("-id")

        # ---------------- Pagination ----------------
        paginator = Paginator(workorders, 10)  # 10 per page
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
            workorders_list = [
                model_to_dict(wo) for wo in page_obj
            ]  # dynamically serialize all fields
            return JsonResponse(
                {
                    "workorders": workorders_list,
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
            "Order_Management/Work_Order_List/work_order_list.html",
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


# Comprehensive Edit View with full update logic
class WorkOrderEditView(View):
    def get(self, request, pk):
        try:
            work_order = WorkOrder.objects.get(id=pk)
        except WorkOrder.DoesNotExist:
            return redirect("work_order_list")

        customers = list(
            Customer.objects.values("id", "customer_name", "contact_number", "address")
        )
        sections = list(Profile.objects.values_list("id", "section_no"))
        alloys = list(Alloy.objects.values("id", "alloy_name"))

        # Related goods
        goods = list(
            WorkOrderGoods.objects.filter(work_order=work_order).values(
                "id",
                "section_no__id",
                "section_no__section_no",
                "wt_range",
                "cut_length",
                "alloy_temper__id",
                "alloy_temper__alloy_name",
                "pack",
                "qty",
                "total_pack",
                "total_no",
                "amount",
            )
        )

        # Related finance
        finance = list(
            Finance.objects.filter(work_order=work_order).values(
                "id", "amount", "tax_type"
            )
        )

        return render(
            request,
            "Order_Management/Work_Order/work_order.html",
            {
                "work_order": work_order,
                "customers": customers,
                "sections": sections,
                "alloys": alloys,
                "goods": goods,
                "finance": finance,
                "edit_mode": True,
            },
        )

    def post(self, request, pk):
        try:
            work_order = WorkOrder.objects.get(id=pk)
        except WorkOrder.DoesNotExist:
            return JsonResponse({"success": False, "message": "Work Order not found"})

        try:
            data = json.loads(request.body)

            # ---- Update WorkOrder main fields ----
            work_order.customer_id = data.get("customer")
            work_order.contact_no = data.get("contact_no")
            work_order.address = data.get("address")
            work_order.sales_manager = data.get("sales_manager")
            work_order.payment_terms = data.get("payment_terms")
            work_order.expiry_date = data.get("expiry_date") or None
            work_order.dispatch_date = data.get("dispatch_date") or None
            work_order.delivery_date = data.get("delivery_date") or None
            work_order.delivery_address = data.get("delivery_address") or ""
            work_order.save()

            # ---- Handle Goods (update/create/delete) ----
            incoming_goods = data.get("goods", [])
            kept_goods_ids = []

            for g in incoming_goods:
                if g.get("id"):  # Update existing
                    goods_obj = WorkOrderGoods.objects.get(
                        id=g["id"], work_order=work_order
                    )
                    goods_obj.section_no_id = int(g.get("section_no") or 0)
                    goods_obj.wt_range = g.get("wt_range") or ""
                    goods_obj.cut_length = float(g.get("cut_length") or 0)
                    goods_obj.alloy_temper_id = int(g.get("alloy_temper") or 0)
                    goods_obj.pack = g.get("pack") or ""
                    goods_obj.qty = int(g.get("qty") or 0)
                    goods_obj.total_pack = int(g.get("total_pack") or 0)
                    goods_obj.total_no = int(g.get("total_no") or 0)
                    goods_obj.amount = float(g.get("amount") or 0)
                    goods_obj.save()
                    kept_goods_ids.append(goods_obj.id)
                else:  # Create new
                    new_goods = WorkOrderGoods.objects.create(
                        work_order=work_order,
                        section_no_id=int(g.get("section_no") or 0),
                        wt_range=g.get("wt_range") or "",
                        cut_length=float(g.get("cut_length") or 0),
                        alloy_temper_id=int(g.get("alloy_temper") or 0),
                        pack=g.get("pack") or "",
                        qty=int(g.get("qty") or 0),
                        total_pack=int(g.get("total_pack") or 0),
                        total_no=int(g.get("total_no") or 0),
                        amount=float(g.get("amount") or 0),
                    )
                    kept_goods_ids.append(new_goods.id)

            # Delete removed goods
            WorkOrderGoods.objects.filter(work_order=work_order).exclude(
                id__in=kept_goods_ids
            ).delete()

            # ---- Handle Finance (update/create/delete) ----
            incoming_finance = data.get("finance", [])
            kept_finance_ids = []

            for f in incoming_finance:
                if f.get("id"):  # Update existing
                    finance_obj = Finance.objects.get(id=f["id"], work_order=work_order)
                    finance_obj.amount = float(f.get("amount") or 0)
                    finance_obj.tax_type = f.get("tax_type") or "SGST"
                    finance_obj.save()
                    kept_finance_ids.append(finance_obj.id)
                else:  # Create new
                    new_finance = Finance.objects.create(
                        work_order=work_order,
                        amount=float(f.get("amount") or 0),
                        tax_type=f.get("tax_type") or "SGST",
                    )
                    kept_finance_ids.append(new_finance.id)

            # Delete removed finance
            Finance.objects.filter(work_order=work_order).exclude(
                id__in=kept_finance_ids
            ).delete()

            return JsonResponse(
                {
                    "success": True,
                    "id": work_order.id,
                    "message": "Work Order updated successfully!",
                    "updated": True,
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


# Delete Work Order View
class WorkOrderDeleteView(View):
    def post(self, request, pk):
        try:
            workorder = WorkOrder.objects.get(pk=pk)
            workorder.delete()
            return JsonResponse({"success": True})
        except WorkOrder.DoesNotExist:
            return JsonResponse({"success": False, "error": "Work Order not found"})


# ==============================================================================================


# ─────────────────────────────────────────────────────────────────────────────
# Views for requisiion print functionality
# ─────────────────────────────────────────────────────────────────────────────
class PrintRequisitionView(View):
    def get(self, request, pk=None):
        try:
            # Check if it's a bulk print request
            ids_param = request.GET.get("ids", "")

            if ids_param:
                # Bulk printing - flatten requisitions with their orders
                try:
                    requisition_ids = [
                        int(id.strip()) for id in ids_param.split(",") if id.strip()
                    ]
                    requisitions_qs = Requisition.objects.filter(
                        id__in=requisition_ids
                    ).prefetch_related('orders__section_no').order_by("id")

                    if not requisitions_qs.exists():
                        return render(
                            request,
                            "error.html",
                            {"error": "No valid requisitions found"},
                        )

                    # Flatten the data for printing
                    print_data = []
                    for req in requisitions_qs:
                        for order in req.orders.all():
                            print_data.append({
                                'requisition_no': req.requisition_no,
                                'customer': req.customer.name if hasattr(req.customer, 'name') else str(req.customer),
                                'section_no': order.section_no.section_no if hasattr(order.section_no, 'section_no') else str(order.section_no),
                                'wt_range': order.wt_range,
                                'cut_length': order.cut_length,
                                'qty': order.qty_in_no,
                                'address': req.address if hasattr(req, 'address') else '',
                                'dispatch_date': req.dispatch_date if hasattr(req, 'dispatch_date') else None,
                                'expiry_date': req.expiry_date if hasattr(req, 'expiry_date') else None,
                                'delivery_address': req.delivery_address if hasattr(req, 'delivery_address') else '',
                            })

                    context = {
                        "requisitions": print_data,
                        "requisition": None,
                        "is_bulk": True,
                    }

                except ValueError:
                    return render(
                        request, "error.html", {"error": "Invalid requisition IDs"}
                    )

            elif pk:
                # Single requisition printing (existing functionality)
                requisition = get_object_or_404(Requisition, pk=pk)
                context = {
                    "requisitions": None,
                    "requisition": requisition,
                    "is_bulk": False,
                }

            else:
                return render(
                    request, "error.html", {"error": "No requisition specified"}
                )

            return render(
                request,
                "Order_Management/Print_Requisition/print_requisition.html",
                context,
            )

        except Requisition.DoesNotExist:
            return render(request, "error.html", {"error": "Requisition not found"})
        except Exception as e:
            return render(
                request, "error.html", {"error": f"An error occurred: {str(e)}"}
            )


# ==============================================================================================


# ─────────────────────────────────────────────────────────────────────────────
# Views for work order print functionality
# ─────────────────────────────────────────────────────────────────────────────
class PrintWorkOrderView(View):
    def get(self, request, pk=None):
        try:
            # Check if it's a bulk print request
            ids_param = request.GET.get("ids", "")

            if ids_param:
                # Bulk printing
                try:
                    workorder_id = [
                        int(id.strip()) for id in ids_param.split(",") if id.strip()
                    ]
                    workorders = WorkOrder.objects.filter(id__in=workorder_id).order_by(
                        "id"
                    )

                    if not workorders.exists():
                        return render(
                            request,
                            "error.html",
                            {"error": "No valid workorders found"},
                        )

                    # For bulk printing, pass list of workorders
                    context = {
                        "workorders": workorders,
                        "workorder": None,  # Keep for backward compatibility
                    }

                except ValueError:
                    return render(
                        request, "error.html", {"error": "Invalid workorder IDs"}
                    )

            elif pk:
                # Single workorder printing (existing functionality)
                workorder = get_object_or_404(WorkOrder, pk=pk)
                context = {
                    "workorders": [
                        workorder
                    ],  # Make it a list for template consistency
                    "workorder": workorder,  # Keep for backward compatibility
                }

            else:
                return render(
                    request, "error.html", {"error": "No workorder specified"}
                )

            return render(
                request,
                "Order_Management/Print_Work_Order/print_work_order.html",
                context,
            )

        except WorkOrder.DoesNotExist:
            return render(request, "error.html", {"error": "WorkOrder not found"})
        except Exception as e:
            return render(
                request, "error.html", {"error": f"An error occurred: {str(e)}"}
            )


# ==============================================================================================
