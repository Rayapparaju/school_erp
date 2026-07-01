from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Student, Teacher, Class, Subject, Enrollment, Attendance,
    Exam, ExamResult, FeeStructure, FeePayment, LibraryBook,
    BookIssue, Event, Notice, ContactMessage, TimeTable,
    Vehicle, Route, Stop, TransportAssignment
)
from .serializers import (
    StudentSerializer, TeacherSerializer, ClassSerializer, SubjectSerializer,
    EnrollmentSerializer, AttendanceSerializer, ExamSerializer, ExamResultSerializer,
    FeeStructureSerializer, FeePaymentSerializer, LibraryBookSerializer,
    BookIssueSerializer, EventSerializer, NoticeSerializer,
    ContactMessageSerializer, TimeTableSerializer,
    VehicleSerializer, RouteSerializer, StopSerializer, TransportAssignmentSerializer
)


class BaseViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class StudentViewSet(BaseViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    search_fields = ['first_name', 'last_name', 'roll_number', 'email']
    filterset_fields = ['gender', 'status', 'blood_group', 'city']


class TeacherViewSet(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    filterset_fields = ['qualification', 'gender', 'status']


class ClassViewSet(BaseViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    search_fields = ['name', 'code', 'section']
    filterset_fields = ['status']


class SubjectViewSet(BaseViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    search_fields = ['name', 'code']
    filterset_fields = ['is_lab', 'status']


class EnrollmentViewSet(BaseViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    search_fields = ['academic_year']
    filterset_fields = ['academic_year', 'status']


class AttendanceViewSet(BaseViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    search_fields = ['remark']
    filterset_fields = ['status', 'date']


class ExamViewSet(BaseViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    search_fields = ['name', 'description']
    filterset_fields = ['exam_type', 'date']


class ExamResultViewSet(BaseViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    search_fields = ['grade', 'remarks']
    filterset_fields = ['grade', 'exam']


class FeeStructureViewSet(BaseViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    search_fields = ['name', 'description']
    filterset_fields = ['is_annual', 'status']


class FeePaymentViewSet(BaseViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    search_fields = ['transaction_id', 'receipt_number']
    filterset_fields = ['payment_method', 'is_paid', 'payment_date']


class LibraryBookViewSet(BaseViewSet):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    search_fields = ['title', 'author', 'isbn']
    filterset_fields = ['category', 'status']


class BookIssueViewSet(BaseViewSet):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    search_fields = ['book__title', 'student__first_name']
    filterset_fields = ['is_returned', 'fine_paid']


class EventViewSet(BaseViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    search_fields = ['title', 'venue', 'organizer']
    filterset_fields = ['event_type', 'is_public', 'status']


class NoticeViewSet(BaseViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    search_fields = ['title', 'content']
    filterset_fields = ['priority', 'status']


class ContactMessageViewSet(BaseViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    search_fields = ['name', 'email', 'subject']
    filterset_fields = ['is_read', 'replied']


class TimeTableViewSet(BaseViewSet):
    queryset = TimeTable.objects.all()
    serializer_class = TimeTableSerializer
    search_fields = ['day', 'room_number']
    filterset_fields = ['day', 'status']


# ==================== TRANSPORT VIEWSETS ====================

class VehicleViewSet(BaseViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    search_fields = ['vehicle_number', 'registration_number', 'driver_name']
    filterset_fields = ['fuel_type', 'status']


class RouteViewSet(BaseViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    search_fields = ['name', 'route_code']
    filterset_fields = ['status']


class StopViewSet(BaseViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    search_fields = ['name', 'landmark']
    filterset_fields = ['status']


class TransportAssignmentViewSet(BaseViewSet):
    queryset = TransportAssignment.objects.all()
    serializer_class = TransportAssignmentSerializer
    search_fields = ['academic_year']
    filterset_fields = ['academic_year', 'status']
