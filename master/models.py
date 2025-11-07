from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.db import models, transaction
from datetime import date
# ------------------------------------------------------------------
# Create your models here.

#─────────────────────────────────────────────────────────────────────────────
# Model for Die Master functionality
#─────────────────────────────────────────────────────────────────────────────
class Die(models.Model):
    """Model for Die management"""
    
    CAVITY_CHOICES = [
        ('One', 'One'),
        ('Two', 'Two'),
        ('Three', 'Three'),
        ('Four', 'Four'),
    ]
    
    MATERIAL_CHOICES = [
        ('SS', 'SS'),
        ('CI', 'CI'),
        ('GI', 'GI'),
    ]
    
    TYPE_CHOICES = [
        ('Dieplate', 'Dieplate'),
        ('Manderel', 'Manderel'),
        ('Backer', 'Backer'),
        ('Feeder', 'Feeder'),
    ]
    
    die_id = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        verbose_name="Die ID"
    )
    date = models.DateField(
        verbose_name="Date", 
        default=timezone.now,
        editable=False,
        null=True, 
        blank=True
    )
    die_no = models.CharField(max_length=100, unique=True, verbose_name="Die No")
    die_name = models.CharField(max_length=200, verbose_name="Die Name", blank=True)
    image = models.ImageField(
        upload_to='die_images/', 
        blank=True, 
        null=True,
        verbose_name="Image"
    )
    
    press = models.ForeignKey(
        'CompanyPress', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='dies',
        verbose_name="Press"
    )
    supplier = models.ForeignKey(
        'Supplier', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='dies',
        verbose_name="Supplier Name"
    )
    project_no = models.CharField(max_length=100, blank=True, verbose_name="Project No")
    date_of_receipt = models.DateField(null=True, blank=True, verbose_name="Date of Receipt")
    no_of_cavity = models.CharField(
        max_length=10, 
        choices=CAVITY_CHOICES,
        verbose_name="No of Cavity",
        blank=True
    )
    req_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Req Weight",
        null=True,
        blank=True
    )
    size = models.CharField(max_length=100, verbose_name="Size", blank=True)
    die_material = models.CharField(
        max_length=10, 
        choices=MATERIAL_CHOICES,
        verbose_name="Die Material",
        blank=True
    )
    hardness = models.CharField(max_length=100, verbose_name="Hardness", blank=True)
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES,
        verbose_name="Type",
        blank=True
    )
    description = models.TextField(blank=True, verbose_name="Description")
    remark = models.TextField(blank=True, verbose_name="Remark")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Die"
        verbose_name_plural = "Dies"
    
    @staticmethod
    def generate_die_id():
        """Generate next Die ID with thread-safe transaction"""
        with transaction.atomic():
            last_die = Die.objects.select_for_update().order_by('-id').first()
            if last_die and last_die.die_id:
                try:
                    last_number = int(last_die.die_id.replace('DIE', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'DIE{str(new_number).zfill(5)}'
    
    def save(self, *args, **kwargs):
        if not self.die_id:
            self.die_id = Die.generate_die_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.die_id} - {self.die_no}"

#─────────────────────────────────────────────────────────────────────────────
# Model for Press functionality
#─────────────────────────────────────────────────────────────────────────────
class Press(models.Model):
    press_name = models.CharField(max_length=100, unique=True, verbose_name="Press Name")
    date_added = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.press_name
    

#─────────────────────────────────────────────────────────────────────────────
# Model for Alloy Harness functionality
#─────────────────────────────────────────────────────────────────────────────
class Alloy(models.Model):
    TEMPER_DESIGNATION_CHOICES = [
        ('Fabricated', 'Fabricated'),
        ('Annealed', 'Annealed'),
        ('Strain Hardened', 'Strain Hardened'),
        ('Solution Heat Treated', 'Solution Heat Treated'),
        ('Thermally Treated', 'Thermally Treated'),
    ]
    
    TEMPER_CODE_CHOICES = [
        ('T1', 'T1'),
        ('T2', 'T2'),
        ('T3', 'T3'),
        ('T4', 'T4'),
        ('T5', 'T5'),
        ('T6', 'T6'),
        ('T7', 'T7'),
        ('T8', 'T8'),
        ('T9', 'T9'),
        ('T10', 'T10'),
    ]
    
    alloy_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Alloy ID"
    )
    date = models.DateField(
        verbose_name="Date",
        default=date.today  # Default to today's date
    )
    alloy_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Alloy Code",
        blank=True,  # Not required
        null=False,
        default=""
    )
    temper_designation = models.CharField(
        max_length=50,
        choices=TEMPER_DESIGNATION_CHOICES,
        verbose_name="Temper Designation",
        blank=True,  # Not required
        null=False,
        default=""
    )
    temper_code = models.CharField(
        max_length=10,
        choices=TEMPER_CODE_CHOICES,
        verbose_name="Temper Code",
        blank=True,  # Not required
        null=False,
        default=""
    )
    tensile_strength = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Tensile Strength",
        blank=True,  # Not required
        null=True  # Allow NULL for decimal fields
    )
    material = models.CharField(
        max_length=255,
        verbose_name="Material",
        blank=True,  # Not required
        null=False,
        default=""
    )
    silicon_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Silicon (%)",
        blank=True,  # Not required
        null=True  # Allow NULL for decimal fields
    )
    copper_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Copper (%)",
        blank=True,  # Not required
        null=True  # Allow NULL for decimal fields
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_alloy_id():
        """Generate next Alloy ID with thread-safe transaction"""
        with transaction.atomic():
            last_alloy = Alloy.objects.select_for_update().order_by('-id').first()
            if last_alloy and last_alloy.alloy_id:
                try:
                    last_number = int(last_alloy.alloy_id.replace('ALY', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'ALY{str(new_number).zfill(5)}'
    
    def save(self, *args, **kwargs):
        if not self.alloy_id:
            self.alloy_id = Alloy.generate_alloy_id()
        # Ensure date is set to today if not provided
        if not self.date:
            self.date = date.today()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.alloy_id} - {self.alloy_code}"
    
    class Meta:
        db_table = 'alloy'
        ordering = ['-created_at']
        verbose_name = "Alloy"
        verbose_name_plural = "Alloys"    

#─────────────────────────────────────────────────────────────────────────────
# Model for LOT functionality
#─────────────────────────────────────────────────────────────────────────────
class Lot(models.Model):
    cast_no = models.CharField(max_length=100, verbose_name="Cost No")
    press_no = models.ForeignKey(Press, on_delete=models.CASCADE, related_name="lots")
    date_of_extrusion = models.DateField(default=timezone.now)
    aging_no = models.CharField(max_length=100, verbose_name="Aging No")
    lot_number = models.CharField(max_length=255, unique=True)  # ✅ auto-generated
    date_added = models.DateField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)

    def generate_lot_number(self):
        return f"{self.cast_no}-{self.press_no.id}-{self.date_of_extrusion.strftime('%Y%m%d')}-{self.aging_no}"

    def save(self, *args, **kwargs):
        if not self.lot_number:
            self.lot_number = self.generate_lot_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.lot_number
    

