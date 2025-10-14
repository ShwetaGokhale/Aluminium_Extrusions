from django.db import models
from django.utils import timezone
from master.models import *   # import model from Master app

# Create your models here.

#─────────────────────────────────────────────────────────────────────────────
# Model for Requisition functionality
#─────────────────────────────────────────────────────────────────────────────
class Requisition(models.Model):
    requisition_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Customer Requisition ID"
    )
    date = models.DateField(verbose_name="Date")
    requisition_no = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Customer Requisition No"
    )
    customer = models.ForeignKey(
        "master.Customer",
        on_delete=models.CASCADE,
        verbose_name="Customer"
    )
    contact_no = models.CharField(
        max_length=20,
        verbose_name="Contact No"
    )
    address = models.TextField(verbose_name="Address")
    sales_manager = models.ForeignKey(
        "master.Staff",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Sales Manager"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Expiry Date"
    )
    dispatch_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Dispatch Date"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_requisition_id():
        """Generate next Requisition ID with thread-safe transaction"""
        with transaction.atomic():
            last_req = Requisition.objects.select_for_update().order_by('-id').first()
            if last_req and last_req.requisition_id:
                try:
                    last_number = int(last_req.requisition_id.replace('REQ', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'REQ{str(new_number).zfill(5)}'

    def save(self, *args, **kwargs):
        if not self.requisition_id:
            self.requisition_id = Requisition.generate_requisition_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.requisition_id} - {self.requisition_no}"

    class Meta:
        db_table = 'requisition'
        ordering = ['-created_at']
        verbose_name = "Customer Requisition"
        verbose_name_plural = "Customer Requisitions"

    
#─────────────────────────────────────────────────────────────────────────────
# Model for Requisition's Order functionality
#─────────────────────────────────────────────────────────────────────────────
class RequisitionOrder(models.Model):
    CUT_LENGTH_CHOICES = [
        ('12ft', '12 ft'),
        ('16ft', '16 ft'),
        ('18ft', '18 ft'),
    ]

    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Requisition"
    )
    section_no = models.ForeignKey(
        "master.Section",
        on_delete=models.CASCADE,
        related_name='requisition_orders',
        verbose_name="Section No"
    )
    wt_range = models.CharField(
        max_length=50,
        verbose_name="WT Range"
    )
    cut_length = models.CharField(
        max_length=10,
        choices=CUT_LENGTH_CHOICES,
        verbose_name="Cut Length"
    )
    qty_in_no = models.IntegerField(
        verbose_name="QTY in No"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requisition.requisition_id} - {self.section_no.section_no}"

    class Meta:
        db_table = 'requisition_order'
        ordering = ['id']
        verbose_name = "Requisition Order"
        verbose_name_plural = "Requisition Orders"    

#─────────────────────────────────────────────────────────────────────────────
# Model for Work Order functionality
#─────────────────────────────────────────────────────────────────────────────
class WorkOrder(models.Model):
    PAYMENT_TERM_CHOICES = [
        ('30', '30 Days'),
        ('45', '45 Days'),
        ('60', '60 Days'),
        ('90', '90 Days'),
    ]

    id = models.AutoField(primary_key=True, unique=True)
    customer = models.ForeignKey("master.Customer", on_delete=models.CASCADE)
    contact_no = models.CharField(max_length=15)
    address = models.TextField()
    sales_manager = models.CharField(max_length=100)
    payment_terms = models.CharField(max_length=2, choices=PAYMENT_TERM_CHOICES)
    delivery_date = models.DateField()
    dispatch_date = models.DateField()
    expiry_date = models.DateField()
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Work Order for {self.customer}"


#─────────────────────────────────────────────────────────────────────────────
# Model for Work Order's Goods functionality
#─────────────────────────────────────────────────────────────────────────────
class WorkOrderGoods(models.Model):
    id = models.AutoField(primary_key=True, unique=True)

    # Link to WorkOrder
    work_order = models.ForeignKey(
        "WorkOrder",
        on_delete=models.CASCADE,
        related_name="goods_items",
        null=True,
        blank=True
    )

    # Section No from Profile model
    section_no = models.ForeignKey(
        "master.Profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Section No"
    )

    wt_range = models.CharField(
        max_length=100,
        verbose_name="Weight Range",
        null=True,
        blank=True
    )
    cut_length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Cut Length",
        null=True,
        blank=True
    )

    # Alloy temper from Alloy model
    alloy_temper = models.ForeignKey(
        "master.Alloy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Alloy Temper"
    )

    pack = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pack")
    qty = models.IntegerField(null=True, blank=True, verbose_name="Quantity")
    total_pack = models.IntegerField(null=True, blank=True, verbose_name="Total Pack")
    total_no = models.IntegerField(null=True, blank=True, verbose_name="Total No")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Amount")

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Goods ID: {self.id} (WorkOrder: {self.work_order.id if self.work_order else 'N/A'})"


#─────────────────────────────────────────────────────────────────────────────
# Model for Finance functionality
#─────────────────────────────────────────────────────────────────────────────
class Finance(models.Model):
    TAX_CHOICES = [
        ('SGST', 'SGST'),
        ('CGST', 'CGST'),
        ('IGST', 'IGST'),
    ]

    id = models.AutoField(primary_key=True, unique=True)
    work_order = models.ForeignKey(
        "WorkOrder",
        on_delete=models.CASCADE,
        related_name="finance_entries",
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")
    tax_type = models.CharField(max_length=4, choices=TAX_CHOICES, verbose_name="Tax Type")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Tax Amount")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total Amount")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Finance ID: {self.id} (WorkOrder: {self.work_order.id if self.work_order else 'N/A'})"

    def save(self, *args, **kwargs):
        if self.tax_type in ['SGST', 'CGST']:
            self.tax_amount = self.amount * 0.08  # 8%
        elif self.tax_type == 'IGST':
            self.tax_amount = self.amount * 0.18  # 18%
        else:
            self.tax_amount = 0

        self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)
