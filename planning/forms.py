from django import forms
from .models import *

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Die Requisition functionality
# ──────────────────────────────────────────────────────────────────────────────
class DieRequisitionForm(forms.ModelForm):
    class Meta:
        model = DieRequisition
        fields = [
            'date', 'customer_requisition_no', 'section_no', 'section_name',
            'wt_range', 'die_no', 'die_name', 'present_wt',
            'no_of_cavity', 'cut_length'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed; font-weight: 600; color: #4a5568;'
            }),
            'customer_requisition_no': forms.Select(attrs={
                'class': 'form-control',
                'id': 'customer_requisition_no'
            }),
            'section_no': forms.Select(attrs={
                'class': 'form-control',
                'id': 'section_no',
                'readonly': 'readonly'
            }),
            'section_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'section_name',
                'readonly': 'readonly'
            }),
            'wt_range': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'wt_range',
                'readonly': 'readonly'
            }),
            'die_no': forms.Select(attrs={
                'class': 'form-control',
                'id': 'die_no'
            }),
            'die_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'die_name',
                'readonly': 'readonly'
            }),
            'present_wt': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'present_wt',
                'readonly': 'readonly',
                'step': '0.01'
            }),
            'no_of_cavity': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'no_of_cavity',
                'readonly': 'readonly'
            }),
            'cut_length': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
        
        # Make fields optional/required as needed
        self.fields['section_name'].required = False
        self.fields['die_name'].required = False
        self.fields['present_wt'].required = False
        self.fields['no_of_cavity'].required = False
        self.fields['cut_length'].required = False
        
        # Make wt_range required
        self.fields['wt_range'].required = True

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Production Planning functionality
# ──────────────────────────────────────────────────────────────────────────────
class ProductionPlanForm(forms.ModelForm):
    class Meta:
        model = ProductionPlan
        fields = [
            'date', 'cust_requisition_id', 'customer_name', 
            'die_requisition', 'die_no', 'section_no', 'section_name',
            'wt_per_piece', 'press', 'date_of_production', 'shift', 
            'operator', 'planned_qty'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed; font-weight: 600; color: #4a5568;'
            }),
            'cust_requisition_id': forms.Select(attrs={
                'class': 'form-control',
                'id': 'cust_requisition_id'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'customer_name',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed;'
            }),
            'die_requisition': forms.Select(attrs={
                'class': 'form-control',
                'id': 'die_requisition'
            }),
            'die_no': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'die_no',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed;'
            }),
            'section_no': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'section_no',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed;'
            }),
            'section_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'section_name',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed;'
            }),
            'wt_per_piece': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'wt_per_piece',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed;',
                'step': '0.01'
            }),
            'press': forms.Select(attrs={
                'class': 'form-control',
                'id': 'press'
            }),
            'date_of_production': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'date_of_production'
            }),
            'shift': forms.Select(attrs={
                'class': 'form-control',
                'id': 'shift'
            }),
            'operator': forms.Select(attrs={
                'class': 'form-control',
                'id': 'operator'
            }),
            'planned_qty': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'planned_qty',
                'min': '1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set today's date as default for new records
        if not self.instance.pk:
            self.initial['date'] = timezone.now().date()
        
        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False