import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.paginator import Paginator
from .models import (
    Student, Teacher, Class, Subject, Enrollment, Attendance,
    Exam, ExamResult, FeeStructure, FeePayment, LibraryBook,
    BookIssue, Event, Notice, ContactMessage, UserProfile, TimeTable,
    Vehicle, Route, Stop, TransportAssignment, AcademicYear, Term, SubjectYearPlan
)
from .forms import (
    RegistrationForm, LoginForm, UserProfileForm, StudentForm, AdmissionForm,
    TeacherForm, ClassForm, SubjectForm, EnrollmentForm, AttendanceForm,
    ExamForm, ExamResultForm, FeeStructureForm, FeePaymentForm, LibraryBookForm,
    BookIssueForm, EventForm, NoticeForm, ContactForm, TimeTableForm,
    PasswordChangeCustomForm, VehicleForm, RouteForm, StopForm,
    TransportAssignmentForm, AcademicYearForm, TermForm, SubjectYearPlanForm
)
from .utils import export_csv, export_excel, generate_pdf_report, generate_fee_receipt_pdf
from .decorators import admin_required, staff_required

# ==================== PUBLIC WEBSITE VIEWS ====================

def home(request):
    events = Event.objects.filter(is_active=True, status=True, is_public=True)[:3]
    notices = Notice.objects.filter(is_active=True, status=True)[:5]
    context = {
        'events': events,
        'notices': notices,
        'student_count': Student.objects.filter(is_active=True).count(),
        'teacher_count': Teacher.objects.filter(is_active=True).count(),
        'class_count': Class.objects.filter(is_active=True).count(),
    }
    return render(request, 'public/index.html', context)


def about(request):
    teachers = Teacher.objects.filter(is_active=True, status=True)[:4]
    return render(request, 'public/about.html', {'teachers': teachers})


def services(request):
    return render(request, 'public/services.html')


def gallery(request):
    events = Event.objects.filter(is_active=True, status=True, is_public=True)
    return render(request, 'public/gallery.html', {'events': events})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'public/contact.html', {'form': form})


# ==================== AUTHENTICATION VIEWS ====================

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                user_type='student',
            )
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    return render(request, 'auth/profile.html')


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid():
            user_form.save()
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=profile)
    return render(request, 'auth/edit_profile.html', {
        'form': user_form,
        'profile': profile,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeCustomForm(request.user)
    return render(request, 'auth/change_password.html', {'form': form})


# ==================== DASHBOARD HOME ====================

@login_required
def dashboard_home(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_classes': Class.objects.filter(is_active=True).count(),
        'total_subjects': Subject.objects.filter(is_active=True).count(),
        'active_enrollments': Enrollment.objects.filter(is_active=True).count(),
        'today_present': Attendance.objects.filter(date=today, status='present').count(),
        'today_absent': Attendance.objects.filter(date=today, status='absent').count(),
        'pending_fees': FeePayment.objects.filter(is_paid=False).count(),
        'total_fees': FeePayment.objects.filter(is_paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
        'issued_books': BookIssue.objects.filter(is_returned=False).count(),
        'total_books': LibraryBook.objects.filter(is_active=True).aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_vehicles': Vehicle.objects.filter(is_active=True).count(),
        'total_routes': Route.objects.filter(is_active=True).count(),
        'active_transport': TransportAssignment.objects.filter(is_active=True).count(),
        'upcoming_events': Event.objects.filter(start_date__gte=timezone.now(), is_active=True)[:5],
        'recent_notices': Notice.objects.filter(is_active=True)[:5],
        'recent_students': Student.objects.filter(is_active=True)[:5],
        'recent_teachers': Teacher.objects.filter(is_active=True)[:5],
        'attendance_today': Attendance.objects.filter(date=today),
    }
    return render(request, 'dashboard/index.html', context)


# ==================== GENERIC CRUD HELPERS ====================

def paginate(request, queryset, per_page=20):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    return paginator.get_page(page)


def search_and_filter(request, queryset, search_fields=None, filter_fields=None):
    search_query = request.GET.get('search', '')
    if search_query and search_fields:
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f'{field}__icontains': search_query})
        queryset = queryset.filter(q_objects)

    if filter_fields and request.GET.get('status'):
        queryset = queryset.filter(status=request.GET.get('status') == 'active')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)

    sort = request.GET.get('sort', '-created_at')
    if sort:
        queryset = queryset.order_by(sort)

    return queryset, search_query


