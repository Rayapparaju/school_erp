from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public Website
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('password-change/', views.change_password, name='change_password'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html'
         ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Dashboard
    path('dashboard/', include(([
        path('', views.dashboard_home, name='home'),
        # Students
        path('students/', views.student_list, name='student_list'),
        path('students/admission/', views.admission_create, name='student_admission'),
        path('students/create/', views.student_create, name='student_create'),
        path('students/<int:pk>/', views.student_detail, name='student_detail'),
        path('students/<int:pk>/update/', views.student_update, name='student_update'),
        path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
        path('students/export/csv/', views.student_export_csv, name='student_export_csv'),
        path('students/export/excel/', views.student_export_excel, name='student_export_excel'),
        path('students/export/pdf/', views.student_export_pdf, name='student_export_pdf'),
        # Teachers
        path('teachers/', views.teacher_list, name='teacher_list'),
        path('teachers/create/', views.teacher_create, name='teacher_create'),
        path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
        path('teachers/<int:pk>/update/', views.teacher_update, name='teacher_update'),
        path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
        path('teachers/export/csv/', views.teacher_export_csv, name='teacher_export_csv'),
        path('teachers/export/excel/', views.teacher_export_excel, name='teacher_export_excel'),
        path('teachers/export/pdf/', views.teacher_export_pdf, name='teacher_export_pdf'),
        # Classes
        path('classes/', views.class_list, name='class_list'),
        path('classes/create/', views.class_create, name='class_create'),
        path('classes/<int:pk>/update/', views.class_update, name='class_update'),
        path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),
        # Subjects
        path('subjects/', views.subject_list, name='subject_list'),
        path('subjects/create/', views.subject_create, name='subject_create'),
        path('subjects/<int:pk>/update/', views.subject_update, name='subject_update'),
        path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
        # Enrollments
        path('enrollments/', views.enrollment_list, name='enrollment_list'),
        path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
        path('enrollments/<int:pk>/update/', views.enrollment_update, name='enrollment_update'),
        path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),
        # Attendance
        path('attendance/', views.attendance_list, name='attendance_list'),
        path('attendance/create/', views.attendance_create, name='attendance_create'),
        path('attendance/<int:pk>/update/', views.attendance_update, name='attendance_update'),
        path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
        # Exams
        path('exams/', views.exam_list, name='exam_list'),
        path('exams/create/', views.exam_create, name='exam_create'),
        path('exams/<int:pk>/update/', views.exam_update, name='exam_update'),
        path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),
        # Exam Results
        path('exam-results/', views.exam_result_list, name='exam_result_list'),
        path('exam-results/create/', views.exam_result_create, name='exam_result_create'),
        path('exam-results/<int:pk>/update/', views.exam_result_update, name='exam_result_update'),
        path('exam-results/<int:pk>/delete/', views.exam_result_delete, name='exam_result_delete'),
        # Fee Structure
        path('fee-structures/', views.fee_structure_list, name='fee_structure_list'),
        path('fee-structures/create/', views.fee_structure_create, name='fee_structure_create'),
        path('fee-structures/<int:pk>/update/', views.fee_structure_update, name='fee_structure_update'),
        path('fee-structures/<int:pk>/delete/', views.fee_structure_delete, name='fee_structure_delete'),
        # Fee Payments
        path('fee-payments/', views.fee_payment_list, name='fee_payment_list'),
        path('fee-payments/create/', views.fee_payment_create, name='fee_payment_create'),
        path('fee-payments/bulk-create/', views.fee_payment_bulk_create, name='fee_payment_bulk_create'),
        path('fee-payments/bulk-receipt/<str:receipt_prefix>/', views.fee_payment_bulk_receipt, name='fee_payment_bulk_receipt'),
        path('fee-payments/bulk-receipt/<str:receipt_prefix>/pdf/', views.fee_payment_bulk_receipt_pdf, name='fee_payment_bulk_receipt_pdf'),
        path('fee-payments/<int:pk>/update/', views.fee_payment_update, name='fee_payment_update'),
        path('fee-payments/<int:pk>/delete/', views.fee_payment_delete, name='fee_payment_delete'),
        path('fee-payments/<int:pk>/receipt/', views.fee_payment_receipt, name='fee_payment_receipt'),
        path('fee-payments/<int:pk>/receipt/pdf/', views.fee_payment_pdf, name='fee_payment_pdf'),
        # Library
        path('library/', views.library_book_list, name='library_book_list'),
        path('library/create/', views.library_book_create, name='library_book_create'),
        path('library/<int:pk>/update/', views.library_book_update, name='library_book_update'),
        path('library/<int:pk>/delete/', views.library_book_delete, name='library_book_delete'),
        path('book-issues/', views.book_issue_list, name='book_issue_list'),
        path('book-issues/create/', views.book_issue_create, name='book_issue_create'),
        path('book-issues/<int:pk>/update/', views.book_issue_update, name='book_issue_update'),
        path('book-issues/<int:pk>/delete/', views.book_issue_delete, name='book_issue_delete'),
        path('book-issues/<int:pk>/return/', views.book_return, name='book_return'),
        # Events
        path('events/', views.event_list, name='event_list'),
        path('events/create/', views.event_create, name='event_create'),
        path('events/<int:pk>/update/', views.event_update, name='event_update'),
        path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
        # Notices
        path('notices/', views.notice_list, name='notice_list'),
        path('notices/create/', views.notice_create, name='notice_create'),
        path('notices/<int:pk>/update/', views.notice_update, name='notice_update'),
        path('notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),
        # Transport
        path('vehicles/', views.vehicle_list, name='vehicle_list'),
        path('vehicles/create/', views.vehicle_create, name='vehicle_create'),
        path('vehicles/<int:pk>/update/', views.vehicle_update, name='vehicle_update'),
        path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
        path('routes/', views.route_list, name='route_list'),
        path('routes/create/', views.route_create, name='route_create'),
        path('routes/<int:pk>/update/', views.route_update, name='route_update'),
        path('routes/<int:pk>/delete/', views.route_delete, name='route_delete'),
        path('stops/', views.stop_list, name='stop_list'),
        path('stops/create/', views.stop_create, name='stop_create'),
        path('stops/<int:pk>/update/', views.stop_update, name='stop_update'),
        path('stops/<int:pk>/delete/', views.stop_delete, name='stop_delete'),
        path('transport-assignments/', views.transport_assignment_list, name='transport_assignment_list'),
        path('transport-assignments/create/', views.transport_assignment_create, name='transport_assignment_create'),
        path('transport-assignments/<int:pk>/update/', views.transport_assignment_update, name='transport_assignment_update'),
        path('transport-assignments/<int:pk>/delete/', views.transport_assignment_delete, name='transport_assignment_delete'),
        # Timetable
        path('timetable/', views.timetable_list, name='timetable_list'),
        path('timetable/create/', views.timetable_create, name='timetable_create'),
        path('timetable/<int:pk>/update/', views.timetable_update, name='timetable_update'),
        path('timetable/<int:pk>/delete/', views.timetable_delete, name='timetable_delete'),
        path('timetable/class/<int:pk>/', views.timetable_class_view, name='timetable_class_view'),
        path('timetable/teacher/<int:pk>/', views.timetable_teacher_view, name='timetable_teacher_view'),
        # Year Plan
        path('year-plans/', views.year_plan_list, name='year_plan_list'),
        path('year-plans/create/', views.year_plan_create, name='year_plan_create'),
        path('year-plans/<int:pk>/', views.year_plan_detail, name='year_plan_detail'),
        path('year-plans/<int:pk>/update/', views.year_plan_update, name='year_plan_update'),
        path('year-plans/<int:pk>/delete/', views.year_plan_delete, name='year_plan_delete'),
        # Subject Year Plan
        path('subject-year-plans/', views.subject_year_plan_list, name='subject_year_plan_list'),
        path('subject-year-plans/create/', views.subject_year_plan_create, name='subject_year_plan_create'),
        path('subject-year-plans/<int:pk>/update/', views.subject_year_plan_update, name='subject_year_plan_update'),
        path('subject-year-plans/<int:pk>/delete/', views.subject_year_plan_delete, name='subject_year_plan_delete'),
        # Reports
        path('reports/', views.reports_dashboard, name='reports'),
        path('reports/students/', views.report_students, name='report_students'),
        path('reports/attendance/', views.report_attendance, name='report_attendance'),
        path('reports/fees/', views.report_fees, name='report_fees'),
        path('reports/exams/', views.report_exams, name='report_exams'),
        # API
        path('api/', include('school.api_urls')),
    ], 'dashboard'), namespace='dashboard')),
]
