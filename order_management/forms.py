from django import forms
from .models import *
from datetime import date

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Requisition functionality
# ──────────────────────────────────────────────────────────────────────────────
class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = [
            'date', 'requisition_no', 'customer', 'contact_no',
            'address', 'sales_manager', 'expiry_date', 'dispatch_date'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'requisition_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter requisition number'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_no': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'readonly': 'readonly'
            }),
            'sales_manager': forms.Select(attrs={
                'class': 'form-control'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'dispatch_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate dropdowns
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['customer'].empty_label = "Select Customer"
        
        self.fields['sales_manager'].queryset = Staff.objects.all()
        self.fields['sales_manager'].empty_label = "Select Sales Manager"
        self.fields['sales_manager'].required = True
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
            self.fields['expiry_date'].initial = date.today()
            self.fields['dispatch_date'].initial = date.today()

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Requisition's Goods functionality
# ──────────────────────────────────────────────────────────────────────────────
class RequisitionOrderForm(forms.ModelForm):
    class Meta:
        model = RequisitionOrder
        fields = ['section_no', 'wt_range', 'cut_length', 'qty_in_no']
        widgets = {
            'section_no': forms.Select(attrs={
                'class': 'form-control'
            }),
            'wt_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10-20'
            }),
            'cut_length': forms.Select(attrs={
                'class': 'form-control'
            }),
            'qty_in_no': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section_no'].queryset = Section.objects.all()
        self.fields['section_no'].empty_label = "Select Section"

# ──────────────────────────────────────────────────────────────────────────────
# Forms for Work Order functionality
# ──────────────────────────────────────────────────────────────────────────────
class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'
        labels = {
            'customer': 'Customer',
            'contact_no': 'Contact Number',
            'address': 'Address',
            'sales_manager': 'Sales Manager',
            'payment_terms': 'Payment Terms',
            'delivery_date': 'Delivery Date',
            'dispatch_date': 'Dispatch Date',
            'expiry_date': 'Expiry Date',
            'delivery_address': 'Delivery Address',
        }
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'dispatch_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        if not self.initial.get('expiry_date'):
            self.fields['expiry_date'].initial = today
        if not self.initial.get('dispatch_date'):
            self.fields['dispatch_date'].initial = today
        if not self.initial.get('delivery_date'):
            self.fields['delivery_date'].initial = today


# ──────────────────────────────────────────────────────────────────────────────
# Forms for Work Order's Goods functionality
# ──────────────────────────────────────────────────────────────────────────────
class WorkOrderGoodsForm(forms.ModelForm):
    class Meta:
        model = WorkOrderGoods
        fields = '__all__'
        labels = {
            'work_order': 'Work Order',
            'section_no': 'Section No',
            'wt_range': 'Weight Range',
            'cut_length': 'Cut Length',
            'alloy_temper': 'Alloy Temper',
            'pack': 'Pack',
            'qty': 'Quantity',
            'total_pack': 'Total Pack',
            'total_no': 'Total No',
            'amount': 'Amount',
        }
        widgets = {
            'wt_range': forms.TextInput(attrs={'placeholder': 'Enter weight range'}),
            'cut_length': forms.NumberInput(attrs={'step': '0.01'}),
            'pack': forms.TextInput(attrs={'placeholder': 'Enter pack type'}),
            'qty': forms.NumberInput(),
            'total_pack': forms.NumberInput(),
            'total_no': forms.NumberInput(),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }


#─────────────────────────────────────────────────────────────────────────────
# Forms for Finance functionality
#─────────────────────────────────────────────────────────────────────────────
class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['work_order', 'amount', 'tax_type', 'tax_amount', 'total_amount']
        labels = {
            'work_order': 'Work Order',
            'amount': 'Amount',
            'tax_type': 'Tax Type',
            'tax_amount': 'Tax Amount',
            'total_amount': 'Total Amount',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'id': 'amount'}),
            'tax_type': forms.Select(attrs={'id': 'tax_type'}),
            'tax_amount': forms.NumberInput(attrs={'readonly': True, 'id': 'tax_amount'}),
            'total_amount': forms.NumberInput(attrs={'readonly': True, 'id': 'total_amount'}),
        }