def crud_list(request, model_class, template_name, context_extra=None, search_fields=None):
    queryset = model_class.objects.all()
    if hasattr(model_class, 'is_active'):
        if request.GET.get('show_all'):
            queryset = model_class.objects.all()
        else:
            queryset = model_class.objects.filter(is_active=True)
    queryset, search_query = search_and_filter(request, queryset, search_fields)
    page_obj = paginate(request, queryset)
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'module_name': model_class._meta.verbose_name_plural.title(),
    }
    if context_extra:
        context.update(context_extra)
    return render(request, template_name, context)


def crud_create(request, form_class, template_name, redirect_url, extra_context=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'{obj._meta.verbose_name.title()} created successfully!')
            return redirect(redirect_url)
    else:
        form = form_class()
    context = {'form': form}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def crud_update(request, model_class, pk, form_class, template_name, redirect_url, extra_context=None):
    obj = get_object_or_404(model_class, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{obj._meta.verbose_name.title()} updated successfully!')
            return redirect(redirect_url)
    else:
        form = form_class(instance=obj)
    context = {'form': form, 'object': obj}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def crud_delete(request, model_class, pk, redirect_url, extra_msg=''):
    obj = get_object_or_404(model_class, pk=pk)
    obj.is_active = False
    obj.status = False
    obj.save()
    messages.success(request, f'{obj._meta.verbose_name.title()} deactivated successfully! {extra_msg}')
    return redirect(redirect_url)


# ==================== STUDENT CRUD ====================

@login_required
def student_list(request):
    return crud_list(request, Student, 'dashboard/students/list.html', search_fields=['first_name', 'last_name', 'roll_number', 'email'])


@login_required
def student_create(request):
    return crud_create(request, StudentForm, 'dashboard/students/form.html', 'dashboard:student_list', {'title': 'Add New Student'})


@login_required
def admission_create(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name} admitted successfully!')
            return redirect('dashboard:student_detail', pk=student.pk)
    else:
        form = AdmissionForm()
    return render(request, 'dashboard/students/admission_form.html', {
        'form': form,
        'title': 'New Student Admission',
    })


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student)
    attendance = Attendance.objects.filter(student=student)[:10]
    exam_results = ExamResult.objects.filter(student=student)[:10]
    payments = FeePayment.objects.filter(student=student)[:10]
    return render(request, 'dashboard/students/detail.html', {
        'student': student,
        'enrollments': enrollments,
        'attendance': attendance,
        'exam_results': exam_results,
        'payments': payments,
    })


@login_required
def student_update(request, pk):
    return crud_update(request, Student, pk, StudentForm, 'dashboard/students/form.html', 'dashboard:student_list', {'title': 'Update Student'})


@login_required
def student_delete(request, pk):
    return crud_delete(request, Student, pk, 'dashboard:student_list')


@login_required
def student_export_csv(request):
    students = Student.objects.filter(is_active=True).prefetch_related('enrollments__class_enrolled')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=students.csv'
    import csv
    writer = csv.writer(response)
    headers = [
        'Roll No', 'First Name', 'Last Name', 'Full Name', 'Email', 'Phone',
        'Date of Birth', 'Gender', 'Address', 'City', 'State', 'Zip Code',
        'Photo URL', 'Admission Date', 'Guardian Name', 'Guardian Phone',
        'Guardian Email', 'Blood Group', 'Medical Notes', 'Class', 'Age',
        'Status', 'Created At', 'Updated At',
    ]
    writer.writerow(headers)
    for s in students:
        cls_name = s.enrollments.first().class_enrolled.name if s.enrollments.exists() else ''
        writer.writerow([
            s.roll_number, s.first_name, s.last_name, s.full_name, s.email,
            s.phone, s.date_of_birth, s.get_gender_display(), s.address,
            s.city, s.state, s.zip_code,
            s.photo.url if s.photo else '', s.admission_date,
            s.guardian_name, s.guardian_phone, s.guardian_email,
            s.blood_group, s.medical_notes, cls_name, s.age,
            'Active' if s.status else 'Inactive',
            s.created_at, s.updated_at,
        ])
    return response


