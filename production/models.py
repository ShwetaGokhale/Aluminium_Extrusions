from django.db import models, transaction
from django.core.validators import MinValueValidator
from master.models import CompanyPress, CompanyShift
from planning.models import ProductionPlan

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
    
    production_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Production ID"
    )
    date = models.DateField(
        verbose_name="Date",
        null=True,
        blank=True
    )
    production_plan_id = models.ForeignKey(
        'planning.ProductionPlan',
        on_delete=models.CASCADE,
        related_name='production_reports',
        verbose_name="Production Plan ID",
        null=True,
        blank=True
    )
    customer_name = models.CharField(
        max_length=200,
        verbose_name="Customer Name",
        blank=True
    )
    die_requisition_id = models.CharField(
        max_length=100,
        verbose_name="Die Requisition ID",
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
    wt_per_piece = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="WT Per Piece",
        null=True,
        blank=True
    )
    press_no = models.ForeignKey(
        'master.CompanyPress',
        on_delete=models.CASCADE,
        related_name='production_reports',
        verbose_name="Press No"
    )
    date_of_production = models.DateField(
        verbose_name="Date of Production",
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
    
    def save(self, *args, **kwargs):
        if not self.production_id:
            self.production_id = OnlineProductionReport.generate_production_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.production_id} - {self.press_no.name if self.press_no else 'N/A'}"    


# ─────────────────────────────────────────────────────────────────────────────
# Model for Total Production Report functionality
# ─────────────────────────────────────────────────────────────────────────────
class ProductionReport(models.Model):
    date = models.DateField()
    time = models.TimeField()
    press = models.CharField(max_length=50)
    die_no = models.CharField(max_length=50)
    order_no = models.CharField(max_length=50)
    length = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order_no} - {self.press} - {self.die_no}"