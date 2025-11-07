from django import forms
from .models import *

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Die Requisition functionality
# ──────────────────────────────────────────────────────────────────────────────
class DieRequisitionForm(forms.ModelForm):
    class Meta:
        model = DieRequisition
        fields = [
            'date', 'press', 'shift', 'staff_name', 
            'customer_requisition_no', 'section_no', 'section_name',
            'wt_range', 'die_no', 'die_name', 'present_wt',
            'no_of_cavity','cut_length', 'remark'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly',  # Make date non-editable
                'style': 'background-color: #f0f0f0; cursor: not-allowed; font-weight: 600; color: #4a5568;'
            }),
            'press': forms.Select(attrs={
                'class': 'form-control',
                'id': 'press'
            }),
            'shift': forms.Select(attrs={
                'class': 'form-control',
                'id': 'shift'
            }),
            'staff_name': forms.Select(attrs={
                'class': 'form-control',
                'id': 'staff_name'
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
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter remarks'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
        
        # Make fields optional/required as needed
        self.fields['remark'].required = False
        self.fields['section_name'].required = False
        self.fields['die_name'].required = False
        self.fields['present_wt'].required = False
        self.fields['no_of_cavity'].required = False
        self.fields['cut_length'].required = False  # Make cut_length optional
        
        # Make wt_range required
        self.fields['wt_range'].required = True


# ──────────────────────────────────────────────────────────────────────────────
# Forms for Production Planning functionality
# ──────────────────────────────────────────────────────────────────────────────
class ProductionPlanForm(forms.ModelForm):
    class Meta:
        model = ProductionPlan
        fields = [
            'date', 'press', 'shift', 'cust_requisition_id', 
            'customer_name', 'die_requisition', 'die_no', 'wt_range',
            'cut_length', 'wt_per_piece', 'qty', 'billet_size',
            'no_of_billet', 'plan_recovery', 'current_recovery', 'status'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0; cursor: not-allowed;'
            }),
            'press': forms.Select(attrs={
                'class': 'form-control',
                'id': 'press'
            }),
            'shift': forms.Select(attrs={
                'class': 'form-control',
                'id': 'shift'
            }),
            'cust_requisition_id': forms.Select(attrs={
                'class': 'form-control',
                'id': 'cust_requisition_id'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'customer_name',
                'readonly': 'readonly'
            }),
            'die_requisition': forms.Select(attrs={
                'class': 'form-control',
                'id': 'die_requisition'
            }),
            'die_no': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'die_no',
                'readonly': 'readonly'
            }),
            'wt_range': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'wt_range',
                'readonly': 'readonly'
            }),
            'cut_length': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'cut_length',
                'readonly': 'readonly'
            }),
            'wt_per_piece': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'wt_per_piece',
                'readonly': 'readonly',
                'step': '0.01'
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'qty',
                'min': '1'
            }),
            'billet_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'billet_size',
                'step': '0.01'
            }),
            'no_of_billet': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'no_of_billet',
                'min': '1'
            }),
            'plan_recovery': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'plan_recovery',
                'step': '0.01'
            }),
            'current_recovery': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'current_recovery',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'status'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set today's date as default for new records
        if not self.instance.pk:
            self.initial['date'] = timezone.now().date()
        
        # Only Press is required
        self.fields['press'].required = True
        
        # Make all other fields optional
        self.fields['date'].required = False
        self.fields['shift'].required = False
        self.fields['cust_requisition_id'].required = False
        self.fields['customer_name'].required = False
        self.fields['die_requisition'].required = False
        self.fields['die_no'].required = False
        self.fields['wt_range'].required = False
        self.fields['cut_length'].required = False
        self.fields['wt_per_piece'].required = False
        self.fields['qty'].required = False
        self.fields['billet_size'].required = False
        self.fields['no_of_billet'].required = False
        self.fields['plan_recovery'].required = False
        self.fields['current_recovery'].required = False
        self.fields['status'].required = False