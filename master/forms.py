from django import forms
from .models import *

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Die Master functionality
# ──────────────────────────────────────────────────────────────────────────────
class DieForm(forms.ModelForm):
    """Form for Die creation and editing"""
    
    class Meta:
        model = Die
        fields = [
            'die_no', 'die_name', 'image',  # Removed 'date' from here
            'press', 'supplier', 'project_no', 'date_of_receipt', 
            'no_of_cavity', 'req_weight', 'size', 'die_material', 
            'hardness', 'type', 'description', 'remark'
        ]
        widgets = {
            # Removed 'date' widget
            'die_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Die Number'
            }),
            'die_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Die Name'
            }),
            'press': forms.Select(attrs={
                'class': 'form-control'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-control'
            }),
            'project_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Project Number'
            }),
            'date_of_receipt': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'no_of_cavity': forms.Select(attrs={
                'class': 'form-control'
            }),
            'req_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter required weight',
                'step': '0.01'
            }),
            'size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter size'
            }),
            'die_material': forms.Select(attrs={
                'class': 'form-control'
            }),
            'hardness': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter hardness'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter remarks'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for dropdowns
        self.fields['press'].queryset = CompanyPress.objects.all()
        self.fields['supplier'].queryset = Supplier.objects.all()
        
        # Make some fields optional
        self.fields['description'].required = False
        self.fields['project_no'].required = False
        self.fields['image'].required = False
        self.fields['remark'].required = False
        self.fields['press'].required = False
        self.fields['supplier'].required = False
        self.fields['date_of_receipt'].required = False
# ──────────────────────────────────────────────────────────────────────────────
# Forms for Press functionality
# ──────────────────────────────────────────────────────────────────────────────
class PressForm(forms.ModelForm):
    class Meta:
        model = Press
        fields = ['press_name', 'date_added']
        widgets = {
            'date_added': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'press_name': 'Press Name',
            'date_added': 'Date Added',
        }

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Alloy  functionality
# ──────────────────────────────────────────────────────────────────────────────
class AlloyForm(forms.ModelForm):
    class Meta:
        model = Alloy
        fields = [
            'date', 'alloy_code', 'temper_designation', 'temper_code',
            'tensile_strength', 'material', 'silicon_percent', 'copper_percent'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly',  # Make date field read-only
                'style': 'background-color: #f0f0f0; cursor: not-allowed;'
            }),
            'alloy_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter alloy code'
            }),
            'temper_designation': forms.Select(attrs={
                'class': 'form-control'
            }),
            'temper_code': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tensile_strength': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tensile strength',
                'step': '0.01'
            }),
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter material'
            }),
            'silicon_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter silicon percentage',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'copper_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter copper percentage',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove required attribute from all fields
        for field_name, field in self.fields.items():
            field.required = False
            # Make date field non-editable
            if field_name == 'date':
                field.disabled = True
