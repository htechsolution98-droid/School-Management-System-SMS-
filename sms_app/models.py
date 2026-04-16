from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

from django.conf import settings


class School(models.Model):

    login_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schools"
    )

    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    is_active = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, related_name="users"
    )


class Staff(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    STAFF_CATEGORIES = [
        ("TEACHER", "Teacher"),
        ("CLERK", "Clerk"),
        ("LIBRARIAN", "Librarian"),
        ("FEE MANAGEMENT", "Fee Management "),
        ("PRINCIPAL", "Principal"),
        ("TRANSOPORTATION", "Transportation "),
        ("INVENTORY", "Inventory "),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    category = models.CharField(
        max_length=20, choices=STAFF_CATEGORIES, default="OTHER"
    )

    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class SchoolClass(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    CLASS_CHOICES = [
        ("nursery", "Nursery"),
        ("lkg", "LKG"),
        ("ukg", "UKG"),
        ("class1", "Class 1"),
        ("class2", "Class 2"),
        ("class3", "Class 3"),
        ("class4", "Class 4"),
        ("class5", "Class 5"),
        ("class6", "Class 6"),
        ("class7", "Class 7"),
        ("class8", "Class 8"),
        ("class9_basic", "Class 9 Basic Math"),
        ("class9_standard", "Class 9 Standard Math"),
        ("class9_advanced", "Class 9 Advanced Math"),
        ("class10_basic", "Class 10 Basic Math"),
        ("class10_standard", "Class 10 Standard Math"),
        ("class10_advanced", "Class 10 Advanced Math"),
        # Streams after 10
        ("class11_science", "Class 11 Science"),
        ("class11_arts", "Class 11 Arts"),
        ("class11_commerce", "Class 11 Commerce"),
        ("class12_science", "Class 12 Science"),
        ("class12_arts", "Class 12 Arts"),
        ("class12_commerce", "Class 12 Commerce"),
    ]

    school_class = models.CharField(max_length=70, choices=CLASS_CHOICES)

    def __str__(self):
        return self.school_class


class Division(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    SchoolClass = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    division = models.CharField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.SchoolClass} ({self.division})"


class AdmissionForm(models.Model):
    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        related_name="admission_forms",
        db_index=True,
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=False)
    fees_enable = models.BooleanField(default=False)

    FEE_TYPE_CHOICES = (
        ("general", "General"),
        ("individual", "Individual"),
    )

    fee_type = models.CharField(
        max_length=20, choices=FEE_TYPE_CHOICES, null=True, blank=True
    )
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    unique_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.school.name}"


class AdmissionFeeStructure(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    admission_form = models.ForeignKey(
        AdmissionForm, on_delete=models.CASCADE, related_name="fee_structures"
    )
    class_name = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, null=True, blank=True
    )
    fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.class_name} - {self.fee_amount}"