@login_required
def student_export_excel(request):
    students = Student.objects.filter(is_active=True).prefetch_related('enrollments__class_enrolled')
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=students.xlsx'
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Students'
    headers = [
        'Roll No', 'First Name', 'Last Name', 'Full Name', 'Email', 'Phone',
        'Date of Birth', 'Gender', 'Address', 'City', 'State', 'Zip Code',
        'Photo URL', 'Admission Date', 'Guardian Name', 'Guardian Phone',
        'Guardian Email', 'Blood Group', 'Medical Notes', 'Class', 'Age',
        'Status', 'Created At', 'Updated At',
    ]
    ws.append(headers)
    for s in students:
        cls_name = s.enrollments.first().class_enrolled.name if s.enrollments.exists() else ''
        ws.append([
            s.roll_number, s.first_name, s.last_name, s.full_name, s.email,
            s.phone, s.date_of_birth, s.get_gender_display(), s.address,
            s.city, s.state, s.zip_code,
            s.photo.url if s.photo else '', s.admission_date,
            s.guardian_name, s.guardian_phone, s.guardian_email,
            s.blood_group, s.medical_notes, cls_name, s.age,
            'Active' if s.status else 'Inactive',
            s.created_at.replace(tzinfo=None) if s.created_at else '',
            s.updated_at.replace(tzinfo=None) if s.updated_at else '',
        ])
    wb.save(response)
    return response


@login_required
def student_export_pdf(request):
    students = Student.objects.filter(is_active=True).prefetch_related('enrollments__class_enrolled')
    data = []
    for s in students:
        cls_name = s.enrollments.first().class_enrolled.name if s.enrollments.exists() else ''
        data.append([
            s.roll_number, s.full_name, s.email, s.phone,
            s.get_gender_display(), s.city, cls_name,
        ])
    headers = ['Roll No', 'Name', 'Email', 'Phone', 'Gender', 'City', 'Class']
    return generate_pdf_report('Student Report', data, headers, 'students_report')


# ==================== TEACHER CRUD ====================

@login_required
def teacher_list(request):
    return crud_list(request, Teacher, 'dashboard/teachers/list.html', search_fields=['first_name', 'last_name', 'employee_id', 'email'])


@login_required
def teacher_create(request):
    return crud_create(request, TeacherForm, 'dashboard/teachers/form.html', 'dashboard:teacher_list', {'title': 'Add New Teacher'})


@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    subjects = Subject.objects.filter(subject_teacher=teacher)
    classes = Class.objects.filter(class_teacher=teacher)
    return render(request, 'dashboard/teachers/detail.html', {
        'teacher': teacher,
        'subjects': subjects,
        'classes': classes,
    })


@login_required
def teacher_update(request, pk):
    return crud_update(request, Teacher, pk, TeacherForm, 'dashboard/teachers/form.html', 'dashboard:teacher_list', {'title': 'Update Teacher'})


@login_required
def teacher_delete(request, pk):
    return crud_delete(request, Teacher, pk, 'dashboard:teacher_list')


@login_required
def teacher_export_csv(request):
    return export_csv(Teacher.objects.filter(is_active=True), 'teachers')


@login_required
def teacher_export_excel(request):
    return export_excel(Teacher.objects.filter(is_active=True), 'teachers')


@login_required
def teacher_export_pdf(request):
    teachers = Teacher.objects.filter(is_active=True)
    data = [[t.employee_id, t.full_name, t.email, t.qualification, t.specialization, t.experience_years] for t in teachers]
    headers = ['ID', 'Name', 'Email', 'Qualification', 'Specialization', 'Experience']
    return generate_pdf_report('Teacher Report', data, headers, 'teachers_report')


# ==================== CLASS CRUD ====================

@login_required
def class_list(request):
    return crud_list(request, Class, 'dashboard/classes/list.html', search_fields=['name', 'code', 'section'])


