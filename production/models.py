from django.db import models, transaction
from django.core.validators import MinValueValidator
from master.models import CompanyPress, CompanyShift
from planning.models import ProductionPlan
from django.utils import timezone

# ─────────────────────────────────────────────────────────────────────────────
# Model for Online Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class OnlineProductionReport(models.Model):
    """Model for Online Production Report management"""
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    # ============ General Section ============
    production_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Production ID"
    )
    date = models.DateField(
        verbose_name="Date",
        default=timezone.now
    )
    date_of_production = models.DateField(
        verbose_name="Date of Production",
        null=True,
        blank=True
    )
    die_requisition = models.ForeignKey(
        'planning.DieRequisition',
        on_delete=models.CASCADE,
        related_name='production_reports',
        verbose_name="Die Requisition ID",
        null=True,
        blank=True
    )
    die_no = models.CharField(
        max_length=100,
        verbose_name="Die No",
        blank=True
    )
    section_no = models.CharField(
        max_length=100,
        verbose_name="Section No",
        blank=True
    )
    section_name = models.CharField(
        max_length=200,
        verbose_name="Section Name",
        blank=True
    )
    wt_per_piece_general = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="WT Per Piece (General)",
        null=True,
        blank=True
    )
    no_of_cavity = models.CharField(
        max_length=10,
        verbose_name="No of Cavity",
        blank=True
    )
    cut_length = models.CharField(
        max_length=10,
        verbose_name="Cut Length",
        blank=True
    )
    press = models.ForeignKey(
        'master.CompanyPress',
        on_delete=models.CASCADE,
        related_name='production_reports',
        verbose_name="Press",
        null=True,
        blank=True
    )
    shift = models.ForeignKey(
        'master.CompanyShift',
        on_delete=models.CASCADE,
        related_name='production_reports',
        verbose_name="Shift",
        null=True,
        blank=True
    )
    operator = models.ForeignKey(
        'master.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='production_reports',
        verbose_name="Operator"
    )
    planned_qty = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Planned QTY",
        null=True,
        blank=True
    )
    
    # ============ Production Time Details ============
    start_time = models.TimeField(
        verbose_name="Start Time",
        null=True,
        blank=True
    )
    end_time = models.TimeField(
        verbose_name="End Time",
        null=True,
        blank=True
    )
    
    # ============ Production Input Details ============
    billet_size = models.CharField(
        max_length=50,
        verbose_name="Billet Size (mm)",
        blank=True
    )
    no_of_billet = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="No of Billet",
        null=True,
        blank=True
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Weight",
        null=True,
        blank=True
    )
    input_qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Input",
        null=True,
        blank=True
    )
    
    # ============ Production Output Details ============
    wt_per_piece_output = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="WT per Piece (Output)",
        null=True,
        blank=True
    )
    no_of_pieces = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="No of Pieces",
        null=True,
        blank=True
    )
    total_output = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total Output",
        null=True,
        blank=True,
        editable=False
    )
    
    # ============ Status ============
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name="Status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'online_production_report'
        ordering = ['-created_at']
        verbose_name = "Online Production Report"
        verbose_name_plural = "Online Production Reports"
    
    @staticmethod
    def generate_production_id():
        """Generate next Production ID with thread-safe transaction"""
        with transaction.atomic():
            last_report = OnlineProductionReport.objects.select_for_update().order_by('-id').first()
            if last_report and last_report.production_id:
                try:
                    last_number = int(last_report.production_id.replace('PRD', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'PRD{str(new_number).zfill(4)}'
    
    def calculate_total_output(self):
        """Calculate total output based on wt_per_piece_output and no_of_pieces"""
        if self.wt_per_piece_output and self.no_of_pieces:
            return self.wt_per_piece_output * self.no_of_pieces
        return None
    
    def save(self, *args, **kwargs):
        if not self.production_id:
            self.production_id = OnlineProductionReport.generate_production_id()
        
        # Auto-calculate total output
        self.total_output = self.calculate_total_output()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.production_id} - {self.press.name if self.press else 'N/A'}"

# ─────────────────────────────────────────────────────────────────────────────
# Model for Daily Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class DailyProductionReport(models.Model):
    """Model for Daily Production Report management"""
    
    # ============ General Section ============
    report_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Report ID"
    )
    date = models.DateField(
        verbose_name="Date",
        default=timezone.now
    )
    online_production_report = models.ForeignKey(
        'production.OnlineProductionReport',
        on_delete=models.CASCADE,
        related_name='daily_reports',
        verbose_name="Die No",
        null=True,
        blank=True
    )
    
    # Auto-populated fields from OnlineProductionReport
    die_no = models.CharField(
        max_length=100,
        verbose_name="Die No",
        blank=True
    )
    section_no = models.CharField(
        max_length=100,
        verbose_name="Section No",
        blank=True
    )
    section_name = models.CharField(
        max_length=200,
        verbose_name="Section Name",
        blank=True
    )
    cavity = models.CharField(
        max_length=10,
        verbose_name="Cavity",
        blank=True
    )
    start_time = models.TimeField(
        verbose_name="Start Time",
        null=True,
        blank=True
    )
    end_time = models.TimeField(
        verbose_name="End Time",
        null=True,
        blank=True
    )
    billet_size = models.CharField(
        max_length=50,
        verbose_name="Billet Size (mm)",
        blank=True
    )
    no_of_billet = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="No of Billet",
        null=True,
        blank=True
    )
    input_qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Input",
        null=True,
        blank=True
    )
    cut_length = models.CharField(
        max_length=10,
        verbose_name="Cut Length",
        blank=True
    )
    wt_per_piece = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="WT per Piece",
        null=True,
        blank=True
    )
    no_of_ok_pcs = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="No of OK PCS",
        null=True,
        blank=True
    )
    output = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Output",
        null=True,
        blank=True
    )
    
    # Calculated fields
    recovery = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Recovery (%)",
        null=True,
        blank=True,
        editable=False
    )
    nop_bp = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="NOP BP",
        null=True,
        blank=True
    )
    nop_ba = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="NOP BA",
        null=True,
        blank=True
    )
    nrt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="NRT (Hours)",
        null=True,
        blank=True,
        editable=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_production_report'
        ordering = ['-created_at']
        verbose_name = "Daily Production Report"
        verbose_name_plural = "Daily Production Reports"
    
    @staticmethod
    def generate_report_id():
        """Generate next Report ID with thread-safe transaction"""
        with transaction.atomic():
            last_report = DailyProductionReport.objects.select_for_update().order_by('-id').first()
            if last_report and last_report.report_id:
                try:
                    last_number = int(last_report.report_id.replace('DPR', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'DPR{str(new_number).zfill(5)}'
    
    def calculate_recovery(self):
        """Calculate recovery percentage: (output / input) * 100"""
        if self.input_qty and self.output and self.input_qty > 0:
            return (self.output / self.input_qty) * 100
        return None
    
    def calculate_nrt(self):
        """Calculate NRT (Net Run Time) in hours: end_time - start_time"""
        if self.start_time and self.end_time:
            from datetime import datetime, timedelta
            
            start = datetime.combine(datetime.today(), self.start_time)
            end = datetime.combine(datetime.today(), self.end_time)
            
            # Handle case where end time is on next day
            if end < start:
                end += timedelta(days=1)
            
            time_diff = end - start
            hours = time_diff.total_seconds() / 3600
            return round(hours, 2)
        return None
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = DailyProductionReport.generate_report_id()
        
        # Auto-calculate recovery and NRT
        self.recovery = self.calculate_recovery()
        self.nrt = self.calculate_nrt()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.report_id} - {self.die_no or 'N/A'}"
    










# class ProductionReport(models.Model):
#     date = models.DateField()
#     time = models.TimeField()
#     press = models.CharField(max_length=50)
#     die_no = models.CharField(max_length=50)
#     order_no = models.CharField(max_length=50)
#     length = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.order_no} - {self.press} - {self.die_no}"