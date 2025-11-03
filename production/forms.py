from django import forms
from .models import OnlineProductionReport
from master.models import CompanyPress, CompanyShift, Staff
from planning.models import ProductionPlan


class OnlineProductionReportForm(forms.ModelForm):
    """Form for Online Production Report"""
    
    class Meta:
        model = OnlineProductionReport
        fields = [
            'date',
            'cast_no',
            'press_no',
            'shift',
            'start_time',
            'end_time',
            'operator',
            'production_plan_id',
            'die_no',
            'cut_length',
            'section_no',
            'section_name',
            'wt_per_piece',
            'billet_size',
            'no_of_billet',
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
            'cast_no': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Cast No'
                }
            ),
            'press_no': forms.Select(
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
            'operator': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Operator'
                }
            ),
            'production_plan_id': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Production Plan'
                }
            ),
            'die_no': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Auto-retrieved'
                }
            ),
            'cut_length': forms.TextInput(
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
                    'placeholder': 'Enter WT Per Piece'
                }
            ),
            'billet_size': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter Billet Size'
                }
            ),
            'no_of_billet': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'placeholder': 'Enter No Of Billet'
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
            'cast_no': 'Cast No',
            'press_no': 'Press No',
            'shift': 'Shift',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'operator': 'Operator',
            'production_plan_id': 'Production Plan ID',
            'die_no': 'Die No',
            'cut_length': 'Cut Length',
            'section_no': 'Section No',
            'section_name': 'Section Name',
            'wt_per_piece': 'WT Per Piece',
            'billet_size': 'Billet Size',
            'no_of_billet': 'No Of Billet',
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
        self.fields['cast_no'].required = False
        self.fields['shift'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        self.fields['operator'].required = False
        self.fields['production_plan_id'].required = False
        self.fields['wt_per_piece'].required = False
        self.fields['billet_size'].required = False
        self.fields['no_of_billet'].required = False
        
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