@login_required
def class_create(request):
    return crud_create(request, ClassForm, 'dashboard/classes/form.html', 'dashboard:class_list', {'title': 'Add New Class'})


@login_required
def class_update(request, pk):
    return crud_update(request, Class, pk, ClassForm, 'dashboard/classes/form.html', 'dashboard:class_list', {'title': 'Update Class'})


@login_required
def class_delete(request, pk):
    return crud_delete(request, Class, pk, 'dashboard:class_list')


# ==================== SUBJECT CRUD ====================

@login_required
def subject_list(request):
    return crud_list(request, Subject, 'dashboard/subjects/list.html', search_fields=['name', 'code'])


@login_required
def subject_create(request):
    return crud_create(request, SubjectForm, 'dashboard/subjects/form.html', 'dashboard:subject_list', {'title': 'Add New Subject'})


@login_required
def subject_update(request, pk):
    return crud_update(request, Subject, pk, SubjectForm, 'dashboard/subjects/form.html', 'dashboard:subject_list', {'title': 'Update Subject'})


@login_required
def subject_delete(request, pk):
    return crud_delete(request, Subject, pk, 'dashboard:subject_list')


# ==================== ENROLLMENT CRUD ====================

@login_required
def enrollment_list(request):
    return crud_list(request, Enrollment, 'dashboard/enrollments/list.html', search_fields=['academic_year'])


@login_required
def enrollment_create(request):
    return crud_create(request, EnrollmentForm, 'dashboard/enrollments/form.html', 'dashboard:enrollment_list', {'title': 'Add New Enrollment'})


@login_required
def enrollment_update(request, pk):
    return crud_update(request, Enrollment, pk, EnrollmentForm, 'dashboard/enrollments/form.html', 'dashboard:enrollment_list', {'title': 'Update Enrollment'})


@login_required
def enrollment_delete(request, pk):
    return crud_delete(request, Enrollment, pk, 'dashboard:enrollment_list')


# ==================== ATTENDANCE CRUD ====================

@login_required
def attendance_list(request):
    return crud_list(request, Attendance, 'dashboard/attendance/list.html', search_fields=['remark'])


@login_required
def attendance_create(request):
    return crud_create(request, AttendanceForm, 'dashboard/attendance/form.html', 'dashboard:attendance_list', {'title': 'Mark Attendance'})


@login_required
def attendance_update(request, pk):
    return crud_update(request, Attendance, pk, AttendanceForm, 'dashboard/attendance/form.html', 'dashboard:attendance_list', {'title': 'Update Attendance'})


@login_required
def attendance_delete(request, pk):
    return crud_delete(request, Attendance, pk, 'dashboard:attendance_list')


# ==================== EXAM CRUD ====================

@login_required
def exam_list(request):
    return crud_list(request, Exam, 'dashboard/exams/list.html', search_fields=['name'])


@login_required
def exam_create(request):
    return crud_create(request, ExamForm, 'dashboard/exams/form.html', 'dashboard:exam_list', {'title': 'Create New Exam'})


@login_required
def exam_update(request, pk):
    return crud_update(request, Exam, pk, ExamForm, 'dashboard/exams/form.html', 'dashboard:exam_list', {'title': 'Update Exam'})


@login_required
def exam_delete(request, pk):
    return crud_delete(request, Exam, pk, 'dashboard:exam_list')


# ==================== EXAM RESULT CRUD ====================

@login_required
def exam_result_list(request):
    return crud_list(request, ExamResult, 'dashboard/exam_results/list.html', search_fields=['grade', 'remarks'])


@login_required
def exam_result_create(request):
    return crud_create(request, ExamResultForm, 'dashboard/exam_results/form.html', 'dashboard:exam_result_list', {'title': 'Add Exam Result'})


@login_required
def exam_result_update(request, pk):
    return crud_update(request, ExamResult, pk, ExamResultForm, 'dashboard/exam_results/form.html', 'dashboard:exam_result_list', {'title': 'Update Exam Result'})


@login_required
def exam_result_delete(request, pk):
    return crud_delete(request, ExamResult, pk, 'dashboard:exam_result_list')


# ==================== FEE STRUCTURE CRUD ====================