# ──────────────────────────────────────────────────────────────────────────────
# Forms for LOT functionality
# ──────────────────────────────────────────────────────────────────────────────
class LotForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = ['cast_no', 'press_no', 'date_of_extrusion', 'aging_no', 'date_added']
        widgets = {
            'date_of_extrusion': forms.DateInput(attrs={'type': 'date'}),
            'date_added': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'cast_no': 'Cost No',
            'press_no': 'Press No',
            'date_of_extrusion': 'Date of Extrusion',
            'aging_no': 'Aging No',
            'date_added': 'Date Added',
        }

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Profile functionality
# ──────────────────────────────────────────────────────────────────────────────
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['category', 'profile_name', 'section_no', 'length_mm', 'width_mm', 
                  'thickness_mm', 'weight_type', 'weight_value', 'shape_image', 'date_added'
                ]
        labels = {
            'category': 'Category',
            'profile_name': 'Profile Name',
            'section_no': 'Section No',
            'length_mm': 'Length (mm)',
            'width_mm': 'Width (mm)',
            'thickness_mm': 'Thickness (mm)',
            'weight_type': 'Weight Type',
            'weight_value': 'Weight Value',
            'shape_image': 'Shape Image',
            'date_added': 'Date Added',
        }
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter category'}),
            'profile_name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter profile name'}),
            'section_no': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter section number'}),
            'length_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01','placeholder': 'Enter length in mm'}),
            'width_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01','placeholder': 'Enter width in mm'}),
            'thickness_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01','placeholder': 'Enter thickness in mm'}),
            'weight_type': forms.Select(attrs={'class': 'form-control'}),
            'weight_value': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter weight value (e.g., 1700 or 1700-1800)'}),
            'shape_image': forms.ClearableFileInput(attrs={'class': 'form-control','accept': 'image/*'}),
            'date_added': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_profile_name(self):
        profile_name = self.cleaned_data['profile_name']
        if Profile.objects.filter(profile_name=profile_name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Profile with this name already exists.")
        return profile_name

    def clean_weight_value(self):
        weight_value = self.cleaned_data['weight_value']
        if weight_value:
            # Validate weight value format (single number or range)
            import re
            # Allow patterns like: 1700, 1700.5, 1700-1800, 1700.5-1800.5
            pattern = r'^\d+(\.\d+)?(\s*-\s*\d+(\.\d+)?)?$'
            if not re.match(pattern, weight_value.strip()):
                raise forms.ValidationError("Weight value must be a number or range (e.g., '1700' or '1700-1800')")
        return weight_value
# ──────────────────────────────────────────────────────────────────────────────
# Forms for Customer functionality
# ──────────────────────────────────────────────────────────────────────────────
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['date', 'name', 'customer_type', 'contact_no', 'contact_person', 'address']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed;'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'customer_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields.values():
            field.required = False
        
        # Set today's date as initial value if creating new customer
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Company functionality
# ──────────────────────────────────────────────────────────────────────────────
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'address', 'contact_no']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_no': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Forms for Company Shift functionality
# ──────────────────────────────────────────────────────────────────────────────
class CompanyShiftForm(forms.ModelForm):
    class Meta:
        model = CompanyShift
        fields = ['name', 'timing']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'timing': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 9:00 AM - 5:00 PM'}),
        }

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Company Press functionality
# ──────────────────────────────────────────────────────────────────────────────
class CompanyPressForm(forms.ModelForm):
    class Meta:
        model = CompanyPress
        fields = ['name', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500 tons, 1000 kg/hr'}),
        }

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Supplier functionality
# ──────────────────────────────────────────────────────────────────────────────
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['date', 'name', 'supplier_type', 'contact_no', 'contact_person', 'address']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name'
            }),
            'supplier_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_person'].required = False


# ──────────────────────────────────────────────────────────────────────────────
# Forms for Staff Type functionality
# ──────────────────────────────────────────────────────────────────────────────
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'date', 'staff_register_no', 'first_name', 'last_name',
            'address', 'contact_no', 'designation', 'shift_assigned',
            'assigned_to_press'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'staff_register_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter staff register number'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter address'
            }),
            'contact_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
            'designation': forms.Select(attrs={
                'class': 'form-control'
            }),
            'shift_assigned': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_to_press': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate press dropdown with company presses
        self.fields['assigned_to_press'].queryset = CompanyPress.objects.select_related('company').all()
        self.fields['assigned_to_press'].required = False
        self.fields['assigned_to_press'].empty_label = "Select Press"

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Section functionality
# ──────────────────────────────────────────────────────────────────────────────
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = [
            'date', 'section_no', 'section_name', 'section_image',
            'shape', 'type', 'usage', 'length_mm', 'width_mm',
            'thickness_mm', 'ionized'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'section_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section number (alphanumeric)'
            }),
            'section_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section name (alphanumeric)'
            }),
            'section_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'shape': forms.Select(attrs={
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'usage': forms.Select(attrs={
                'class': 'form-control'
            }),
            'length_mm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter length in mm',
                'step': '0.01'
            }),
            'width_mm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter width in mm',
                'step': '0.01'
            }),
            'thickness_mm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter thickness in mm',
                'step': '0.01'
            }),
            'ionized': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section_image'].required = False