class FormSection(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    form = models.ForeignKey(
        "AdmissionForm", on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class FormField(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        # ('file', 'File'),
        ("date", "Date"),
        ("select", "Select"),
        ("checkbox", "Checkbox"),
        ("radio", "Radio"),
    ]

    section = models.ForeignKey(
        "FormSection", on_delete=models.CASCADE, related_name="fields"
    )
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=False)
    options = models.JSONField(blank=True, null=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.label} ({self.field_type})"


class Student(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    form = models.ForeignKey("AdmissionForm", on_delete=models.CASCADE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    mobile = models.CharField(max_length=12, null=True, blank=True)

    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, null=True, blank=True
    )
    division = models.CharField(max_length=20, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    details_done = models.BooleanField(default=False)

    principle_verified = models.BooleanField(default=False)
    fees_verified = models.BooleanField(default=False)
    clerk_verified = models.BooleanField(default=False)

    principle_verified_at = models.DateTimeField(null=True, blank=True)
    clerk_verified_at = models.DateTimeField(null=True, blank=True)
    fees_verified_at = models.DateTimeField(null=True, blank=True)

    gr_no = models.CharField(max_length=100, default=None, blank=True, null=True)


class Perents(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    perents_of = models.ForeignKey(Student, on_delete=models.CASCADE)


class StudentFieldValue(models.Model):
    form_id = models.ForeignKey(
        AdmissionForm, on_delete=models.CASCADE, null=True, blank=True
    )
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    student = models.ForeignKey(
        "Student", on_delete=models.CASCADE, related_name="field_values"
    )
    field = models.ForeignKey(
        "FormField", on_delete=models.CASCADE, related_name="values"
    )

    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.field.label}"


class DocumentField(models.Model):
    form_id = models.ForeignKey(
        "AdmissionForm",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="label",
    )

    school = models.ForeignKey(
        "School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="document_fields",  # changed
    )

    label = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label if self.label else "Student Document"


class DocumentFile(models.Model):
    form_id = models.ForeignKey(
        "AdmissionForm", on_delete=models.CASCADE, null=True, blank=True
    )

    school = models.ForeignKey(
        "School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="document_files",  # ✅ changed
    )

    label = models.ForeignKey(
        "DocumentField", on_delete=models.CASCADE, null=True, blank=True
    )

    document = models.FileField(upload_to="student_documents/", null=True, blank=True)

    student = models.ForeignKey(
        "Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label.label if self.label else "Student Document"


class Subject(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    name = models.CharField(max_length=100)

    division = models.ForeignKey(
        Division, on_delete=models.CASCADE, related_name="subjects"
    )

    def __str__(self):
        return f"{self.name} ({self.division})"


class Syllabus(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    division = models.ForeignKey(
        "Division", on_delete=models.CASCADE, related_name="syllabi"
    )
    subject = models.ForeignKey(
        "Subject", on_delete=models.CASCADE, related_name="syllabi"
    )
    syllabus_file = models.FileField(upload_to="syllabus/")

    def __str__(self):
        return f"{self.division} - {self.subject}"


class AdmissionFee(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="fee", null=True, blank=True
    )

    amount = models.IntegerField()
    currency = models.CharField(max_length=10, default="INR")

    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    payment_mode = models.CharField(
        max_length=100, null=True, blank=True
    )  # fill while Admission prossecc by student

    fee_verify = models.BooleanField(default=False)  # fee managment verify tanf change

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)


class AssignClass(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, null=True, blank=True
    )
    division = models.ForeignKey(
        Division, on_delete=models.CASCADE, null=True, blank=True
    )
    is_class_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.division}"


# ========= TIME TABLE MODEL============


class Tt_year(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    year = models.CharField(max_length=10, null=True, blank=True)


class Tt_day(models.Model):
    DAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
    ]

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    year = models.ForeignKey(Tt_year, on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(max_length=50, choices=DAY_CHOICES, null=True, blank=True)
    class_div = models.ForeignKey(
        Division, on_delete=models.CASCADE, null=True, blank=True
    )
    lecture = models.CharField(max_length=50, null=True, blank=True)


class Tt_day_time(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    day = models.ForeignKey(Tt_day, on_delete=models.CASCADE, null=True, blank=True)
    start = models.TimeField(null=True, blank=True)
    end = models.TimeField(null=True, blank=True)


class Tt_breaks(models.Model):
    day = models.ForeignKey(Tt_day, on_delete=models.CASCADE, null=True, blank=True)
    total_breaks = models.IntegerField(null=True, blank=True)
    breaks = models.IntegerField(null=True, blank=True)
    time = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)


class Tt_slot(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    day = models.ForeignKey(Tt_day, on_delete=models.CASCADE, null=True, blank=True)
    lecture = models.CharField(max_length=50, null=True, blank=True)
    slot = models.JSONField(null=True, blank=True)


class Time_table(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    year = models.ForeignKey(Tt_year, on_delete=models.CASCADE, null=True, blank=True)
    start = models.TimeField(null=True, blank=True)
    end = models.TimeField(null=True, blank=True)
    class_div = models.ForeignKey(
        Division, on_delete=models.CASCADE, null=True, blank=True
    )
    day = models.CharField(max_length=50, null=True, blank=True)
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    slot = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.year} - {self.day} - {self.class_div} - {self.slot}"

class AttendanceTimeRule(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    half_day_time = models.TimeField(null=True, blank=True)
    
    
class AttendanceLocation(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Attendance Location for {self.school}"


class Attendance(models.Model):

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=20, null=True, blank=True)
    date_time = models.DateTimeField(null=True, blank=True)
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.date}"


class LeaveTemplate(models.Model):
    TIMELINE_CHOICES = [
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("SEMI_ANNUAL", "Semi-Annual"),
        ("ANNUAL", "Annual"),
    ]

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    time_line = models.CharField(
        max_length=20, choices=TIMELINE_CHOICES, null=True, blank=True
    )
    leave_type = models.CharField(max_length=100, null=True, blank=True)
    leave_num = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.leave_type} - {self.time_line}"


class LeaveRequest(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    leave_type = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    total_days = models.IntegerField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(
        auto_now=True, null=True, blank=True
    )  # at a time no nedd this

    def __str__(self):
        return f"{self.staff.name} - {self.leave_type} - {self.status}"


class LeavePerDay(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

    leave = models.ForeignKey(
        LeaveRequest, on_delete=models.CASCADE, null=True, blank=True, related_name="leave_days"
    )
    date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.total_leaves} leaves"


class StaffRemainingLeave(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    leave_template = models.ForeignKey(
        LeaveTemplate, on_delete=models.CASCADE, null=True, blank=True
    )
    total_levaes = models.IntegerField(null=True, blank=True)
    remaining_leaves = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.staff} - {self.leave_template}"





class Announcement(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    publish_at = models.DateTimeField()   # when it becomes visible
    expires_at = models.DateTimeField(null=True, blank=True)  # optional

    created_at = models.DateTimeField(auto_now_add=True)

class AnnouncementTarget(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, db_index=True)  
    TARGET_TYPE = [
        ('ALL', 'All'),
        ('ROLE', 'Role'),
        ('CLASS', 'Class'),
        ('SPECIFIC', 'Specific User'),
    ]

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='targets'
    )

    target_type = models.CharField(max_length=10, choices=TARGET_TYPE)
    target_id = models.IntegerField(null=True, blank=True)