@login_required
def fee_structure_list(request):
    return crud_list(request, FeeStructure, 'dashboard/fee_structures/list.html', search_fields=['name'])


@login_required
def fee_structure_create(request):
    return crud_create(request, FeeStructureForm, 'dashboard/fee_structures/form.html', 'dashboard:fee_structure_list', {'title': 'Add Fee Structure'})


@login_required
def fee_structure_update(request, pk):
    return crud_update(request, FeeStructure, pk, FeeStructureForm, 'dashboard/fee_structures/form.html', 'dashboard:fee_structure_list', {'title': 'Update Fee Structure'})


@login_required
def fee_structure_delete(request, pk):
    return crud_delete(request, FeeStructure, pk, 'dashboard:fee_structure_list')


# ==================== FEE PAYMENT CRUD ====================

@login_required
def fee_payment_list(request):
    return crud_list(request, FeePayment, 'dashboard/fee_payments/list.html', search_fields=['transaction_id', 'receipt_number'])


@login_required
def fee_payment_create(request):
    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, 'Fee payment recorded successfully!')
            return redirect('dashboard:fee_payment_receipt', pk=obj.pk)
    else:
        form = FeePaymentForm()
    return render(request, 'dashboard/fee_payments/form.html', {'form': form, 'title': 'Record Fee Payment'})


@login_required
def fee_payment_receipt(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk)
    return render(request, 'dashboard/fee_payments/receipt.html', {'payment': payment})


@login_required
def fee_payment_pdf(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk)
    school_name = getattr(request, 'school_name', None) or getattr(settings, 'SCHOOL_NAME', 'School ERP')
    return generate_fee_receipt_pdf(payment, school_name)


@login_required
def fee_payment_update(request, pk):
    return crud_update(request, FeePayment, pk, FeePaymentForm, 'dashboard/fee_payments/form.html', 'dashboard:fee_payment_list', {'title': 'Update Fee Payment'})


@login_required
def fee_payment_delete(request, pk):
    return crud_delete(request, FeePayment, pk, 'dashboard:fee_payment_list')


# ==================== LIBRARY BOOK CRUD ====================

@login_required
def library_book_list(request):
    return crud_list(request, LibraryBook, 'dashboard/library/list.html', search_fields=['title', 'author', 'isbn'])


@login_required
def library_book_create(request):
    return crud_create(request, LibraryBookForm, 'dashboard/library/form.html', 'dashboard:library_book_list', {'title': 'Add New Book'})


@login_required
def library_book_update(request, pk):
    return crud_update(request, LibraryBook, pk, LibraryBookForm, 'dashboard/library/form.html', 'dashboard:library_book_list', {'title': 'Update Book'})


@login_required
def library_book_delete(request, pk):
    return crud_delete(request, LibraryBook, pk, 'dashboard:library_book_list')


# ==================== BOOK ISSUE CRUD ====================

@login_required
def book_issue_list(request):
    return crud_list(request, BookIssue, 'dashboard/book_issues/list.html', search_fields=['book__title', 'student__first_name'])


@login_required
def book_issue_create(request):
    return crud_create(request, BookIssueForm, 'dashboard/book_issues/form.html', 'dashboard:book_issue_list', {'title': 'Issue Book'})


@login_required
def book_issue_update(request, pk):
    return crud_update(request, BookIssue, pk, BookIssueForm, 'dashboard/book_issues/form.html', 'dashboard:book_issue_list', {'title': 'Update Book Issue'})


@login_required
def book_issue_delete(request, pk):
    return crud_delete(request, BookIssue, pk, 'dashboard:book_issue_list')


@login_required
def book_return(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk)
    if request.method == 'POST':
        issue.return_date = timezone.now().date()
        issue.is_returned = True
        if issue.due_date < issue.return_date:
            days_overdue = (issue.return_date - issue.due_date).days
            issue.fine_amount = days_overdue * 5
        issue.save()
        book = issue.book
        book.available += 1
        book.save()
        messages.success(request, f'Book "{issue.book}" returned successfully!')
        return redirect('dashboard:book_issue_list')
    return render(request, 'dashboard/book_issues/return.html', {'issue': issue})


