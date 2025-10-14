# import necessary modules and decorators
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64

from .models import *
from .forms import *


# ─────────────────────────────────────────────────────────────────────────────
# Views for Die Master functionality
# ─────────────────────────────────────────────────────────────────────────────
class DieFormView(View):
    """Render the die form page with template."""

    def get(self, request):
        # Generate preview of next Die ID
        next_die_id = Die.generate_die_id()
        
        context = {
            'edit_mode': False,
            'next_die_id': next_die_id,
            'form': DieForm(),
            'presses': CompanyPress.objects.all(),
            'suppliers': Supplier.objects.all()
        }
        return render(request, 'Master/Die/die.html', context)


class DieEditView(View):
    """Render the die edit form page with template."""

    def get(self, request, die_id):
        die = get_object_or_404(Die, id=die_id)
        
        context = {
            'edit_mode': True,
            'die': die,
            'form': DieForm(instance=die),
            'presses': CompanyPress.objects.all(),
            'suppliers': Supplier.objects.all()
        }
        return render(request, 'Master/Die/die.html', context)


class DieListView(View):
    """Render the die list page with template."""

    def get(self, request):
        dies = Die.objects.all().select_related('press', 'supplier')
        
        # Handle search functionality
        global_search = request.GET.get('global_search', '').strip()
        if global_search:
            dies = dies.filter(
                die_no__icontains=global_search
            )
        
        dies = dies.order_by('-created_at')
        
        context = {
            'dies': dies,
            'global_search': global_search
        }
        return render(request, 'Master/Die_List/die_list.html', context)


