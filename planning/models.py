from django.db import models
from django.db import models, transaction
from django.core.validators import MinValueValidator
from master.models import *   # import model from Master app
from order_management.models import *


# Create your models here.

#─────────────────────────────────────────────────────────────────────────────
# Model for Die Requisition functionality
#─────────────────────────────────────────────────────────────────────────────
class DieRequisition(models.Model):
    """Model for Die Requisition management"""
    CUT_LENGTH_CHOICES = [
        ('12ft', '12 ft'),
        ('16ft', '16 ft'),
        ('18ft', '18 ft'),
    ]
    
    die_requisition_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Die Requisition ID"
    )
    date = models.DateField(verbose_name="Date")
    customer_requisition_no = models.ForeignKey(
        'order_management.Requisition',
        on_delete=models.CASCADE,
        related_name='die_requisitions',
        verbose_name="Customer Requisition No"
    )
    section_no = models.ForeignKey(
        'master.Section',
        on_delete=models.CASCADE,
        related_name='die_requisitions',
        verbose_name="Section No"
    )
    section_name = models.CharField(
        max_length=200,
        verbose_name="Section Name"
    )
    wt_range = models.CharField(
        max_length=50,
        verbose_name="WT Range"
    )
    die_no = models.ForeignKey(
        'master.Die',
        on_delete=models.CASCADE,
        related_name='die_requisitions',
        verbose_name="Die No"
    )
    die_name = models.CharField(
        max_length=200,
        verbose_name="Die Name"
    )
    present_wt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Present WT"
    )
    no_of_cavity = models.CharField(
        max_length=10,
        verbose_name="No of Cavity"
    )
    cut_length = models.CharField(
        max_length=10,
        choices=CUT_LENGTH_CHOICES,
        blank=True,
        null=True,
        verbose_name="Cut Length"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'die_requisition'
        ordering = ['-created_at']
        verbose_name = "Die Requisition"
        verbose_name_plural = "Die Requisitions"
    
    @staticmethod
    def generate_die_requisition_id():
        """Generate next Die Requisition ID with thread-safe transaction"""
        with transaction.atomic():
            last_req = DieRequisition.objects.select_for_update().order_by('-id').first()
            if last_req and last_req.die_requisition_id:
                try:
                    last_number = int(last_req.die_requisition_id.replace('DRQ', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'DRQ{str(new_number).zfill(5)}'
    
    def save(self, *args, **kwargs):
        if not self.die_requisition_id:
            self.die_requisition_id = DieRequisition.generate_die_requisition_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.die_requisition_id} - {self.customer_requisition_no.requisition_no}"


# ──────────────────────────────────────────────────────────────────────────────
# Model for Production Planning functionality
# ──────────────────────────────────────────────────────────────────────────────
class ProductionPlan(models.Model):
    """Model for Production Planning management"""
    
    production_plan_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Production Plan ID"
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="Date"
    )
    cust_requisition_id = models.ForeignKey(
        'order_management.Requisition',
        on_delete=models.CASCADE,
        related_name='production_plans',
        verbose_name="Cust Requisition ID",
        null=True,
        blank=True
    )
    customer_name = models.CharField(
        max_length=200,
        verbose_name="Customer Name",
        blank=True
    )
    die_requisition = models.ForeignKey(
        'planning.DieRequisition',
        on_delete=models.CASCADE,
        related_name='production_plans',
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
        max_length=50,
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
        verbose_name="WT per Piece",
        default=0
    )
    # NEW FIELDS
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
    
    # Production Planning Details
    press = models.ForeignKey(
        'master.CompanyPress',
        on_delete=models.CASCADE,
        related_name='production_plans',
        verbose_name="Press"
    )
    date_of_production = models.DateField(
        verbose_name="Date of Production",
        null=True,
        blank=True
    )
    shift = models.ForeignKey(
        'master.CompanyShift',
        on_delete=models.CASCADE,
        related_name='production_plans',
        verbose_name="Shift",
        null=True,
        blank=True
    )
    operator = models.ForeignKey(
        'master.Staff',
        on_delete=models.SET_NULL,
        related_name='production_plans',
        verbose_name="Operator",
        null=True,
        blank=True
    )
    planned_qty = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Planned QTY",
        null=True,
        blank=True
    )
    
    # Billet Planning Details
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'production_plan'
        ordering = ['-created_at']
        verbose_name = "Production Plan"
        verbose_name_plural = "Production Plans"
    
    @staticmethod
    def generate_production_plan_id():
        """Generate next Production Plan ID with thread-safe transaction"""
        with transaction.atomic():
            last_plan = ProductionPlan.objects.select_for_update().order_by('-id').first()
            if last_plan and last_plan.production_plan_id:
                try:
                    last_number = int(last_plan.production_plan_id.replace('PDP', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'PDP{str(new_number).zfill(5)}'
    
    def save(self, *args, **kwargs):
        if not self.production_plan_id:
            self.production_plan_id = ProductionPlan.generate_production_plan_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.production_plan_id} - {self.customer_name}"