# ==================== EVENT CRUD ====================

@login_required
def event_list(request):
    return crud_list(request, Event, 'dashboard/events/list.html', search_fields=['title', 'venue'])


@login_required
def event_create(request):
    return crud_create(request, EventForm, 'dashboard/events/form.html', 'dashboard:event_list', {'title': 'Create Event'})


@login_required
def event_update(request, pk):
    return crud_update(request, Event, pk, EventForm, 'dashboard/events/form.html', 'dashboard:event_list', {'title': 'Update Event'})


@login_required
def event_delete(request, pk):
    return crud_delete(request, Event, pk, 'dashboard:event_list')


# ==================== NOTICE CRUD ====================

@login_required
def notice_list(request):
    return crud_list(request, Notice, 'dashboard/notices/list.html', search_fields=['title', 'content'])


@login_required
def notice_create(request):
    return crud_create(request, NoticeForm, 'dashboard/notices/form.html', 'dashboard:notice_list', {'title': 'Create Notice'})


@login_required
def notice_update(request, pk):
    return crud_update(request, Notice, pk, NoticeForm, 'dashboard/notices/form.html', 'dashboard:notice_list', {'title': 'Update Notice'})


@login_required
def notice_delete(request, pk):
    return crud_delete(request, Notice, pk, 'dashboard:notice_list')


# ==================== REPORTS ====================

@login_required
def reports_dashboard(request):
    return render(request, 'dashboard/reports/index.html')


@login_required
def report_students(request):
    students = Student.objects.filter(is_active=True)
    total = students.count()
    by_gender = students.values('gender').annotate(count=Count('id'))
    return render(request, 'dashboard/reports/students.html', {
        'students': students,
        'total': total,
        'by_gender': by_gender,
    })


