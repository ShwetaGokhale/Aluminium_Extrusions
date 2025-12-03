from django import forms
from .models import OnlineProductionReport
from master.models import CompanyPress, CompanyShift, Staff
from planning.models import ProductionPlan
from .models import ProductionReport

# ─────────────────────────────────────────────────────────────────────────────
# Form for Online Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class OnlineProductionReportForm(forms.ModelForm):
    """Form for Online Production Report"""
    
    class Meta:
        model = OnlineProductionReport
        fields = [
            'date',
            'production_plan_id',
            'customer_name',
            'die_requisition_id',
            'die_no',
            'section_no',
            'section_name',
            'wt_per_piece',
            'press_no',
            'date_of_production',
            'shift',
            'operator',
            'planned_qty',
            'start_time',
            'end_time',
            'status'
        ]
        
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Select Date'
                }
            ),
            'production_plan_id': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Production Plan'
                }
            ),
            'customer_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'die_requisition_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'die_no': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'section_no': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'section_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'wt_per_piece': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'press_no': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Press',
                    'required': True,
                    'style': 'background-color: #f0f0f0;'
                }
            ),
            'date_of_production': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'shift': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Shift',
                    'style': 'background-color: #f0f0f0;'
                }
            ),
            'operator': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Operator',
                    'style': 'background-color: #f0f0f0;'
                }
            ),
            'planned_qty': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'start_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'placeholder': 'Start Time'
                }
            ),
            'end_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'placeholder': 'End Time'
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-control',
                    'required': True
                }
            )
        }
        
        labels = {
            'date': 'Date',
            'production_plan_id': 'Production Plan ID',
            'customer_name': 'Customer Name',
            'die_requisition_id': 'Die Requisition ID',
            'die_no': 'Die No',
            'section_no': 'Section No',
            'section_name': 'Section Name',
            'wt_per_piece': 'WT Per Piece',
            'press_no': 'Press',
            'date_of_production': 'Date of Production',
            'shift': 'Shift',
            'operator': 'Operator',
            'planned_qty': 'Planned QTY',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'status': 'Status'
        }
    
    def __init__(self, *args, **kwargs):
        super(OnlineProductionReportForm, self).__init__(*args, **kwargs)
        
        # Set today's date as default for new forms
        if not self.instance.pk:
            from datetime import date
            self.initial['date'] = date.today()
            self.initial['status'] = 'in_progress'
        
        # Make press_no required, others optional
        self.fields['press_no'].required = True
        self.fields['date'].required = False
        self.fields['production_plan_id'].required = False
        self.fields['customer_name'].required = False
        self.fields['die_requisition_id'].required = False
        self.fields['die_no'].required = False
        self.fields['section_no'].required = False
        self.fields['section_name'].required = False
        self.fields['wt_per_piece'].required = False
        self.fields['date_of_production'].required = False
        self.fields['shift'].required = False
        self.fields['operator'].required = False
        self.fields['planned_qty'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        
        # Set queryset for dropdowns
        self.fields['press_no'].queryset = CompanyPress.objects.all().order_by('name')
        self.fields['shift'].queryset = CompanyShift.objects.all().order_by('name')
        self.fields['operator'].queryset = Staff.objects.all().order_by('first_name')
        self.fields['production_plan_id'].queryset = ProductionPlan.objects.all().order_by('-created_at')
        
        # Customize empty label
        self.fields['press_no'].empty_label = "Select Press"
        self.fields['shift'].empty_label = "Select Shift"
        self.fields['operator'].empty_label = "Select Operator"
        self.fields['production_plan_id'].empty_label = "Select Production Plan"
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Validate that end_time is after start_time if both are provided
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError(
                    "End time must be after start time."
                )
        
        return cleaned_data    

# ─────────────────────────────────────────────────────────────────────────────
# Forms for Total Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class ProductionFilterForm(forms.Form):
    order_no = forms.ChoiceField(choices=[], required=True)
    press = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_no'].choices = [('', 'Select Order No')] + list(
            ProductionReport.objects.values_list('order_no', 'order_no').distinct()
        )
        self.fields['press'].choices = [('', 'Select Press')] + list(
            ProductionReport.objects.values_list('press', 'press').distinct()
        )