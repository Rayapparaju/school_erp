from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Student(BaseModel):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    admission_date = models.DateField(default=timezone.now)
    roll_number = models.CharField(max_length=50, unique=True)
    guardian_name = models.CharField(max_length=200)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    medical_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Teacher(BaseModel):
    GENDER_CHOICES = Student.GENDER_CHOICES
    QUALIFICATION_CHOICES = [
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'Ph.D.'),
        ('diploma', 'Diploma'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES)
    specialization = models.CharField(max_length=200)
    joining_date = models.DateField(default=timezone.now)
    photo = models.ImageField(upload_to='teachers/photos/', blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    experience_years = models.IntegerField(default=0)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Class(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    section = models.CharField(max_length=10, blank=True)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.IntegerField(default=40)

    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        ordering = ['name', 'section']

    def __str__(self):
        return f"{self.name} - {self.section}" if self.section else self.name


class Subject(BaseModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    subject_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    classes = models.ManyToManyField(Class, related_name='subjects')
    is_lab = models.BooleanField(default=False)
    max_marks = models.IntegerField(default=100)
    pass_marks = models.IntegerField(default=40)

    class Meta:
        ordering = ['name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Enrollment(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    academic_year = models.CharField(max_length=20)
    date_enrolled = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ['student', 'class_enrolled', 'academic_year']
        ordering = ['-academic_year']

    def __str__(self):
        return f"{self.student} -> {self.class_enrolled} ({self.academic_year})"


class Attendance(BaseModel):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remark = models.TextField(blank=True)
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class Exam(BaseModel):
    EXAM_TYPE_CHOICES = [
        ('midterm', 'Mid Term'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('test', 'Test'),
        ('practical', 'Practical'),
    ]

    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.IntegerField(default=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.date})"


class ExamResult(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ['exam', 'student']
        ordering = ['-exam__date']

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}"

    def save(self, *args, **kwargs):
        percentage = (float(self.marks_obtained) / float(self.exam.total_marks)) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C'
        elif percentage >= 40:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)


class FeeStructure(BaseModel):
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition Fee'),
        ('library', 'Library Fee'),
        ('books', 'Books Fee'),
        ('admission', 'Admission Fee'),
        ('transport', 'Transport Fee'),
    ]

    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='tuition')
    name = models.CharField(max_length=200, blank=True)
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='fee_structures')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    description = models.TextField(blank=True)
    is_annual = models.BooleanField(default=False)
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['class_enrolled', 'fee_type']
        unique_together = ('class_enrolled', 'fee_type')
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.get_fee_type_display()} - {self.class_enrolled}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - \u20b9{self.amount}"


class FeePayment(BaseModel):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('cheque', 'Cheque'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    is_paid = models.BooleanField(default=False)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Fee Payment'
        verbose_name_plural = 'Fee Payments'

    def __str__(self):
        return f"{self.student} - {self.fee_structure} - \u20b9{self.amount_paid}"


class LibraryBook(BaseModel):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    publisher = models.CharField(max_length=200, blank=True)
    published_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    category = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    available = models.IntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True)
    cover_image = models.ImageField(upload_to='library/covers/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Library Book'
        verbose_name_plural = 'Library Books'

    def __str__(self):
        return f"{self.title} by {self.author}"


class BookIssue(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_issues')
    book = models.ForeignKey(LibraryBook, on_delete=models.CASCADE, related_name='issues')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Book Issue'
        verbose_name_plural = 'Book Issues'

    def __str__(self):
        return f"{self.book} -> {self.student} ({self.issue_date})"


class Event(BaseModel):
    EVENT_TYPE_CHOICES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('holiday', 'Holiday'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200, blank=True)
    is_public = models.BooleanField(default=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.title


class Notice(BaseModel):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=300)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    attachment = models.FileField(upload_to='notices/', blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    target_classes = models.ManyToManyField(Class, blank=True)
    publish_date = models.DateField(default=timezone.now)
    expire_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-publish_date', '-priority']
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'

    def __str__(self):
        return self.title


class ContactMessage(BaseModel):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.subject} - {self.name}"


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('staff', 'Staff'),
    ], default='student')
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"


class TimeTable(BaseModel):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetables')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['day', 'start_time']
        verbose_name = 'Time Table'
        verbose_name_plural = 'Time Tables'
        unique_together = ['class_enrolled', 'day', 'start_time']

    def __str__(self):
        return f"{self.class_enrolled} - {self.subject} ({self.day})"


# ==================== TRANSPORT MODELS ====================

class Vehicle(BaseModel):
    vehicle_number = models.CharField(max_length=50, unique=True, verbose_name='Vehicle #')
    registration_number = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    driver_name = models.CharField(max_length=200)
    driver_phone = models.CharField(max_length=20)
    driver_license = models.CharField(max_length=100)
    insurance_valid_until = models.DateField()
    last_maintenance_date = models.DateField(null=True, blank=True)
    fuel_type = models.CharField(max_length=20, choices=[
        ('petrol', 'Petrol'), ('diesel', 'Diesel'), ('cng', 'CNG'), ('electric', 'Electric')
    ], default='diesel')
    photo = models.ImageField(upload_to='transport/vehicles/', blank=True, null=True)

    class Meta:
        ordering = ['vehicle_number']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.vehicle_number} - {self.model_name}"


class Route(BaseModel):
    name = models.CharField(max_length=200)
    route_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')

    class Meta:
        ordering = ['name']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'

    def __str__(self):
        return f"{self.route_code} - {self.name}"


class Stop(BaseModel):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=200)
    address = models.TextField()
    landmark = models.CharField(max_length=200, blank=True)
    stop_order = models.IntegerField(validators=[MinValueValidator(1)])
    morning_pickup_time = models.TimeField()
    evening_drop_time = models.TimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['route', 'stop_order']
        verbose_name = 'Stop'
        verbose_name_plural = 'Stops'
        unique_together = ['route', 'stop_order']

    def __str__(self):
        return f"{self.route.route_code} - {self.name} (Stop #{self.stop_order})"


class TransportAssignment(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transport_assignments')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='assignments')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='assignments')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='assignments')
    academic_year = models.CharField(max_length=20)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transport Assignment'
        verbose_name_plural = 'Transport Assignments'
        unique_together = ['student', 'academic_year']

    def __str__(self):
        return f"{self.student.full_name} -> {self.vehicle.vehicle_number} ({self.academic_year})"


class AcademicYear(BaseModel):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Term(BaseModel):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['start_date']
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class SubjectYearPlan(BaseModel):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='subject_plans')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='subject_plans')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='year_plans')
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subject_plans')
    topic = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    no_of_periods = models.IntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['class_enrolled', 'subject', 'start_date']
        verbose_name = 'Subject Year Plan'
        verbose_name_plural = 'Subject Year Plans'

    def __str__(self):
        return f"{self.subject} - {self.topic} ({self.class_enrolled})"