@login_required
def report_attendance(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    monthly = Attendance.objects.filter(date__gte=month_start, date__lte=today)
    present = monthly.filter(status='present').count()
    absent = monthly.filter(status='absent').count()
    late = monthly.filter(status='late').count()
    total = present + absent + late
    return render(request, 'dashboard/reports/attendance.html', {
        'monthly': monthly,
        'present': present,
        'absent': absent,
        'late': late,
        'total': total,
    })


@login_required
def report_fees(request):
    payments = FeePayment.objects.filter(is_paid=True)
    total_collected = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    by_method = payments.values('payment_method').annotate(
        total=Sum('amount_paid'), count=Count('id')
    )
    return render(request, 'dashboard/reports/fees.html', {
        'payments': payments,
        'total_collected': total_collected,
        'by_method': by_method,
    })


@login_required
def report_exams(request):
    results = ExamResult.objects.all()
    avg_marks = results.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
    return render(request, 'dashboard/reports/exams.html', {
        'results': results,
        'avg_marks': avg_marks,
    })


# ==================== TRANSPORT CRUD ====================

@login_required
def vehicle_list(request):
    return crud_list(request, Vehicle, 'dashboard/transport/vehicle_list.html', search_fields=['vehicle_number', 'registration_number', 'driver_name'])


@login_required
def vehicle_create(request):
    return crud_create(request, VehicleForm, 'dashboard/transport/vehicle_form.html', 'dashboard:vehicle_list', {'title': 'Add Vehicle'})


@login_required
def vehicle_update(request, pk):
    return crud_update(request, Vehicle, pk, VehicleForm, 'dashboard/transport/vehicle_form.html', 'dashboard:vehicle_list', {'title': 'Update Vehicle'})


@login_required
def vehicle_delete(request, pk):
    return crud_delete(request, Vehicle, pk, 'dashboard:vehicle_list')


@login_required
def route_list(request):
    return crud_list(request, Route, 'dashboard/transport/route_list.html', search_fields=['name', 'route_code'])


@login_required
def route_create(request):
    return crud_create(request, RouteForm, 'dashboard/transport/route_form.html', 'dashboard:route_list', {'title': 'Add Route'})


@login_required
def route_update(request, pk):
    return crud_update(request, Route, pk, RouteForm, 'dashboard/transport/route_form.html', 'dashboard:route_list', {'title': 'Update Route'})


@login_required
def route_delete(request, pk):
    return crud_delete(request, Route, pk, 'dashboard:route_list')


@login_required
def stop_list(request):
    return crud_list(request, Stop, 'dashboard/transport/stop_list.html', search_fields=['name', 'landmark'])


@login_required
def stop_create(request):
    return crud_create(request, StopForm, 'dashboard/transport/stop_form.html', 'dashboard:stop_list', {'title': 'Add Stop'})


@login_required
def stop_update(request, pk):
    return crud_update(request, Stop, pk, StopForm, 'dashboard/transport/stop_form.html', 'dashboard:stop_list', {'title': 'Update Stop'})


@login_required
def stop_delete(request, pk):
    return crud_delete(request, Stop, pk, 'dashboard:stop_list')


@login_required
def transport_assignment_list(request):
    return crud_list(request, TransportAssignment, 'dashboard/transport/assignment_list.html', search_fields=['academic_year'])


@login_required
def transport_assignment_create(request):
    return crud_create(request, TransportAssignmentForm, 'dashboard/transport/assignment_form.html', 'dashboard:transport_assignment_list', {'title': 'Assign Transport'})


@login_required
def transport_assignment_update(request, pk):
    return crud_update(request, TransportAssignment, pk, TransportAssignmentForm, 'dashboard/transport/assignment_form.html', 'dashboard:transport_assignment_list', {'title': 'Update Assignment'})


@login_required
def transport_assignment_delete(request, pk):
    return crud_delete(request, TransportAssignment, pk, 'dashboard:transport_assignment_list')


# ==================== AJAX / JSON VIEWS ====================

def ajax_dashboard_stats(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    data = {
        'students': Student.objects.filter(is_active=True).count(),
        'teachers': Teacher.objects.filter(is_active=True).count(),
        'attendance_today': Attendance.objects.filter(date=today, status='present').count(),
        'fees_collected': float(FeePayment.objects.filter(is_paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0),
    }
    return JsonResponse(data)


def ajax_chart_data(request):
    today = timezone.now().date()
    labels = []
    student_data = []
    teacher_data = []
    for i in range(11, -1, -1):
        month = today.replace(day=1) - timedelta(days=30 * i)
        labels.append(month.strftime('%b %Y'))
        student_data.append(Student.objects.filter(created_at__month=month.month, created_at__year=month.year).count())
        teacher_data.append(Teacher.objects.filter(created_at__month=month.month, created_at__year=month.year).count())
    return JsonResponse({
        'labels': labels,
        'students': student_data,
        'teachers': teacher_data,
    })


def ajax_attendance_chart(request):
    today = timezone.now().date()
    days = []
    present_data = []
    absent_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        days.append(day.strftime('%a'))
        present_data.append(Attendance.objects.filter(date=day, status='present').count())
        absent_data.append(Attendance.objects.filter(date=day, status='absent').count())
    return JsonResponse({
        'days': days,
        'present': present_data,
        'absent': absent_data,
    })


# ==================== TIMETABLE ====================

@login_required
def timetable_list(request):
    queryset = TimeTable.objects.select_related('class_enrolled', 'subject', 'teacher').filter(is_active=True)
    class_id = request.GET.get('class')
    teacher_id = request.GET.get('teacher')
    if class_id:
        queryset = queryset.filter(class_enrolled_id=class_id)
    if teacher_id:
        queryset = queryset.filter(teacher_id=teacher_id)
    queryset, search_query = search_and_filter(request, queryset, ['class_enrolled__name', 'subject__name', 'teacher__first_name'])
    page_obj = paginate(request, queryset)
    return render(request, 'dashboard/timetable/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'classes': Class.objects.filter(is_active=True),
        'teachers': Teacher.objects.filter(is_active=True),
        'selected_class': int(class_id) if class_id else None,
        'selected_teacher': int(teacher_id) if teacher_id else None,
    })


@login_required
def timetable_class_view(request, pk):
    cls = get_object_or_404(Class, pk=pk)
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    timetable = {}
    for day in days:
        timetable[day] = TimeTable.objects.filter(class_enrolled=cls, day=day).select_related('subject', 'teacher').order_by('start_time')
    return render(request, 'dashboard/timetable/class_view.html', {
        'cls': cls, 'timetable': timetable, 'days': days,
    })


@login_required
def timetable_teacher_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    timetable = {}
    for day in days:
        timetable[day] = TimeTable.objects.filter(teacher=teacher, day=day).select_related('class_enrolled', 'subject').order_by('start_time')
    return render(request, 'dashboard/timetable/teacher_view.html', {
        'teacher': teacher, 'timetable': timetable, 'days': days,
    })


@login_required
def timetable_create(request):
    return crud_create(request, TimeTableForm, 'dashboard/timetable/form.html', 'dashboard:timetable_list', {'title': 'Add Timetable Entry'})


@login_required
def timetable_update(request, pk):
    return crud_update(request, TimeTable, pk, TimeTableForm, 'dashboard/timetable/form.html', 'dashboard:timetable_list', {'title': 'Update Timetable Entry'})


@login_required
def timetable_delete(request, pk):
    return crud_delete(request, TimeTable, pk, 'dashboard:timetable_list')


# ==================== YEAR PLAN ====================

@login_required
def year_plan_list(request):
    years = AcademicYear.objects.prefetch_related('terms').filter(is_active=True)
    return render(request, 'dashboard/year_plan/list.html', {'years': years})


@login_required
def year_plan_detail(request, pk):
    year = get_object_or_404(AcademicYear.objects.prefetch_related('terms'), pk=pk)
    events = Event.objects.filter(
        start_date__date__gte=year.start_date, end_date__date__lte=year.end_date, status=True, is_active=True
    ).order_by('start_date')
    return render(request, 'dashboard/year_plan/detail.html', {
        'year': year, 'events': events,
    })


@login_required
def year_plan_create(request):
    return crud_create(request, AcademicYearForm, 'dashboard/year_plan/form.html', 'dashboard:year_plan_list', {'title': 'Add Academic Year'})


@login_required
def year_plan_update(request, pk):
    return crud_update(request, AcademicYear, pk, AcademicYearForm, 'dashboard/year_plan/form.html', 'dashboard:year_plan_list', {'title': 'Update Academic Year'})


@login_required
def year_plan_delete(request, pk):
    return crud_delete(request, AcademicYear, pk, 'dashboard:year_plan_list')


# ==================== SUBJECT YEAR PLAN ====================

@login_required
def subject_year_plan_list(request):
    queryset = SubjectYearPlan.objects.select_related('subject', 'class_enrolled', 'term', 'academic_year').filter(is_active=True)
    class_id = request.GET.get('class')
    subject_id = request.GET.get('subject')
    year_id = request.GET.get('year')
    if class_id:
        queryset = queryset.filter(class_enrolled_id=class_id)
    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    if year_id:
        queryset = queryset.filter(academic_year_id=year_id)
    queryset, search_query = search_and_filter(request, queryset, ['topic', 'subject__name', 'class_enrolled__name'])
    page_obj = paginate(request, queryset)
    return render(request, 'dashboard/subject_year_plan/list.html', {
        'page_obj': page_obj, 'search_query': search_query,
        'classes': Class.objects.filter(is_active=True),
        'subjects': Subject.objects.filter(is_active=True),
        'years': AcademicYear.objects.filter(is_active=True),
        'selected_class': int(class_id) if class_id else None,
        'selected_subject': int(subject_id) if subject_id else None,
        'selected_year': int(year_id) if year_id else None,
    })


@login_required
def subject_year_plan_create(request):
    return crud_create(request, SubjectYearPlanForm, 'dashboard/subject_year_plan/form.html', 'dashboard:subject_year_plan_list', {'title': 'Add Subject Year Plan'})


@login_required
def subject_year_plan_update(request, pk):
    return crud_update(request, SubjectYearPlan, pk, SubjectYearPlanForm, 'dashboard/subject_year_plan/form.html', 'dashboard:subject_year_plan_list', {'title': 'Update Subject Year Plan'})


@login_required
def subject_year_plan_delete(request, pk):
    return crud_delete(request, SubjectYearPlan, pk, 'dashboard:subject_year_plan_list')
