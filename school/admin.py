from django.contrib import admin
from .models import (
    Student, Teacher, Class, Subject, Enrollment, Attendance,
    Exam, ExamResult, FeeStructure, FeePayment, LibraryBook,
    BookIssue, Event, Notice, ContactMessage, UserProfile, TimeTable,
    Vehicle, Route, Stop, TransportAssignment, AcademicYear, Term, SubjectYearPlan
)


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    date_hierarchy = 'created_at'


@admin.register(Student)
class StudentAdmin(BaseAdmin):
    list_display = ['roll_number', 'first_name', 'last_name', 'email', 'phone', 'status']
    list_filter = ['gender', 'status', 'city', 'blood_group']
    search_fields = ['first_name', 'last_name', 'roll_number', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Teacher)
class TeacherAdmin(BaseAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'email', 'qualification', 'status']
    list_filter = ['qualification', 'gender', 'status']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email', 'specialization']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Class)
class ClassAdmin(BaseAdmin):
    list_display = ['name', 'section', 'code', 'class_teacher', 'capacity', 'status']
    list_filter = ['status']
    search_fields = ['name', 'code', 'section']


@admin.register(Subject)
class SubjectAdmin(BaseAdmin):
    list_display = ['name', 'code', 'subject_teacher', 'is_lab', 'max_marks', 'status']
    list_filter = ['is_lab', 'status']
    search_fields = ['name', 'code']


@admin.register(Enrollment)
class EnrollmentAdmin(BaseAdmin):
    list_display = ['student', 'class_enrolled', 'academic_year', 'date_enrolled', 'status']
    list_filter = ['academic_year', 'status']
    search_fields = ['student__first_name', 'student__roll_number', 'academic_year']


@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ['student', 'class_enrolled', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date']
    search_fields = ['student__first_name', 'student__roll_number']


@admin.register(Exam)
class ExamAdmin(BaseAdmin):
    list_display = ['name', 'exam_type', 'class_enrolled', 'subject', 'date', 'total_marks']
    list_filter = ['exam_type', 'date']
    search_fields = ['name', 'subject__name']


@admin.register(ExamResult)
class ExamResultAdmin(BaseAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'grade']
    list_filter = ['exam__exam_type', 'grade']
    search_fields = ['student__first_name', 'exam__name']


@admin.register(FeeStructure)
class FeeStructureAdmin(BaseAdmin):
    list_display = ['name', 'fee_type', 'class_enrolled', 'amount', 'due_date', 'status']
    list_filter = ['fee_type', 'is_annual', 'status']
    search_fields = ['name', 'class_enrolled__name']


@admin.register(FeePayment)
class FeePaymentAdmin(BaseAdmin):
    list_display = ['student', 'fee_structure', 'amount_paid', 'payment_date', 'payment_method', 'is_paid']
    list_filter = ['payment_method', 'is_paid', 'payment_date']
    search_fields = ['student__first_name', 'receipt_number', 'transaction_id']


@admin.register(LibraryBook)
class LibraryBookAdmin(BaseAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'quantity', 'available', 'status']
    list_filter = ['category', 'status']
    search_fields = ['title', 'author', 'isbn']


@admin.register(BookIssue)
class BookIssueAdmin(BaseAdmin):
    list_display = ['book', 'student', 'issue_date', 'due_date', 'return_date', 'is_returned']
    list_filter = ['is_returned', 'issue_date']
    search_fields = ['book__title', 'student__first_name']


@admin.register(Event)
class EventAdmin(BaseAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'venue', 'is_public', 'status']
    list_filter = ['event_type', 'is_public', 'status']
    search_fields = ['title', 'venue']


@admin.register(Notice)
class NoticeAdmin(BaseAdmin):
    list_display = ['title', 'priority', 'publish_date', 'expire_date', 'posted_by', 'status']
    list_filter = ['priority', 'status', 'publish_date']
    search_fields = ['title', 'content']


@admin.register(ContactMessage)
class ContactMessageAdmin(BaseAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'replied', 'created_at']
    list_filter = ['is_read', 'replied']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(BaseAdmin):
    list_display = ['user', 'user_type', 'phone', 'is_email_verified']
    list_filter = ['user_type', 'is_email_verified']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(TimeTable)
class TimeTableAdmin(BaseAdmin):
    list_display = ['class_enrolled', 'subject', 'teacher', 'day', 'start_time', 'end_time']
    list_filter = ['day', 'status']
    search_fields = ['class_enrolled__name', 'subject__name', 'teacher__first_name']


# ==================== TRANSPORT ADMIN ====================

@admin.register(Vehicle)
class VehicleAdmin(BaseAdmin):
    list_display = ['vehicle_number', 'registration_number', 'model_name', 'capacity', 'driver_name', 'fuel_type', 'status']
    list_filter = ['fuel_type', 'status']
    search_fields = ['vehicle_number', 'registration_number', 'driver_name']


@admin.register(Route)
class RouteAdmin(BaseAdmin):
    list_display = ['route_code', 'name', 'distance_km', 'fee_amount', 'vehicle', 'status']
    list_filter = ['status']
    search_fields = ['name', 'route_code']


@admin.register(Stop)
class StopAdmin(BaseAdmin):
    list_display = ['name', 'route', 'stop_order', 'morning_pickup_time', 'evening_drop_time', 'status']
    list_filter = ['status']
    search_fields = ['name', 'route__name']
    ordering = ['route', 'stop_order']


@admin.register(TransportAssignment)
class TransportAssignmentAdmin(BaseAdmin):
    list_display = ['student', 'vehicle', 'route', 'stop', 'academic_year', 'fee_amount', 'status']
    list_filter = ['academic_year', 'status']
    search_fields = ['student__first_name', 'student__roll_number', 'vehicle__vehicle_number']


@admin.register(AcademicYear)
class AcademicYearAdmin(BaseAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current', 'status']
    list_filter = ['is_current', 'status']


@admin.register(Term)
class TermAdmin(BaseAdmin):
    list_display = ['name', 'academic_year', 'start_date', 'end_date', 'status']
    list_filter = ['academic_year', 'status']


@admin.register(SubjectYearPlan)
class SubjectYearPlanAdmin(BaseAdmin):
    list_display = ['subject', 'topic', 'class_enrolled', 'term', 'no_of_periods', 'is_completed', 'status']
    list_filter = ['is_completed', 'academic_year', 'term', 'status']
    search_fields = ['topic', 'subject__name', 'class_enrolled__name']
