from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class School(models.Model):

    login_id = models.ForeignKey(User,on_delete=models.CASCADE)

    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
# Contact Info
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

# Address Info
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

# School Details
    # established_year = models.PositiveIntegerField(null=True, blank=True)
    # board = models.CharField(max_length=100, null=True, blank=True)
    # website = models.URLField(null=True, blank=True)

# Admin Info
    # principal_name = models.CharField(max_length=255, null=True, blank=True)
    # total_students = models.PositiveIntegerField(null=True, blank=True)
    # total_teachers = models.PositiveIntegerField(null=True, blank=True)

# Status & Timestamps
    is_active = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name
    

    
class Staff(models.Model):

    STAFF_CATEGORIES = [
        ('TEACHER', 'Teacher'),
        ('CLERK', 'Clerk'),
        ('LIBRARIAN', 'Librarian'),
        ('FEE MANAGEMENT', 'Fee Management '),
        ('PRINCIPAL', 'Principal'),
        ('TRANSOPORTATION', 'Transportation '),
        ('INVENTORY', 'Inventory '),
        
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    category = models.CharField(max_length=20, choices=STAFF_CATEGORIES, default='OTHER')

    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


import uuid


class AdmissionForm(models.Model):
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='admission_forms')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    fees_enable = models.BooleanField(default=False)
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True , blank=True)
    
    unique_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.school.name}"
    
class FormSection(models.Model):
    form = models.ForeignKey(
        'AdmissionForm',
        on_delete=models.CASCADE,
        related_name='sections'
    )

    title = models.CharField(max_length=255)  # e.g. "Personal Details"
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.title
    
    

class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('file', 'File'),
        ('date', 'Date'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
    ]

    section = models.ForeignKey(
        'FormSection',
        on_delete=models.CASCADE,
        related_name='fields'
    )

    label = models.CharField(max_length=255)  # e.g., "Student Name"
    
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPES
    )

    is_required = models.BooleanField(default=False)

    options = models.JSONField(blank=True, null=True)  
    # Example: ["A", "B", "C"]

    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.label} ({self.field_type})"
    
class Student(models.Model):
    # Status
    form = models.ForeignKey('AdmissionForm',on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    form_filled = models.BooleanField(default=False)

    #verified field
    principle_verified = models.BooleanField(default=False)
    fees_verified = models.BooleanField(default=False)
    clerk_verified = models.BooleanField(default=False)
    
    principle_verified_at = models.DateTimeField(null=True, blank=True)
    clerk_verified_at = models.DateTimeField(null=True, blank=True)
    fees_verified_at = models.DateTimeField(null=True, blank=True)

    gr_no =  models.CharField(max_length=100, default=None,blank=True, null=True)

    


class StudentFieldValue(models.Model):
    student = models.ForeignKey(
        'Student',   # renamed from Student
        on_delete=models.CASCADE,
        related_name='field_values'
    )
    

    field = models.ForeignKey(
        'FormField',
        on_delete=models.CASCADE,
        related_name='values'
    )

    value = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='student_files/', blank=True, null=True)

    def __str__(self):
        return f"{self.student.email} - {self.field.label}"


class AdmissionFee(models.Model):
    # student = models.ForeignKey("Student", on_delete=models.CASCADE)
    
    # Amount details
    amount = models.IntegerField()  # in rupees
    currency = models.CharField(max_length=10, default="INR")

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ("created", "Created"),
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")

    # # Extra useful fields
    # receipt_id = models.CharField(max_length=255, blank=True, null=True)
    # payment_method = models.CharField(max_length=50, blank=True, null=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)