@method_decorator(csrf_exempt, name="dispatch")
class DieAPI(View):
    """API endpoints for CRUD on Die model."""

    def get(self, request):
        """Get all dies as JSON or get next Die ID"""
        # Check if requesting next Die ID
        if request.GET.get('action') == 'get_next_id':
            next_die_id = Die.generate_die_id()
            return JsonResponse({
                'success': True,
                'next_die_id': next_die_id
            })
        
        # Otherwise return all dies
        dies = Die.objects.all().select_related('press', 'supplier').order_by('-created_at')
        formatted = [
            {
                "id": d.id,
                "die_id": d.die_id,
                "date": d.date.strftime("%Y-%m-%d"),
                "die_no": d.die_no,
                "die_name": d.die_name,
                "description": d.description,
                "press": d.press.name if d.press else "N/A",
                "press_id": d.press.id if d.press else None,
                "supplier": d.supplier.name if d.supplier else "N/A",
                "supplier_id": d.supplier.id if d.supplier else None,
                "project_no": d.project_no,
                "date_of_receipt": d.date_of_receipt.strftime("%Y-%m-%d") if d.date_of_receipt else None,
                "no_of_cavity": d.no_of_cavity,
                "req_weight": str(d.req_weight),
                "size": d.size,
                "die_material": d.die_material,
                "hardness": d.hardness,
                "type": d.type,
                "image_url": d.image.url if d.image else None,
                "remark": d.remark,
                "created_at": d.created_at.strftime("%Y-%m-%d"),
            }
            for d in dies
        ]
        return JsonResponse({"success": True, "dies": formatted})

    @method_decorator(csrf_exempt)
    def post(self, request):
        """Create a new die"""
        try:
            # Handle multipart form data for image upload
            date = request.POST.get('date')
            die_no = request.POST.get('die_no', '').strip()
            die_name = request.POST.get('die_name', '').strip()
            press_id = request.POST.get('press')
            supplier_id = request.POST.get('supplier')
            project_no = request.POST.get('project_no', '').strip()
            date_of_receipt = request.POST.get('date_of_receipt')
            no_of_cavity = request.POST.get('no_of_cavity')
            req_weight = request.POST.get('req_weight')
            size = request.POST.get('size', '').strip()
            die_material = request.POST.get('die_material')
            hardness = request.POST.get('hardness', '').strip()
            die_type = request.POST.get('type')
            description = request.POST.get('description', '').strip()
            remark = request.POST.get('remark', '').strip()
            image = request.FILES.get('image')
            
            # Validate required fields
            if not all([date, die_no, die_name, no_of_cavity, 
                       req_weight, size, die_material, hardness, die_type]):
                return JsonResponse({
                    'success': False, 
                    'message': 'Please fill all required fields.'
                })
            
            # Create die (die_id will be auto-generated in save method)
            die = Die.objects.create(
                date=date,
                die_no=die_no,
                die_name=die_name,
                press_id=press_id if press_id else None,
                supplier_id=supplier_id if supplier_id else None,
                project_no=project_no,
                date_of_receipt=date_of_receipt if date_of_receipt else None,
                no_of_cavity=no_of_cavity,
                req_weight=req_weight,
                size=size,
                die_material=die_material,
                hardness=hardness,
                type=die_type,
                description=description,
                remark=remark,
                image=image
            )
            
            return JsonResponse({
                'success': True,
                'created': True,
                'message': 'Die created successfully!',
                'die': {
                    'id': die.id,
                    'die_id': die.die_id,
                    'die_no': die.die_no,
                    'image_url': die.image.url if die.image else None
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': str(e)
            })


@method_decorator(csrf_exempt, name="dispatch")
class DieDetailAPI(View):
    """API for edit & delete Die"""
    def get(self, request, die_id):
        """Get die details as JSON"""
        try:
            die = get_object_or_404(Die, id=die_id)
            
            return JsonResponse({
                'success': True,
                'die': {
                    'id': die.id,
                    'die_id': die.die_id,
                    'date': die.date.strftime("%Y-%m-%d"),
                    'die_no': die.die_no,
                    'die_name': die.die_name,
                    'description': die.description,
                    'press_id': die.press.id if die.press else None,
                    'press_name': die.press.name if die.press else "N/A",
                    'supplier_id': die.supplier.id if die.supplier else None,
                    'supplier_name': die.supplier.name if die.supplier else "N/A",
                    'project_no': die.project_no,
                    'date_of_receipt': die.date_of_receipt.strftime("%Y-%m-%d") if die.date_of_receipt else None,
                    'no_of_cavity': die.no_of_cavity,
                    'req_weight': str(die.req_weight),
                    'size': die.size,
                    'die_material': die.die_material,
                    'hardness': die.hardness,
                    'type': die.type,
                    'image_url': die.image.url if die.image else None,
                    'remark': die.remark,
                    'created_at': die.created_at.strftime("%Y-%m-%d"),
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    def post(self, request, die_id):
        """Edit an existing die"""
        try:
            die = get_object_or_404(Die, id=die_id)
            
            # Handle multipart form data for image upload
            date = request.POST.get('date')
            die_no = request.POST.get('die_no', '').strip()
            die_name = request.POST.get('die_name', '').strip()
            press_id = request.POST.get('press')
            supplier_id = request.POST.get('supplier')
            project_no = request.POST.get('project_no', '').strip()
            date_of_receipt = request.POST.get('date_of_receipt')
            no_of_cavity = request.POST.get('no_of_cavity')
            req_weight = request.POST.get('req_weight')
            size = request.POST.get('size', '').strip()
            die_material = request.POST.get('die_material')
            hardness = request.POST.get('hardness', '').strip()
            die_type = request.POST.get('type')
            description = request.POST.get('description', '').strip()
            remark = request.POST.get('remark', '').strip()
            image = request.FILES.get('image')
            
            # Validate required fields
            if not all([date, die_no, die_name, no_of_cavity, 
                       req_weight, size, die_material, hardness, die_type]):
                return JsonResponse({
                    'success': False, 
                    'message': 'Please fill all required fields.'
                })
            
            # Update die (die_id remains unchanged)
            die.date = date
            die.die_no = die_no
            die.die_name = die_name
            die.press_id = press_id if press_id else None
            die.supplier_id = supplier_id if supplier_id else None
            die.project_no = project_no
            die.date_of_receipt = date_of_receipt if date_of_receipt else None
            die.no_of_cavity = no_of_cavity
            die.req_weight = req_weight
            die.size = size
            die.die_material = die_material
            die.hardness = hardness
            die.type = die_type
            die.description = description
            die.remark = remark
            
            # Update image if new one is uploaded
            if image:
                die.image = image
            
            die.save()
            
            return JsonResponse({
                'success': True,
                'updated': True,
                'message': 'Die updated successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': str(e)
            })

    def delete(self, request, die_id):
        """Delete a die by ID"""
        try:
            die = get_object_or_404(Die, id=die_id)
            die_no = die.die_no
            
            # Delete image file if exists
            if die.image:
                default_storage.delete(die.image.name)
            
            die.delete()
            return JsonResponse({
                'success': True, 
                'message': f'Die "{die_no}" deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': str(e)
            })


# ─────────────────────────────────────────────────────────────────────────────
# Views for Press functionality
# ─────────────────────────────────────────────────────────────────────────────
class PressListView(View):
    """Render the press list page with template + handle add."""

    def get(self, request):
        presses = Press.objects.all().order_by("-date_added")
        form = PressForm()
        return render(
            request, "Master/Press/press.html", {"presses": presses, "form": form}
        )

    def post(self, request):
        form = PressForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("press-list")  # ✅ use your URL name here
        # if form invalid, re-render with errors
        presses = Press.objects.all().order_by("-date_added")
        return render(
            request, "Master/Press/press.html", {"presses": presses, "form": form}
        )


@method_decorator(csrf_exempt, name="dispatch")
class PressAPI(View):
    """API endpoints for CRUD on Press model."""

    def get(self, request):
        """Get all presses as JSON"""
        presses = Press.objects.all().order_by("-date_added")
        formatted = [
            {
                "id": p.id,
                "press_name": p.press_name,
                "date_added": p.date_added.strftime("%Y-%m-%d"),
            }
            for p in presses
        ]
        return JsonResponse({"success": True, "presses": formatted})

    @method_decorator(csrf_exempt)
    def post(self, request):
        """Add a new press"""
        try:
            data = json.loads(request.body)
            press_name = data.get("press_name")
            date_added = parse_date(data.get("date_added"))

            if not press_name or not date_added:
                return JsonResponse(
                    {"success": False, "message": "Missing required fields."}
                )

            press = Press.objects.create(
                press_name=press_name,
                date_added=date_added,
            )

            return JsonResponse(
                {
                    "success": True,
                    "press": {
                        "id": press.id,
                        "press_name": press.press_name,
                        "date_added": press.date_added.strftime("%Y-%m-%d"),
                    },
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class PressDetailAPI(View):
    """API for edit & delete Press"""

    def post(self, request, press_id):
        """Edit an existing press"""
        try:
            data = json.loads(request.body)
            press_name = data.get("press_name")
            date_added = parse_date(data.get("date_added"))

            if not press_name or not date_added:
                return JsonResponse(
                    {"success": False, "message": "Missing required fields."}
                )

            press = get_object_or_404(Press, id=press_id)  # ✅ FIXED
            press.press_name = press_name
            press.date_added = date_added
            press.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    def delete(self, request, press_id):
        """Delete a press by id"""
        try:
            press = get_object_or_404(Press, id=press_id)  # ✅ FIXED
            press.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


# ─────────────────────────────────────────────────────────────────────────────
# Views for Alloy Harness functionality
# ─────────────────────────────────────────────────────────────────────────────
class AlloyListView(View):
    """Render the alloy list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            alloys = Alloy.objects.filter(
                models.Q(alloy_code__icontains=search_query) |
                models.Q(material__icontains=search_query) |
                models.Q(temper_designation__icontains=search_query)
            ).order_by("-created_at")
        else:
            alloys = Alloy.objects.all().order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(alloys, 10)  # 10 per page
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
            alloys_list = []
            for a in page_obj:
                alloy_dict = model_to_dict(a)
                alloys_list.append(alloy_dict)
            
            return JsonResponse(
                {
                    "alloys": alloys_list,
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
            "Master/Alloy_List/alloy_list.html",
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


class AlloyFormView(View):
    """Render the alloy form page"""
    
    def get(self, request):
        # Generate preview of next Alloy ID
        next_alloy_id = Alloy.generate_alloy_id()
        
        return render(
            request,
            "Master/Alloy/alloy.html",
            {
                "edit_mode": False,
                "next_alloy_id": next_alloy_id,
            },
        )


class AlloyEditView(View):
    """Render the alloy edit form page"""
    
    def get(self, request, pk):
        try:
            alloy = Alloy.objects.get(id=pk)
        except Alloy.DoesNotExist:
            return redirect("alloy_list")
        
        return render(
            request,
            "Master/Alloy/alloy.html",
            {
                "alloy": alloy,
                "edit_mode": True,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class AlloyAPI(View):
    """API for CRUD on Alloy"""
    
    def get(self, request):
        """Get all alloys or get next Alloy ID"""
        # Check if requesting next Alloy ID
        if request.GET.get('action') == 'get_next_id':
            next_alloy_id = Alloy.generate_alloy_id()
            return JsonResponse({
                'success': True,
                'next_alloy_id': next_alloy_id
            })
        
        # Otherwise return all alloys
        alloys = Alloy.objects.all().order_by("-created_at")
        
        formatted = []
        for a in alloys:
            alloy_data = {
                "id": a.id,
                "alloy_id": a.alloy_id,
                "date": a.date.strftime("%Y-%m-%d"),
                "alloy_code": a.alloy_code,
                "temper_designation": a.temper_designation,
                "temper_code": a.temper_code,
                "tensile_strength": str(a.tensile_strength),
                "material": a.material,
                "silicon_percent": str(a.silicon_percent),
                "copper_percent": str(a.copper_percent),
                "created_at": a.created_at.strftime("%Y-%m-%d"),
            }
            formatted.append(alloy_data)
        
        return JsonResponse({"success": True, "alloys": formatted})
    
    def post(self, request):
        """Create a new alloy"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip() if isinstance(data.get("date"), str) else data.get("date")
            alloy_code = data.get("alloy_code", "").strip()
            temper_designation = data.get("temper_designation", "").strip()
            temper_code = data.get("temper_code", "").strip()
            tensile_strength = data.get("tensile_strength", "").strip() if isinstance(data.get("tensile_strength"), str) else data.get("tensile_strength")
            material = data.get("material", "").strip()
            silicon_percent = data.get("silicon_percent", "").strip() if isinstance(data.get("silicon_percent"), str) else data.get("silicon_percent")
            copper_percent = data.get("copper_percent", "").strip() if isinstance(data.get("copper_percent"), str) else data.get("copper_percent")
            
            if not all([date, alloy_code, temper_designation, temper_code, tensile_strength, material, silicon_percent, copper_percent]):
                return JsonResponse({
                    "success": False,
                    "message": "All fields are required."
                })
            
            # Check if alloy_code already exists
            if Alloy.objects.filter(alloy_code=alloy_code).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Alloy Code already exists."
                })
            
            # Create alloy (alloy_id will be auto-generated)
            alloy = Alloy.objects.create(
                date=date,
                alloy_code=alloy_code,
                temper_designation=temper_designation,
                temper_code=temper_code,
                tensile_strength=tensile_strength,
                material=material,
                silicon_percent=silicon_percent,
                copper_percent=copper_percent
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Alloy created successfully!",
                    "alloy": {
                        "id": alloy.id,
                        "alloy_id": alloy.alloy_id,
                        "alloy_code": alloy.alloy_code,
                        "temper_designation": alloy.temper_designation,
                        "created_at": alloy.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class AlloyDetailAPI(View):
    """API for get, edit & delete Alloy"""
    
    def get(self, request, pk):
        """Get alloy details"""
        try:
            alloy = get_object_or_404(Alloy, id=pk)
            return JsonResponse(
                {
                    "success": True,
                    "alloy": {
                        "id": alloy.id,
                        "alloy_id": alloy.alloy_id,
                        "date": alloy.date.strftime("%Y-%m-%d"),
                        "alloy_code": alloy.alloy_code,
                        "temper_designation": alloy.temper_designation,
                        "temper_code": alloy.temper_code,
                        "tensile_strength": str(alloy.tensile_strength),
                        "material": alloy.material,
                        "silicon_percent": str(alloy.silicon_percent),
                        "copper_percent": str(alloy.copper_percent),
                        "created_at": alloy.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update alloy"""
        try:
            alloy = get_object_or_404(Alloy, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip() if isinstance(data.get("date"), str) else data.get("date")
            alloy_code = data.get("alloy_code", "").strip()
            temper_designation = data.get("temper_designation", "").strip()
            temper_code = data.get("temper_code", "").strip()
            tensile_strength = data.get("tensile_strength", "").strip() if isinstance(data.get("tensile_strength"), str) else data.get("tensile_strength")
            material = data.get("material", "").strip()
            silicon_percent = data.get("silicon_percent", "").strip() if isinstance(data.get("silicon_percent"), str) else data.get("silicon_percent")
            copper_percent = data.get("copper_percent", "").strip() if isinstance(data.get("copper_percent"), str) else data.get("copper_percent")
            
            if not all([date, alloy_code, temper_designation, temper_code, tensile_strength, material, silicon_percent, copper_percent]):
                return JsonResponse({
                    "success": False,
                    "message": "All fields are required."
                })
            
            # Check if alloy_code already exists (excluding current alloy)
            if Alloy.objects.filter(alloy_code=alloy_code).exclude(id=pk).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Alloy Code already exists."
                })
            
            # Update alloy (alloy_id remains unchanged)
            alloy.date = date
            alloy.alloy_code = alloy_code
            alloy.temper_designation = temper_designation
            alloy.temper_code = temper_code
            alloy.tensile_strength = tensile_strength
            alloy.material = material
            alloy.silicon_percent = silicon_percent
            alloy.copper_percent = copper_percent
            alloy.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Alloy updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete alloy"""
        try:
            alloy = get_object_or_404(Alloy, id=pk)
            alloy.delete()
            return JsonResponse({
                "success": True,
                "message": "Alloy deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class AlloyDeleteView(View):
    """Delete alloy view"""
    
    def post(self, request, pk):
        try:
            alloy = get_object_or_404(Alloy, id=pk)
            alloy.delete()
            return JsonResponse({"success": True, "message": "Alloy deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


# ─────────────────────────────────────────────────────────────────────────────
# Views for LOT functionality
# ─────────────────────────────────────────────────────────────────────────────
class LotListView(View):
    """Render the lot list page"""

    def get(self, request):
        lots = Lot.objects.all().order_by("-created_at")
        presses = Press.objects.all()
        return render(
            request, "Master/Lot/lot.html", {"lots": lots, "presses": presses}
        )


@method_decorator(csrf_exempt, name="dispatch")
class LotAPI(View):
    """API for CRUD on Lot"""

    def get(self, request):
        lots = Lot.objects.all().order_by("-created_at")
        formatted = [
            {
                "id": lot.id,
                "cast_no": lot.cast_no,
                "press_no_name": lot.press_no.press_name,  # ✅ renamed for frontend display
                "press_id": lot.press_no.id,
                "date_of_extrusion": lot.date_of_extrusion.strftime("%Y-%m-%d"),
                "aging_no": lot.aging_no,
                "lot_number": lot.lot_number,
                "date_added": lot.date_added.strftime("%Y-%m-%d"),
            }
            for lot in lots
        ]
        return JsonResponse({"success": True, "lots": formatted})

    def post(self, request):
        try:
            data = json.loads(request.body)
            cast_no = data.get("cast_no")
            press_id = data.get("press_no")
            date_of_extrusion = parse_date(data.get("date_of_extrusion"))
            aging_no = data.get("aging_no")
            date_added = parse_date(data.get("date_added"))

            if not (cast_no and press_id and date_of_extrusion and aging_no):
                return JsonResponse(
                    {"success": False, "message": "Missing required fields."}
                )

            press = get_object_or_404(Press, id=press_id)

            lot = Lot.objects.create(
                cast_no=cast_no,
                press_no=press,
                date_of_extrusion=date_of_extrusion,
                aging_no=aging_no,
                date_added=date_added,
            )

            return JsonResponse(
                {
                    "success": True,
                    "lot": {
                        "id": lot.id,
                        "cast_no": lot.cast_no,
                        "press_no": lot.press_no.press_name,
                        "date_of_extrusion": lot.date_of_extrusion.strftime("%Y-%m-%d"),
                        "aging_no": lot.aging_no,
                        "lot_number": lot.lot_number,
                        "date_added": lot.date_added.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class LotDetailAPI(View):
    """API for edit & delete Lot"""

    def post(self, request, lot_id):
        try:
            data = json.loads(request.body)
            cast_no = data.get("cast_no")
            press_id = data.get("press_no")
            date_of_extrusion = parse_date(data.get("date_of_extrusion"))
            aging_no = data.get("aging_no")
            date_added = parse_date(data.get("date_added"))

            if not (cast_no and press_id and date_of_extrusion and aging_no):
                return JsonResponse(
                    {"success": False, "message": "Missing required fields."}
                )

            lot = get_object_or_404(Lot, id=lot_id)
            press = get_object_or_404(Press, id=press_id)

            lot.cast_no = cast_no
            lot.press_no = press
            lot.date_of_extrusion = date_of_extrusion
            lot.aging_no = aging_no
            lot.date_added = date_added
            lot.lot_number = lot.generate_lot_number()
            lot.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    def delete(self, request, lot_id):
        try:
            lot = get_object_or_404(Lot, id=lot_id)
            lot.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


# ──────────────────────────────────────────────────────────────────────────────
# View for Profile functionality
# ──────────────────────────────────────────────────────────────────────────────
class ProfileListView(View):
    """Render the profile list page"""

    def get(self, request):
        profiles = Profile.objects.all().order_by("-created_at")
        weight_types = Profile.WEIGHT_TYPE_CHOICES
        return render(
            request,
            "Master/Profile/profile.html",
            {"profiles": profiles, "weight_types": weight_types},
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProfileAPI(View):
    """API for CRUD on Profile"""

    def get(self, request):
        try:
            profiles = Profile.objects.all().order_by("-created_at")
            formatted = [
                {
                    "id": p.id,
                    "category": p.category,
                    "profile_name": p.profile_name,
                    "section_no": p.section_no,
                    "length_mm": float(p.length_mm) if p.length_mm else None,
                    "width_mm": float(p.width_mm) if p.width_mm else None,
                    "thickness_mm": float(p.thickness_mm) if p.thickness_mm else None,
                    "weight_type": p.get_weight_type_display(),
                    "weight_type_key": p.weight_type,
                    "weight_value": p.weight_value,  # Remove float() conversion - keep as string
                    "shape_image": p.shape_image.url if p.shape_image else None,
                    "date_added": p.date_added.strftime("%Y-%m-%d"),
                }
                for p in profiles
            ]
            return JsonResponse({"success": True, "profiles": formatted})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    def post(self, request):
        try:
            data = request.POST
            shape_file = request.FILES.get("shape_image")

            # Validate required fields
            required_fields = ['category', 'profile_name', 'section_no', 'weight_type', 'weight_value']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({"success": False, "message": f"{field} is required"})

            profile = Profile.objects.create(
                category=data.get("category"),
                profile_name=data.get("profile_name"),
                section_no=data.get("section_no"),
                length_mm=data.get("length_mm") or None,
                width_mm=data.get("width_mm") or None,
                thickness_mm=data.get("thickness_mm") or None,
                weight_type=data.get("weight_type"),
                weight_value=data.get("weight_value"),  # Now stores string value
                shape_image=shape_file,
                date_added=parse_date(data.get("date_added")) if data.get("date_added") else None,
            )

            return JsonResponse({
                "success": True,
                "message": "Profile created successfully",
                "profile": {
                    "id": profile.id,
                    "category": profile.category,
                    "profile_name": profile.profile_name,
                    "section_no": profile.section_no,
                    "length_mm": float(profile.length_mm) if profile.length_mm else None,
                    "width_mm": float(profile.width_mm) if profile.width_mm else None,
                    "thickness_mm": float(profile.thickness_mm) if profile.thickness_mm else None,
                    "weight_type": profile.get_weight_type_display(),
                    "weight_value": profile.weight_value,  # Now string value
                    "shape_image": profile.shape_image.url if profile.shape_image else None,
                    "date_added": profile.date_added.strftime("%Y-%m-%d"),
                },
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class ProfileDetailAPI(View):
    """API for edit & delete Profile"""

    def post(self, request, profile_id):
        try:
            data = request.POST
            shape_file = request.FILES.get("shape_image")

            profile = get_object_or_404(Profile, id=profile_id)
            
            # Update fields
            if data.get("category"):
                profile.category = data.get("category")
            if data.get("profile_name"):
                profile.profile_name = data.get("profile_name")
            if data.get("section_no"):
                profile.section_no = data.get("section_no")
            
            profile.length_mm = data.get("length_mm") or None
            profile.width_mm = data.get("width_mm") or None
            profile.thickness_mm = data.get("thickness_mm") or None
            
            if data.get("weight_type"):
                profile.weight_type = data.get("weight_type")
            if data.get("weight_value"):
                profile.weight_value = data.get("weight_value")
            
            if data.get("date_added"):
                profile.date_added = parse_date(data.get("date_added"))
            
            if shape_file:
                profile.shape_image = shape_file
                
            profile.save()

            return JsonResponse({
                "success": True, 
                "message": "Profile updated successfully"
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    def delete(self, request, profile_id):
        try:
            profile = get_object_or_404(Profile, id=profile_id)
            profile.delete()
            return JsonResponse({
                "success": True, 
                "message": "Profile deleted successfully"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

# ─────────────────────────────────────────────────────────────────────────────
# Views for Customer functionality
# ─────────────────────────────────────────────────────────────────────────────
class CustomerListView(View):
    """Render the customer list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            customers = Customer.objects.filter(
                name__icontains=search_query
            ).order_by("-created_at")
        else:
            customers = Customer.objects.all().order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(customers, 10)  # 10 per page
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
            customers_list = [model_to_dict(s) for s in page_obj]
            return JsonResponse(
                {
                    "customers": customers_list,
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
            "Master/Customer_List/customer_list.html",
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


class CustomerFormView(View):
    """Render the customer form page"""
    
    def get(self, request):
        # Generate preview of next Customer ID
        next_customer_id = Customer.generate_customer_id()
        
        return render(
            request,
            "Master/Customer/customer.html",
            {
                "edit_mode": False,
                "next_customer_id": next_customer_id,
            },
        )


class CustomerEditView(View):
    """Render the customer edit form page"""
    
    def get(self, request, pk):
        try:
            customer = Customer.objects.get(id=pk)
        except Customer.DoesNotExist:
            return redirect("customer_list")
        
        return render(
            request,
            "Master/Customer/customer.html",
            {
                "customer": customer,
                "edit_mode": True,
            },
        )
    
    def post(self, request, pk):
        try:
            customer = Customer.objects.get(id=pk)
        except Customer.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Customer not found"}
            )
        
        try:
            data = json.loads(request.body)
            
            # Update customer fields
            customer.date = data.get("date")
            customer.name = data.get("name")
            customer.customer_type = data.get("customer_type")
            customer.contact_no = data.get("contact_no")
            customer.contact_person = data.get("contact_person", "")
            customer.address = data.get("address")
            customer.save()
            
            return JsonResponse(
                {
                    "success": True,
                    "id": customer.id,
                    "message": "Customer updated successfully!",
                    "updated": True,
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class CustomerAPI(View):
    """API for CRUD on Customer"""
    
    def get(self, request):
        """Get all customers or get next Customer ID"""
        # Check if requesting next Customer ID
        if request.GET.get('action') == 'get_next_id':
            next_customer_id = Customer.generate_customer_id()
            return JsonResponse({
                'success': True,
                'next_customer_id': next_customer_id
            })
        
        # Otherwise return all customers
        customers = Customer.objects.all().order_by("-created_at")
        formatted = [
            {
                "id": s.id,
                "customer_id": s.customer_id,
                "date": s.date.strftime("%Y-%m-%d"),
                "name": s.name,
                "customer_type": s.customer_type,
                "contact_no": s.contact_no,
                "contact_person": s.contact_person,
                "address": s.address,
                "created_at": s.created_at.strftime("%Y-%m-%d"),
            }
            for s in customers
        ]
        return JsonResponse({"success": True, "customers": formatted})
    
    def post(self, request):
        """Create a new customer"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            name = data.get("name", "").strip()
            customer_type = data.get("customer_type", "").strip()
            contact_no = data.get("contact_no", "").strip()
            contact_person = data.get("contact_person", "").strip()
            address = data.get("address", "").strip()
            
            if not all([date, name, customer_type, contact_no, address]):
                return JsonResponse({
                    "success": False,
                    "message": "Date, Name, Customer Type, Contact No, and Address are required."
                })
            
            # Create customer (customer_id will be auto-generated)
            customer = Customer.objects.create(
                date=date,
                name=name,
                customer_type=customer_type,
                contact_no=contact_no,
                contact_person=contact_person,
                address=address
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Customer created successfully!",
                    "customer": {
                        "id": customer.id,
                        "customer_id": customer.customer_id,
                        "name": customer.name,
                        "customer_type": customer.customer_type,
                        "contact_no": customer.contact_no,
                        "contact_person": customer.contact_person,
                        "address": customer.address,
                        "created_at": customer.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class CustomerDetailAPI(View):
    """API for get, edit & delete Customer"""
    
    def get(self, request, pk):
        """Get customer details"""
        try:
            customer = get_object_or_404(Customer, id=pk)
            return JsonResponse(
                {
                    "success": True,
                    "supplier": {
                        "id": customer.id,
                        "customer_id": customer.customer_id,
                        "date": customer.date.strftime("%Y-%m-%d"),
                        "name": customer.name,
                        "customer_type": customer.customer_type,
                        "contact_no": customer.contact_no,
                        "contact_person": customer.contact_person,
                        "address": customer.address,
                        "created_at": customer.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update customer"""
        try:
            customer = get_object_or_404(Customer, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            name = data.get("name", "").strip()
            customer_type = data.get("customer_type", "").strip()
            contact_no = data.get("contact_no", "").strip()
            contact_person = data.get("contact_person", "").strip()
            address = data.get("address", "").strip()
            
            if not all([date, name, customer_type, contact_no, address]):
                return JsonResponse({
                    "success": False,
                    "message": "Date, Name, Customer Type, Contact No, and Address are required."
                })
            
            # Update customer (customer_id remains unchanged)
            customer.date = date
            customer.name = name
            customer.customer_type = customer_type
            customer.contact_no = contact_no
            customer.contact_person = contact_person
            customer.address = address
            customer.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Customer updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete customer"""
        try:
            customer = get_object_or_404(Customer, id=pk)
            customer.delete()
            return JsonResponse({
                "success": True,
                "message": "Customer deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class CustomerDeleteView(View):
    """Delete customer view"""
    
    def post(self, request, pk):
        try:
            customer = get_object_or_404(Customer, id=pk)
            customer.delete()
            return JsonResponse({"success": True, "message": "Customer deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

# ──────────────────────────────────────────────────────────────────────────────
# Views for Company functionality
# ──────────────────────────────────────────────────────────────────────────────
class CompanyFormView(View):
    """Render the company form page with template."""

    def get(self, request):
        context = {
            'edit_mode': False,
            'form': CompanyForm()
        }
        return render(request, 'Master/Company/company.html', context)


class CompanyEditView(View):
    """Render the company edit form page with template."""

    def get(self, request, company_id):
        company = get_object_or_404(Company, id=company_id)
        shifts = company.shifts.all()
        presses = company.presses.all()
        
        context = {
            'edit_mode': True,
            'company': company,
            'shifts': list(shifts.values('id', 'name', 'timing')),
            'presses': list(presses.values('id', 'name', 'capacity')),
            'form': CompanyForm(instance=company)
        }
        return render(request, 'Master/Company/company.html', context)


class CompanyListView(View):
    """Render the company list page with template."""

    def get(self, request):
        companies = Company.objects.all().select_related().prefetch_related('shifts', 'presses')
        
        # Handle search functionality
        global_search = request.GET.get('global_search', '').strip()
        if global_search:
            companies = companies.filter(
                name__icontains=global_search
            )
        
        companies = companies.order_by('-created_at')
        
        context = {
            'companies': companies,
            'global_search': global_search
        }
        return render(request, 'Master/Company_List/company_list.html', context)


@method_decorator(csrf_exempt, name="dispatch")
class CompanyAPI(View):
    """API endpoints for CRUD on Company model."""

    def get(self, request):
        """Get all companies as JSON"""
        companies = Company.objects.all().order_by('-created_at')
        formatted = [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "address": c.address,
                "contact_no": c.contact_no,
                "created_at": c.created_at.strftime("%Y-%m-%d"),
                "shifts_count": c.shifts.count(),
                "presses_count": c.presses.count(),
            }
            for c in companies
        ]
        return JsonResponse({"success": True, "companies": formatted})

    @method_decorator(csrf_exempt)
    def post(self, request):
        """Create a new company with shifts and presses"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            name = data.get('name', '').strip()
            contact_no = data.get('contact_no', '').strip()
            address = data.get('address', '').strip()
            
            if not name or not contact_no or not address:
                return JsonResponse({
                    'success': False, 
                    'message': 'Name, contact number, and address are required fields.'
                })
            
            # Create company
            company = Company.objects.create(
                name=name,
                description=data.get('description', ''),
                address=address,
                contact_no=contact_no
            )
            
            # Create shifts
            shifts_data = data.get('shifts', [])
            created_shifts = []
            for shift_data in shifts_data:
                shift_name = shift_data.get('name', '').strip()
                shift_timing = shift_data.get('timing', '').strip()
                if shift_name and shift_timing:
                    shift = CompanyShift.objects.create(
                        company=company,
                        name=shift_name,
                        timing=shift_timing
                    )
                    created_shifts.append({
                        'id': shift.id,
                        'name': shift.name,
                        'timing': shift.timing
                    })
            
            # Create presses
            presses_data = data.get('presses', [])
            created_presses = []
            for press_data in presses_data:
                press_name = press_data.get('name', '').strip()
                press_capacity = press_data.get('capacity', '').strip()
                if press_name and press_capacity:
                    press = CompanyPress.objects.create(
                        company=company,
                        name=press_name,
                        capacity=press_capacity
                    )
                    created_presses.append({
                        'id': press.id,
                        'name': press.name,
                        'capacity': press.capacity
                    })
            
            return JsonResponse({
                'success': True,
                'created': True,
                'message': 'Company created successfully!',
                'company': {
                    'id': company.id,
                    'name': company.name,
                    'description': company.description,
                    'address': company.address,
                    'contact_no': company.contact_no,
                    'shifts': created_shifts,
                    'presses': created_presses
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': str(e)
            })


@method_decorator(csrf_exempt, name="dispatch")
class CompanyDetailAPI(View):
    """API for edit & delete Company"""

    def get(self, request, company_id):
        """Get company details as JSON"""
        try:
            company = get_object_or_404(Company, id=company_id)
            shifts = company.shifts.all()
            presses = company.presses.all()
            
            return JsonResponse({
                'success': True,
                'company': {
                    'id': company.id,
                    'name': company.name,
                    'description': company.description,
                    'address': company.address,
                    'contact_no': company.contact_no,
                    'created_at': company.created_at.strftime("%Y-%m-%d"),
                },
                'shifts': list(shifts.values('id', 'name', 'timing')),
                'presses': list(presses.values('id', 'name', 'capacity'))
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    def post(self, request, company_id):
        """Edit an existing company with shifts and presses"""
        try:
            company = get_object_or_404(Company, id=company_id)
            data = json.loads(request.body)
            
            # Validate required fields
            name = data.get('name', '').strip()
            contact_no = data.get('contact_no', '').strip()
            address = data.get('address', '').strip()
            
            if not name or not contact_no or not address:
                return JsonResponse({
                    'success': False, 
                    'message': 'Name, contact number, and address are required fields.'
                })
            
            # Update company
            company.name = name
            company.description = data.get('description', '')
            company.address = address
            company.contact_no = contact_no
            company.save()
            
            # Handle shifts
            shifts_data = data.get('shifts', [])
            existing_shift_ids = []
            
            for shift_data in shifts_data:
                shift_name = shift_data.get('name', '').strip()
                shift_timing = shift_data.get('timing', '').strip()
                
                if shift_name and shift_timing:
                    if shift_data.get('id'):
                        # Update existing shift
                        try:
                            shift = CompanyShift.objects.get(id=shift_data['id'], company=company)
                            shift.name = shift_name
                            shift.timing = shift_timing
                            shift.save()
                            existing_shift_ids.append(shift.id)
                        except CompanyShift.DoesNotExist:
                            # Create new shift if ID doesn't exist
                            shift = CompanyShift.objects.create(
                                company=company,
                                name=shift_name,
                                timing=shift_timing
                            )
                            existing_shift_ids.append(shift.id)
                    else:
                        # Create new shift
                        shift = CompanyShift.objects.create(
                            company=company,
                            name=shift_name,
                            timing=shift_timing
                        )
                        existing_shift_ids.append(shift.id)
            
            # Delete removed shifts
            company.shifts.exclude(id__in=existing_shift_ids).delete()
            
            # Handle presses
            presses_data = data.get('presses', [])
            existing_press_ids = []
            
            for press_data in presses_data:
                press_name = press_data.get('name', '').strip()
                press_capacity = press_data.get('capacity', '').strip()
                
                if press_name and press_capacity:
                    if press_data.get('id'):
                        # Update existing press
                        try:
                            press = CompanyPress.objects.get(id=press_data['id'], company=company)
                            press.name = press_name
                            press.capacity = press_capacity
                            press.save()
                            existing_press_ids.append(press.id)
                        except CompanyPress.DoesNotExist:
                            # Create new press if ID doesn't exist
                            press = CompanyPress.objects.create(
                                company=company,
                                name=press_name,
                                capacity=press_capacity
                            )
                            existing_press_ids.append(press.id)
                    else:
                        # Create new press
                        press = CompanyPress.objects.create(
                            company=company,
                            name=press_name,
                            capacity=press_capacity
                        )
                        existing_press_ids.append(press.id)
            
            # Delete removed presses
            company.presses.exclude(id__in=existing_press_ids).delete()
            
            return JsonResponse({
                'success': True,
                'updated': True,
                'message': 'Company updated successfully!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': str(e)
            })

    def delete(self, request, company_id):
        """Delete a company by ID"""
        try:
            company = get_object_or_404(Company, id=company_id)
            company_name = company.name
            company.delete()
            return JsonResponse({
                'success': True, 
                'message': f'Company "{company_name}" deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': str(e)
            })
        

# ──────────────────────────────────────────────────────────────────────────────
# Views for Supplier functionality
# ──────────────────────────────────────────────────────────────────────────────
class SupplierListView(View):
    """Render the supplier list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            suppliers = Supplier.objects.filter(
                name__icontains=search_query
            ).order_by("-created_at")
        else:
            suppliers = Supplier.objects.all().order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(suppliers, 10)  # 10 per page
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
            suppliers_list = [model_to_dict(s) for s in page_obj]
            return JsonResponse(
                {
                    "suppliers": suppliers_list,
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
            "Master/Supplier_List/supplier_list.html",
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


class SupplierFormView(View):
    """Render the supplier form page"""
    
    def get(self, request):
        # Generate preview of next Supplier ID
        next_supplier_id = Supplier.generate_supplier_id()
        
        return render(
            request,
            "Master/Supplier/supplier.html",
            {
                "edit_mode": False,
                "next_supplier_id": next_supplier_id,
            },
        )


class SupplierEditView(View):
    """Render the supplier edit form page"""
    
    def get(self, request, pk):
        try:
            supplier = Supplier.objects.get(id=pk)
        except Supplier.DoesNotExist:
            return redirect("supplier_list")
        
        return render(
            request,
            "Master/Supplier/supplier.html",
            {
                "supplier": supplier,
                "edit_mode": True,
            },
        )
    
    def post(self, request, pk):
        try:
            supplier = Supplier.objects.get(id=pk)
        except Supplier.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Supplier not found"}
            )
        
        try:
            data = json.loads(request.body)
            
            # Update supplier fields
            supplier.date = data.get("date")
            supplier.name = data.get("name")
            supplier.supplier_type = data.get("supplier_type")
            supplier.contact_no = data.get("contact_no")
            supplier.contact_person = data.get("contact_person", "")
            supplier.address = data.get("address")
            supplier.save()
            
            return JsonResponse(
                {
                    "success": True,
                    "id": supplier.id,
                    "message": "Supplier updated successfully!",
                    "updated": True,
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class SupplierAPI(View):
    """API for CRUD on Supplier"""
    
    def get(self, request):
        """Get all suppliers or get next Supplier ID"""
        # Check if requesting next Supplier ID
        if request.GET.get('action') == 'get_next_id':
            next_supplier_id = Supplier.generate_supplier_id()
            return JsonResponse({
                'success': True,
                'next_supplier_id': next_supplier_id
            })
        
        # Otherwise return all suppliers
        suppliers = Supplier.objects.all().order_by("-created_at")
        formatted = [
            {
                "id": s.id,
                "supplier_id": s.supplier_id,
                "date": s.date.strftime("%Y-%m-%d"),
                "name": s.name,
                "supplier_type": s.supplier_type,
                "contact_no": s.contact_no,
                "contact_person": s.contact_person,
                "address": s.address,
                "created_at": s.created_at.strftime("%Y-%m-%d"),
            }
            for s in suppliers
        ]
        return JsonResponse({"success": True, "suppliers": formatted})
    
    def post(self, request):
        """Create a new supplier"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            name = data.get("name", "").strip()
            supplier_type = data.get("supplier_type", "").strip()
            contact_no = data.get("contact_no", "").strip()
            contact_person = data.get("contact_person", "").strip()
            address = data.get("address", "").strip()
            
            if not all([date, name, supplier_type, contact_no, address]):
                return JsonResponse({
                    "success": False,
                    "message": "Date, Name, Supplier Type, Contact No, and Address are required."
                })
            
            # Create supplier (supplier_id will be auto-generated)
            supplier = Supplier.objects.create(
                date=date,
                name=name,
                supplier_type=supplier_type,
                contact_no=contact_no,
                contact_person=contact_person,
                address=address
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Supplier created successfully!",
                    "supplier": {
                        "id": supplier.id,
                        "supplier_id": supplier.supplier_id,
                        "name": supplier.name,
                        "supplier_type": supplier.supplier_type,
                        "contact_no": supplier.contact_no,
                        "contact_person": supplier.contact_person,
                        "address": supplier.address,
                        "created_at": supplier.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class SupplierDetailAPI(View):
    """API for get, edit & delete Supplier"""
    
    def get(self, request, pk):
        """Get supplier details"""
        try:
            supplier = get_object_or_404(Supplier, id=pk)
            return JsonResponse(
                {
                    "success": True,
                    "supplier": {
                        "id": supplier.id,
                        "supplier_id": supplier.supplier_id,
                        "date": supplier.date.strftime("%Y-%m-%d"),
                        "name": supplier.name,
                        "supplier_type": supplier.supplier_type,
                        "contact_no": supplier.contact_no,
                        "contact_person": supplier.contact_person,
                        "address": supplier.address,
                        "created_at": supplier.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update supplier"""
        try:
            supplier = get_object_or_404(Supplier, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            name = data.get("name", "").strip()
            supplier_type = data.get("supplier_type", "").strip()
            contact_no = data.get("contact_no", "").strip()
            contact_person = data.get("contact_person", "").strip()
            address = data.get("address", "").strip()
            
            if not all([date, name, supplier_type, contact_no, address]):
                return JsonResponse({
                    "success": False,
                    "message": "Date, Name, Supplier Type, Contact No, and Address are required."
                })
            
            # Update supplier (supplier_id remains unchanged)
            supplier.date = date
            supplier.name = name
            supplier.supplier_type = supplier_type
            supplier.contact_no = contact_no
            supplier.contact_person = contact_person
            supplier.address = address
            supplier.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Supplier updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete supplier"""
        try:
            supplier = get_object_or_404(Supplier, id=pk)
            supplier.delete()
            return JsonResponse({
                "success": True,
                "message": "Supplier deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class SupplierDeleteView(View):
    """Delete supplier view"""
    
    def post(self, request, pk):
        try:
            supplier = get_object_or_404(Supplier, id=pk)
            supplier.delete()
            return JsonResponse({"success": True, "message": "Supplier deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


# ──────────────────────────────────────────────────────────────────────────────
# Views for Staff functionality
# ──────────────────────────────────────────────────────────────────────────────
class StaffListView(View):
    """Render the staff list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            staff_members = Staff.objects.filter(
                models.Q(staff_register_no__icontains=search_query) |
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query)
            ).select_related('assigned_to_press__company').order_by("-created_at")
        else:
            staff_members = Staff.objects.select_related(
                'assigned_to_press__company'
            ).all().order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(staff_members, 10)  # 10 per page
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
            staff_list = []
            for s in page_obj:
                staff_dict = model_to_dict(s)
                if s.assigned_to_press:
                    staff_dict['assigned_to_press'] = str(s.assigned_to_press)
                staff_list.append(staff_dict)
            
            return JsonResponse(
                {
                    "staff": staff_list,
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
            "Master/Staff_List/staff_list.html",
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


class StaffFormView(View):
    """Render the staff form page"""
    
    def get(self, request):
        # Generate preview of next Staff ID
        next_staff_id = Staff.generate_staff_id()
        
        # Get all company presses for dropdown
        company_presses = CompanyPress.objects.select_related('company').all()
        
        return render(
            request,
            "Master/Staff/staff.html",
            {
                "edit_mode": False,
                "next_staff_id": next_staff_id,
                "company_presses": company_presses,
            },
        )


class StaffEditView(View):
    """Render the staff edit form page"""
    
    def get(self, request, pk):
        try:
            staff = Staff.objects.select_related(
                'assigned_to_press__company'
            ).get(id=pk)
        except Staff.DoesNotExist:
            return redirect("staff_list")
        
        # Get all company presses for dropdown
        company_presses = CompanyPress.objects.select_related('company').all()
        
        return render(
            request,
            "Master/Staff/staff.html",
            {
                "staff": staff,
                "edit_mode": True,
                "company_presses": company_presses,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class StaffAPI(View):
    """API for CRUD on Staff"""
    
    def get(self, request):
        """Get all staff or get next Staff ID"""
        # Check if requesting next Staff ID
        if request.GET.get('action') == 'get_next_id':
            next_staff_id = Staff.generate_staff_id()
            return JsonResponse({
                'success': True,
                'next_staff_id': next_staff_id
            })
        
        # Get company presses for dropdown
        if request.GET.get('action') == 'get_presses':
            presses = CompanyPress.objects.select_related('company').all()
            press_list = [
                {
                    'id': p.id,
                    'name': f"{p.company.name} - {p.name}",
                    'company': p.company.name
                }
                for p in presses
            ]
            return JsonResponse({
                'success': True,
                'presses': press_list
            })
        
        # Otherwise return all staff
        staff_members = Staff.objects.select_related(
            'assigned_to_press__company'
        ).all().order_by("-created_at")
        
        formatted = []
        for s in staff_members:
            staff_data = {
                "id": s.id,
                "staff_id": s.staff_id,
                "date": s.date.strftime("%Y-%m-%d"),
                "staff_register_no": s.staff_register_no,
                "first_name": s.first_name,
                "last_name": s.last_name,
                "address": s.address,
                "contact_no": s.contact_no,
                "designation": s.designation,
                "shift_assigned": s.shift_assigned,
                "assigned_to_press": s.assigned_to_press.id if s.assigned_to_press else None,
                "assigned_to_press_name": str(s.assigned_to_press) if s.assigned_to_press else "",
                "created_at": s.created_at.strftime("%Y-%m-%d"),
            }
            formatted.append(staff_data)
        
        return JsonResponse({"success": True, "staff": formatted})
    
    def post(self, request):
        """Create a new staff member"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            staff_register_no = data.get("staff_register_no", "").strip()
            first_name = data.get("first_name", "").strip()
            last_name = data.get("last_name", "").strip()
            address = data.get("address", "").strip()
            contact_no = data.get("contact_no", "").strip()
            designation = data.get("designation", "").strip()
            shift_assigned = data.get("shift_assigned", "").strip()
            
            if not all([date, staff_register_no, first_name, last_name, address, contact_no, designation, shift_assigned]):
                return JsonResponse({
                    "success": False,
                    "message": "All fields except Assigned To Press are required."
                })
            
            # Check if staff_register_no already exists
            if Staff.objects.filter(staff_register_no=staff_register_no).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Staff Register No already exists."
                })
            
            # Get assigned press if provided
            assigned_to_press_id = data.get("assigned_to_press")
            assigned_to_press = None
            if assigned_to_press_id:
                try:
                    assigned_to_press = CompanyPress.objects.get(id=assigned_to_press_id)
                except CompanyPress.DoesNotExist:
                    pass
            
            # Create staff (staff_id will be auto-generated)
            staff = Staff.objects.create(
                date=date,
                staff_register_no=staff_register_no,
                first_name=first_name,
                last_name=last_name,
                address=address,
                contact_no=contact_no,
                designation=designation,
                shift_assigned=shift_assigned,
                assigned_to_press=assigned_to_press
            )
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Staff created successfully!",
                    "staff": {
                        "id": staff.id,
                        "staff_id": staff.staff_id,
                        "staff_register_no": staff.staff_register_no,
                        "first_name": staff.first_name,
                        "last_name": staff.last_name,
                        "designation": staff.designation,
                        "created_at": staff.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class StaffDetailAPI(View):
    """API for get, edit & delete Staff"""
    
    def get(self, request, pk):
        """Get staff details"""
        try:
            staff = get_object_or_404(Staff, id=pk)
            return JsonResponse(
                {
                    "success": True,
                    "staff": {
                        "id": staff.id,
                        "staff_id": staff.staff_id,
                        "date": staff.date.strftime("%Y-%m-%d"),
                        "staff_register_no": staff.staff_register_no,
                        "first_name": staff.first_name,
                        "last_name": staff.last_name,
                        "address": staff.address,
                        "contact_no": staff.contact_no,
                        "designation": staff.designation,
                        "shift_assigned": staff.shift_assigned,
                        "assigned_to_press": staff.assigned_to_press.id if staff.assigned_to_press else None,
                        "created_at": staff.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update staff"""
        try:
            staff = get_object_or_404(Staff, id=pk)
            data = json.loads(request.body)
            
            # Validate required fields
            date = data.get("date", "").strip()
            staff_register_no = data.get("staff_register_no", "").strip()
            first_name = data.get("first_name", "").strip()
            last_name = data.get("last_name", "").strip()
            address = data.get("address", "").strip()
            contact_no = data.get("contact_no", "").strip()
            designation = data.get("designation", "").strip()
            shift_assigned = data.get("shift_assigned", "").strip()
            
            if not all([date, staff_register_no, first_name, last_name, address, contact_no, designation, shift_assigned]):
                return JsonResponse({
                    "success": False,
                    "message": "All fields except Assigned To Press are required."
                })
            
            # Check if staff_register_no already exists (excluding current staff)
            if Staff.objects.filter(staff_register_no=staff_register_no).exclude(id=pk).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Staff Register No already exists."
                })
            
            # Get assigned press if provided
            assigned_to_press_id = data.get("assigned_to_press")
            assigned_to_press = None
            if assigned_to_press_id:
                try:
                    assigned_to_press = CompanyPress.objects.get(id=assigned_to_press_id)
                except CompanyPress.DoesNotExist:
                    pass
            
            # Update staff (staff_id remains unchanged)
            staff.date = date
            staff.staff_register_no = staff_register_no
            staff.first_name = first_name
            staff.last_name = last_name
            staff.address = address
            staff.contact_no = contact_no
            staff.designation = designation
            staff.shift_assigned = shift_assigned
            staff.assigned_to_press = assigned_to_press
            staff.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Staff updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete staff"""
        try:
            staff = get_object_or_404(Staff, id=pk)
            staff.delete()
            return JsonResponse({
                "success": True,
                "message": "Staff deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class StaffDeleteView(View):
    """Delete staff view"""
    
    def post(self, request, pk):
        try:
            staff = get_object_or_404(Staff, id=pk)
            staff.delete()
            return JsonResponse({"success": True, "message": "Staff deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
        

# ──────────────────────────────────────────────────────────────────────────────
# Views for Section functionality
# ──────────────────────────────────────────────────────────────────────────────
class SectionListView(View):
    """Render the section list page"""
    
    def get(self, request):
        # ---------------- Global Search ----------------
        search_query = request.GET.get("global_search", "")
        if search_query:
            sections = Section.objects.filter(
                models.Q(section_no__icontains=search_query) |
                models.Q(section_name__icontains=search_query)
            ).order_by("-created_at")
        else:
            sections = Section.objects.all().order_by("-created_at")
        
        # ---------------- Pagination ----------------
        paginator = Paginator(sections, 10)  # 10 per page
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
            sections_list = []
            for s in page_obj:
                section_dict = model_to_dict(s, exclude=['section_image'])
                if s.section_image:
                    section_dict['section_image'] = s.section_image.url
                sections_list.append(section_dict)
            
            return JsonResponse(
                {
                    "sections": sections_list,
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
            "Master/Section_List/section_list.html",
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


class SectionFormView(View):
    """Render the section form page"""
    
    def get(self, request):
        # Generate preview of next Section ID
        next_section_id = Section.generate_section_id()
        
        return render(
            request,
            "Master/Section/section.html",
            {
                "edit_mode": False,
                "next_section_id": next_section_id,
            },
        )


class SectionEditView(View):
    """Render the section edit form page"""
    
    def get(self, request, pk):
        try:
            section = Section.objects.get(id=pk)
        except Section.DoesNotExist:
            return redirect("section_list")
        
        return render(
            request,
            "Master/Section/section.html",
            {
                "section": section,
                "edit_mode": True,
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class SectionAPI(View):
    """API for CRUD on Section"""
    
    def get(self, request):
        """Get all sections or get next Section ID"""
        # Check if requesting next Section ID
        if request.GET.get('action') == 'get_next_id':
            next_section_id = Section.generate_section_id()
            return JsonResponse({
                'success': True,
                'next_section_id': next_section_id
            })
        
        # Otherwise return all sections
        sections = Section.objects.all().order_by("-created_at")
        
        formatted = []
        for s in sections:
            section_data = {
                "id": s.id,
                "section_id": s.section_id,
                "date": s.date.strftime("%Y-%m-%d"),
                "section_no": s.section_no,
                "section_name": s.section_name,
                "section_image": s.section_image.url if s.section_image else None,
                "shape": s.shape,
                "type": s.type,
                "usage": s.usage,
                "length_mm": str(s.length_mm),
                "width_mm": str(s.width_mm),
                "thickness_mm": str(s.thickness_mm),
                "ionized": s.ionized,
                "created_at": s.created_at.strftime("%Y-%m-%d"),
            }
            formatted.append(section_data)
        
        return JsonResponse({"success": True, "sections": formatted})
    
    def post(self, request):
        """Create a new section"""
        try:
            # Check if it's form data with file upload or JSON
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle form data with file
                data = request.POST
                image_file = request.FILES.get('section_image')
            else:
                # Handle JSON data
                data = json.loads(request.body)
                image_file = None
                
                # Handle base64 image if present
                if 'section_image_base64' in data and data['section_image_base64']:
                    image_data = data['section_image_base64']
                    if ',' in image_data:
                        format, imgstr = image_data.split(';base64,')
                        ext = format.split('/')[-1]
                        image_file = ContentFile(base64.b64decode(imgstr), name=f'section_{data.get("section_no")}.{ext}')
            
            # Validate required fields
            date = data.get("date", "").strip() if isinstance(data.get("date"), str) else data.get("date")
            section_no = data.get("section_no", "").strip()
            section_name = data.get("section_name", "").strip()
            shape = data.get("shape", "").strip()
            type_val = data.get("type", "").strip()
            usage = data.get("usage", "").strip()
            length_mm = data.get("length_mm", "").strip() if isinstance(data.get("length_mm"), str) else data.get("length_mm")
            width_mm = data.get("width_mm", "").strip() if isinstance(data.get("width_mm"), str) else data.get("width_mm")
            thickness_mm = data.get("thickness_mm", "").strip() if isinstance(data.get("thickness_mm"), str) else data.get("thickness_mm")
            
            if not all([date, section_no, section_name, shape, type_val, usage, length_mm, width_mm, thickness_mm]):
                return JsonResponse({
                    "success": False,
                    "message": "All fields except Section Image are required."
                })
            
            # Check if section_no already exists
            if Section.objects.filter(section_no=section_no).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Section No already exists."
                })
            
            # Get ionized value
            ionized = data.get("ionized") in ['true', 'True', True, 'on', '1']
            
            # Create section (section_id will be auto-generated)
            section = Section.objects.create(
                date=date,
                section_no=section_no,
                section_name=section_name,
                shape=shape,
                type=type_val,
                usage=usage,
                length_mm=length_mm,
                width_mm=width_mm,
                thickness_mm=thickness_mm,
                ionized=ionized
            )
            
            # Handle image upload
            if image_file:
                section.section_image = image_file
                section.save()
            
            return JsonResponse(
                {
                    "success": True,
                    "created": True,
                    "message": "Section created successfully!",
                    "section": {
                        "id": section.id,
                        "section_id": section.section_id,
                        "section_no": section.section_no,
                        "section_name": section.section_name,
                        "shape": section.shape,
                        "type": section.type,
                        "created_at": section.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class SectionDetailAPI(View):
    """API for get, edit & delete Section"""
    
    def get(self, request, pk):
        """Get section details"""
        try:
            section = get_object_or_404(Section, id=pk)
            return JsonResponse(
                {
                    "success": True,
                    "section": {
                        "id": section.id,
                        "section_id": section.section_id,
                        "date": section.date.strftime("%Y-%m-%d"),
                        "section_no": section.section_no,
                        "section_name": section.section_name,
                        "section_image": section.section_image.url if section.section_image else None,
                        "shape": section.shape,
                        "type": section.type,
                        "usage": section.usage,
                        "length_mm": str(section.length_mm),
                        "width_mm": str(section.width_mm),
                        "thickness_mm": str(section.thickness_mm),
                        "ionized": section.ionized,
                        "created_at": section.created_at.strftime("%Y-%m-%d"),
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def post(self, request, pk):
        """Update section"""
        try:
            section = get_object_or_404(Section, id=pk)
            
            # Check if it's form data with file upload or JSON
            if request.content_type and 'multipart/form-data' in request.content_type:
                data = request.POST
                image_file = request.FILES.get('section_image')
            else:
                data = json.loads(request.body)
                image_file = None
                
                # Handle base64 image if present
                if 'section_image_base64' in data and data['section_image_base64']:
                    image_data = data['section_image_base64']
                    if ',' in image_data:
                        format, imgstr = image_data.split(';base64,')
                        ext = format.split('/')[-1]
                        image_file = ContentFile(base64.b64decode(imgstr), name=f'section_{data.get("section_no")}.{ext}')
            
            # Validate required fields
            date = data.get("date", "").strip() if isinstance(data.get("date"), str) else data.get("date")
            section_no = data.get("section_no", "").strip()
            section_name = data.get("section_name", "").strip()
            shape = data.get("shape", "").strip()
            type_val = data.get("type", "").strip()
            usage = data.get("usage", "").strip()
            length_mm = data.get("length_mm", "").strip() if isinstance(data.get("length_mm"), str) else data.get("length_mm")
            width_mm = data.get("width_mm", "").strip() if isinstance(data.get("width_mm"), str) else data.get("width_mm")
            thickness_mm = data.get("thickness_mm", "").strip() if isinstance(data.get("thickness_mm"), str) else data.get("thickness_mm")
            
            if not all([date, section_no, section_name, shape, type_val, usage, length_mm, width_mm, thickness_mm]):
                return JsonResponse({
                    "success": False,
                    "message": "All fields except Section Image are required."
                })
            
            # Check if section_no already exists (excluding current section)
            if Section.objects.filter(section_no=section_no).exclude(id=pk).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Section No already exists."
                })
            
            # Get ionized value
            ionized = data.get("ionized") in ['true', 'True', True, 'on', '1']
            
            # Update section (section_id remains unchanged)
            section.date = date
            section.section_no = section_no
            section.section_name = section_name
            section.shape = shape
            section.type = type_val
            section.usage = usage
            section.length_mm = length_mm
            section.width_mm = width_mm
            section.thickness_mm = thickness_mm
            section.ionized = ionized
            
            # Handle image upload
            if image_file:
                section.section_image = image_file
            
            section.save()
            
            return JsonResponse({
                "success": True,
                "updated": True,
                "message": "Section updated successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    def delete(self, request, pk):
        """Delete section"""
        try:
            section = get_object_or_404(Section, id=pk)
            # Delete image file if exists
            if section.section_image:
                section.section_image.delete()
            section.delete()
            return JsonResponse({
                "success": True,
                "message": "Section deleted successfully!"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class SectionDeleteView(View):
    """Delete section view"""
    
    def post(self, request, pk):
        try:
            section = get_object_or_404(Section, id=pk)
            # Delete image file if exists
            if section.section_image:
                section.section_image.delete()
            section.delete()
            return JsonResponse({"success": True, "message": "Section deleted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})