# ──────────────────────────────────────────────────────────────────────────────
# Model for Profile functionality 
# ──────────────────────────────────────────────────────────────────────────────
class Profile(models.Model):
    # Category field
    category = models.CharField(max_length=100, verbose_name="Category")

    profile_name = models.CharField(max_length=100, unique=True, verbose_name="Profile Name")
    
    section_no = models.CharField(max_length=50, verbose_name="Section No")

    # Size fields in mm
    length_mm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Length (mm)", blank=True, null=True)
    width_mm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Width (mm)", blank=True, null=True)
    thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Thickness (mm)", blank=True, null=True)

    # Weight fields
    WEIGHT_TYPE_CHOICES = [
        ('KG_12', 'kg/12\''),
        ('KG_16', 'kg/16\''),
        ('KG_18', 'kg/18\''),
    ]
    weight_type = models.CharField(max_length=20, choices=WEIGHT_TYPE_CHOICES, verbose_name="Weight Type")
    weight_value = models.CharField(max_length=50, verbose_name="Weight Value")  # Changed from DecimalField to CharField

    shape_image = models.ImageField(upload_to='profile_shapes/', blank=True, null=True, verbose_name="Shape Image")
    date_added = models.DateField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.category} - {self.profile_name}"    
# ──────────────────────────────────────────────────────────────────────────────
# Model for Customer functionality
# ──────────────────────────────────────────────────────────────────────────────
class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('Manufacturer', 'Manufacturer'),
        ('Stockist', 'Stockist'),
        ('Supplier', 'Supplier'),
        ('Bulk Order', 'Ingots'),
        ('Retail', 'Retail'),
    ]
    
    customer_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Customer ID"
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="Date"
    )
    name = models.CharField(max_length=255, blank=True, verbose_name="Name")
    customer_type = models.CharField(
        max_length=50,
        choices=CUSTOMER_TYPE_CHOICES,
        blank=True,
        verbose_name="Customer Type"
    )
    contact_no = models.CharField(max_length=20, blank=True, verbose_name="Contact No")
    contact_person = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Customer Contact Person"
    )
    address = models.TextField(blank=True, verbose_name="Address")
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_customer_id():
        """Generate next Customer ID with thread-safe transaction"""
        with transaction.atomic():
            last_customer = Customer.objects.select_for_update().order_by('-id').first()
            if last_customer and last_customer.customer_id:
                try:
                    last_number = int(last_customer.customer_id.replace('CUS', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'CUS{str(new_number).zfill(4)}'
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer_id = Customer.generate_customer_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer_id} - {self.name}"
    
    class Meta:
        db_table = 'customer'
        ordering = ['-created_at']

# ──────────────────────────────────────────────────────────────────────────────
# Model for Company functionality
# ──────────────────────────────────────────────────────────────────────────────
class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.TextField()
    contact_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


#─────────────────────────────────────────────────────────────────────────────
# Model for Company Shift functionality
#─────────────────────────────────────────────────────────────────────────────
class CompanyShift(models.Model):
    company = models.ForeignKey(Company, related_name='shifts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    timing = models.CharField(max_length=50)  # e.g., "9:00 AM - 5:00 PM"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


#─────────────────────────────────────────────────────────────────────────────
# Model for Company Press functionality
#─────────────────────────────────────────────────────────────────────────────
class CompanyPress(models.Model):
    company = models.ForeignKey(Company, related_name='presses', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    capacity = models.CharField(max_length=50)  # e.g., "500 tons", "1000 kg/hr"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    class Meta:
        verbose_name_plural = "Company Presses"

#─────────────────────────────────────────────────────────────────────────────
# Model for Supplier functionality
#─────────────────────────────────────────────────────────────────────────────
class Supplier(models.Model):
    SUPPLIER_TYPE_CHOICES = [
        ('Die Supplier', 'Die Supplier'),
        ('Raw Material', 'Raw Material'),
        ('Billets', 'Billets'),
        ('Ingots', 'Ingots'),
        ('Parts', 'Parts'),
        ('Service', 'Service'),
    ]
    
    supplier_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Supplier ID"
    )
    date = models.DateField(verbose_name="Date")
    name = models.CharField(max_length=255, verbose_name="Name")
    supplier_type = models.CharField(
        max_length=50,
        choices=SUPPLIER_TYPE_CHOICES,
        verbose_name="Supplier Type"
    )
    contact_no = models.CharField(max_length=20, verbose_name="Contact No")
    contact_person = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Supplier Contact Person"
    )
    address = models.TextField(verbose_name="Address")
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_supplier_id():
        """Generate next Supplier ID with thread-safe transaction"""
        with transaction.atomic():
            last_supplier = Supplier.objects.select_for_update().order_by('-id').first()
            if last_supplier and last_supplier.supplier_id:
                try:
                    last_number = int(last_supplier.supplier_id.replace('SUP', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'SUP{str(new_number).zfill(4)}'
    
    def save(self, *args, **kwargs):
        if not self.supplier_id:
            self.supplier_id = Supplier.generate_supplier_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.supplier_id} - {self.name}"
    
    class Meta:
        db_table = 'supplier'
        ordering = ['-created_at']


#─────────────────────────────────────────────────────────────────────────────
# Model for Staff functionality
#─────────────────────────────────────────────────────────────────────────────
class Staff(models.Model):
    DESIGNATION_CHOICES = [
        ('Worker', 'Worker'),
        ('Machine Operator', 'Machine Operator'),
        ('Supervisor', 'Supervisor'),
        ('Incharge', 'Incharge'),
    ]
    
    SHIFT_CHOICES = [
        ('Morning', 'Morning'),
        ('Night', 'Night'),
    ]
    
    staff_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Staff ID"
    )
    date = models.DateField(verbose_name="Date")
    staff_register_no = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Staff Register No"
    )
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    address = models.TextField(verbose_name="Address")
    contact_no = models.CharField(
        max_length=20,
        verbose_name="Contact No",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Enter a valid contact number"
            )
        ]
    )
    designation = models.CharField(
        max_length=50,
        choices=DESIGNATION_CHOICES,
        verbose_name="Designation"
    )
    shift_assigned = models.CharField(
        max_length=20,
        choices=SHIFT_CHOICES,
        verbose_name="Shift Assigned"
    )
    assigned_to_press = models.ForeignKey(
        'CompanyPress',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members',
        verbose_name="Assigned To Press"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_staff_id():
        """Generate next Staff ID with thread-safe transaction"""
        with transaction.atomic():
            last_staff = Staff.objects.select_for_update().order_by('-id').first()
            if last_staff and last_staff.staff_id:
                try:
                    last_number = int(last_staff.staff_id.replace('STF', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'STF{str(new_number).zfill(4)}'
    
    def save(self, *args, **kwargs):
        if not self.staff_id:
            self.staff_id = Staff.generate_staff_id()
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.staff_id} - {self.get_full_name()}"
    
    class Meta:
        db_table = 'staff'
        ordering = ['-created_at']
        verbose_name = "Staff"
        verbose_name_plural = "Staff"


#─────────────────────────────────────────────────────────────────────────────
# Model for Section functionality
#─────────────────────────────────────────────────────────────────────────────
class Section(models.Model):
    SHAPE_CHOICES = [
        ('T Profile', 'T Profile'),
        ('U Profile', 'U Profile'),
        ('C Profile', 'C Profile'),
        ('H Profile', 'H Profile'),
        ('L Profile', 'L Profile'),
    ]
    
    TYPE_CHOICES = [
        ('Section', 'Section'),
        ('Channel', 'Channel'),
        ('Angle', 'Angle'),
        ('Mesh', 'Mesh'),
        ('Rod', 'Rod'),
    ]
    
    USAGE_CHOICES = [
        ('Industrial', 'Industrial'),
        ('Construction', 'Construction'),
        ('Solar', 'Solar'),
        ('Automobile', 'Automobile'),
    ]
    
    section_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Section ID"
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="Date"
    )
    section_no = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Section No"
    )
    section_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Section Name"
    )
    section_image = models.ImageField(
        upload_to='sections/',
        blank=True,
        null=True,
        verbose_name="Section Image"
    )
    shape = models.CharField(
        max_length=50,
        choices=SHAPE_CHOICES,
        blank=True,
        verbose_name="Shape"
    )
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        blank=True,
        verbose_name="Type"
    )
    usage = models.CharField(
        max_length=50,
        choices=USAGE_CHOICES,
        blank=True,
        verbose_name="Usage"
    )
    length_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Length in mm"
    )
    width_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Width in mm"
    )
    thickness_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Thickness in mm"
    )
    ionized = models.BooleanField(
        default=False,
        verbose_name="Ionized"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def generate_section_id():
        """Generate next Section ID with thread-safe transaction"""
        with transaction.atomic():
            last_section = Section.objects.select_for_update().order_by('-id').first()
            if last_section and last_section.section_id:
                try:
                    last_number = int(last_section.section_id.replace('SEC', ''))
                    new_number = last_number + 1
                except (ValueError, AttributeError):
                    new_number = 1
            else:
                new_number = 1
            return f'SEC{str(new_number).zfill(5)}'
    
    def save(self, *args, **kwargs):
        if not self.section_id:
            self.section_id = Section.generate_section_id()
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.section_id} - {self.section_name}"
    
    class Meta:
        db_table = 'section'
        ordering = ['-created_at']
        verbose_name = "Section"
        verbose_name_plural = "Sections"