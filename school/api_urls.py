from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'students', api_views.StudentViewSet)
router.register(r'teachers', api_views.TeacherViewSet)
router.register(r'classes', api_views.ClassViewSet)
router.register(r'subjects', api_views.SubjectViewSet)
router.register(r'enrollments', api_views.EnrollmentViewSet)
router.register(r'attendance', api_views.AttendanceViewSet)
router.register(r'exams', api_views.ExamViewSet)
router.register(r'exam-results', api_views.ExamResultViewSet)
router.register(r'fee-structures', api_views.FeeStructureViewSet)
router.register(r'fee-payments', api_views.FeePaymentViewSet)
router.register(r'library-books', api_views.LibraryBookViewSet)
router.register(r'book-issues', api_views.BookIssueViewSet)
router.register(r'events', api_views.EventViewSet)
router.register(r'notices', api_views.NoticeViewSet)
router.register(r'contact-messages', api_views.ContactMessageViewSet)
router.register(r'timetables', api_views.TimeTableViewSet)
router.register(r'vehicles', api_views.VehicleViewSet)
router.register(r'routes', api_views.RouteViewSet)
router.register(r'stops', api_views.StopViewSet)
router.register(r'transport-assignments', api_views.TransportAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
