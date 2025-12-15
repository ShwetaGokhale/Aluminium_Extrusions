from django import forms
from .models import OnlineProductionReport
from master.models import CompanyPress, CompanyShift, Staff
from planning.models import ProductionPlan, DieRequisition
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
            'date_of_production',
            'die_requisition',
            'die_no',
            'section_no',
            'section_name',
            'wt_per_piece_general',
            'no_of_cavity',
            'cut_length',
            'press',
            'shift',
            'operator',
            'planned_qty',
            'start_time',
            'end_time',
            'billet_size',
            'no_of_billet',
            'weight',
            'input_qty',
            'wt_per_piece_output',
            'no_of_pieces',
            'status'
        ]
        
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Select Date',
                    'required': True
                }
            ),
            'date_of_production': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Select Date of Production',
                    'required': True
                }
            ),
            'die_requisition': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Die Requisition',
                    'required': True
                }
            ),
            'die_no': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Die No'
                }
            ),
            'section_no': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Section No'
                }
            ),
            'section_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Section Name'
                }
            ),
            'wt_per_piece_general': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'WT per Piece'
                }
            ),
            'no_of_cavity': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'No of Cavity'
                }
            ),
            'cut_length': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Cut Length'
                }
            ),
            'press': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Press',
                    'required': True
                }
            ),
            'shift': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Shift'
                }
            ),
            'operator': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Operator'
                }
            ),
            'planned_qty': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'placeholder': 'Planned QTY'
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
            'billet_size': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Billet Size (mm)'
                }
            ),
            'no_of_billet': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'placeholder': 'No of Billet'
                }
            ),
            'weight': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Weight (Auto-calculated)',
                    'readonly': True
                }
            ),
            'input_qty': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Input Quantity (Auto-calculated)',
                    'readonly': True
                }
            ),
            'wt_per_piece_output': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'WT per Piece'
                }
            ),
            'no_of_pieces': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'placeholder': 'No of Pieces'
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
            'date_of_production': 'Date of Production',
            'die_requisition': 'Die Requisition ID',
            'die_no': 'Die No',
            'section_no': 'Section No',
            'section_name': 'Section Name',
            'wt_per_piece_general': 'WT per Piece',
            'no_of_cavity': 'No of Cavity',
            'cut_length': 'Cut Length',
            'press': 'Press',
            'shift': 'Shift',
            'operator': 'Operator',
            'planned_qty': 'Planned QTY',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'billet_size': 'Billet Size (mm)',
            'no_of_billet': 'No of Billet',
            'weight': 'Weight (Auto-calculated)',
            'input_qty': 'Input (Auto-calculated)',
            'wt_per_piece_output': 'WT per Piece',
            'no_of_pieces': 'No of Pieces',
            'status': 'Status'
        }
    
    def __init__(self, *args, **kwargs):
        super(OnlineProductionReportForm, self).__init__(*args, **kwargs)
        
        # Set today's date as default for new forms
        if not self.instance.pk:
            from datetime import date
            self.initial['date'] = date.today()
            self.initial['status'] = 'in_progress'
        
        # Set required fields
        self.fields['date'].required = True
        self.fields['date_of_production'].required = True
        self.fields['die_requisition'].required = True
        self.fields['press'].required = True
        self.fields['status'].required = True
        
        # Set optional fields
        self.fields['die_no'].required = False
        self.fields['section_no'].required = False
        self.fields['section_name'].required = False
        self.fields['wt_per_piece_general'].required = False
        self.fields['no_of_cavity'].required = False
        self.fields['cut_length'].required = False
        self.fields['shift'].required = False
        self.fields['operator'].required = False
        self.fields['planned_qty'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        self.fields['billet_size'].required = False
        self.fields['no_of_billet'].required = False
        self.fields['weight'].required = False
        self.fields['input_qty'].required = False
        self.fields['wt_per_piece_output'].required = False
        self.fields['no_of_pieces'].required = False
        
        # Set queryset for dropdowns
        self.fields['press'].queryset = CompanyPress.objects.all().order_by('name')
        self.fields['shift'].queryset = CompanyShift.objects.all().order_by('name')
        self.fields['operator'].queryset = Staff.objects.all().order_by('first_name')
        self.fields['die_requisition'].queryset = DieRequisition.objects.all().order_by('-created_at')
        
        # Customize empty labels
        self.fields['press'].empty_label = "Select Press"
        self.fields['shift'].empty_label = "Select Shift"
        self.fields['operator'].empty_label = "Select Operator"
        self.fields['die_requisition'].empty_label = "Select Date of Production First"
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        date_of_production = cleaned_data.get('date_of_production')
        die_requisition = cleaned_data.get('die_requisition')
        press = cleaned_data.get('press')
        
        # Validate required fields
        if not date:
            raise forms.ValidationError("Date is required.")
        
        if not date_of_production:
            raise forms.ValidationError("Date of Production is required.")
        
        if not die_requisition:
            raise forms.ValidationError("Die Requisition ID is required.")
        
        if not press:
            raise forms.ValidationError("Press is required.")
        
        # Validate that end_time is after start_time if both are provided
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError(
                    "End time must be after start time."
                )
        
        # Validate date_of_production is not in the future
        from datetime import date as dt_date
        if date_of_production and date_of_production > dt_date.today():
            raise forms.ValidationError(
                "Date of Production cannot be in the future."
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # The total_output will be automatically calculated in the model's save method
        
        if commit:
            instance.save()
        return instance

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