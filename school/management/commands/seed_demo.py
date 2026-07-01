"""
Management command to seed the database with demo data for the School ERP system.
Usage: python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import date, timedelta
import random

from school.models import (
    Student, Teacher, Class as SchoolClass, Subject, Enrollment, Attendance,
    Exam, ExamResult, FeeStructure, FeePayment, LibraryBook, BookIssue,
    Event, Notice, UserProfile, TimeTable, Vehicle, Route, Stop, TransportAssignment,
    AcademicYear, Term, SubjectYearPlan
)


class Command(BaseCommand):
    help = 'Seeds the database with demo data for testing and presentation'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Seeding demo data...'))

        today = timezone.now().date()
        academic_year = f"{today.year}-{today.year + 1}"

        # Create academic year and terms
        year, _ = AcademicYear.objects.get_or_create(
            name=academic_year,
            defaults={'start_date': date(today.year, 4, 1), 'end_date': date(today.year + 1, 3, 31), 'is_current': True}
        )
        if _:
            term_data = [
                ('Term 1', date(today.year, 4, 1), date(today.year, 6, 30)),
                ('Term 2', date(today.year, 7, 15), date(today.year, 9, 30)),
                ('Term 3', date(today.year, 10, 15), date(today.year + 1, 3, 31)),
            ]
            for tname, tstart, tend in term_data:
                Term.objects.create(academic_year=year, name=tname, start_date=tstart, end_date=tend)
            self.stdout.write(self.style.SUCCESS(f'  Created academic year: {academic_year}'))

        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@school.edu', 'admin123')
            self.stdout.write(self.style.SUCCESS('  Created admin user (admin/admin123)'))

        # Create demo teacher users
        teacher_data = [
            ('john_doe', 'John', 'Doe', 'john@school.edu', 'Mathematics'),
            ('jane_smith', 'Jane', 'Smith', 'jane@school.edu', 'Physics'),
            ('bob_wilson', 'Bob', 'Wilson', 'bob@school.edu', 'English'),
            ('alice_brown', 'Alice', 'Brown', 'alice@school.edu', 'Chemistry'),
            ('charlie_davis', 'Charlie', 'Davis', 'charlie@school.edu', 'Computer Science'),
        ]

        teachers = []
        for username, fn, ln, email, spec in teacher_data:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'first_name': fn, 'last_name': ln, 'email': email}
            )
            if _:
                user.set_password('teacher123')
                user.save()
                UserProfile.objects.create(user=user, user_type='teacher')

            teacher, created = Teacher.objects.get_or_create(
                employee_id=f'TCH{username[:3].upper()}',
                defaults={
                    'first_name': fn, 'last_name': ln, 'email': email,
                    'phone': f'+1555{random.randint(1000000,9999999)}',
                    'date_of_birth': date(1980, random.randint(1, 12), random.randint(1, 28)),
                    'gender': random.choice(['male', 'female']),
                    'address': f'{random.randint(100,999)} Main St, Cityville',
                    'qualification': random.choice(['master', 'phd']),
                    'specialization': spec,
                    'joining_date': today - timedelta(days=random.randint(365, 2000)),
                    'salary': random.randint(40000, 90000),
                    'experience_years': random.randint(5, 20),
                }
            )
            if created:
                teacher.user = user
                teacher.save()
            teachers.append(teacher)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created teacher: {fn} {ln}'))

        # Create classes
        class_data = [
            ('Grade 1', 'GR1', None, 40),
            ('Grade 2', 'GR2', None, 40),
            ('Grade 3', 'GR3', None, 40),
            ('Grade 4', 'GR4', None, 40),
            ('Grade 5', 'GR5', None, 40),
            ('Grade 6', 'GR6', None, 40),
            ('Grade 7', 'GR7', None, 40),
            ('Grade 8', 'GR8', None, 40),
            ('Grade 9', 'GR9', None, 40),
            ('Grade 10', 'GR10', None, 40),
        ]

        classes = []
        for i, (name, code, _, cap) in enumerate(class_data):
            cls, created = SchoolClass.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'section': 'A',
                    'class_teacher': teachers[i % len(teachers)],
                    'capacity': cap,
                }
            )
            classes.append(cls)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created class: {name}'))

        # Create subjects
        subject_data = [
            ('Mathematics', 'MATH', True),
            ('English', 'ENG', False),
            ('Physics', 'PHY', True),
            ('Chemistry', 'CHEM', True),
            ('Biology', 'BIO', True),
            ('History', 'HIST', False),
            ('Geography', 'GEO', False),
            ('Computer Science', 'CS', True),
            ('Art', 'ART', False),
            ('Physical Education', 'PE', False),
        ]

        subjects = []
        for i, (name, code, is_lab) in enumerate(subject_data):
            subj, created = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'subject_teacher': teachers[i % len(teachers)],
                    'is_lab': is_lab,
                    'max_marks': 100,
                    'pass_marks': 40,
                }
            )
            if created:
                subj.classes.add(*random.sample(classes, random.randint(3, 6)))
            subjects.append(subj)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created subject: {name}'))

        # Create demo students
        first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason', 'Isabella', 'Logan']
        last_names = ['Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez']

        students = []
        for i in range(30):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            roll = f'STU{today.year}{i+1:04d}'
            email = f'{fn.lower()}.{ln.lower()}{i+1:02d}@student.edu'

            student, created = Student.objects.get_or_create(
                roll_number=roll,
                defaults={
                    'first_name': fn, 'last_name': ln, 'email': email,
                    'phone': f'+1555{random.randint(1000000,9999999)}',
                    'date_of_birth': date(2010, random.randint(1, 12), random.randint(1, 28)),
                    'gender': random.choice(['male', 'female']),
                    'address': f'{random.randint(100,999)} Student Ave, Cityville',
                    'city': 'Cityville', 'state': 'Stateland', 'zip_code': '10001',
                    'admission_date': today - timedelta(days=random.randint(30, 365)),
                    'guardian_name': f'{random.choice(last_names)} Parent',
                    'guardian_phone': f'+1555{random.randint(1000000,9999999)}',
                }
            )
            students.append(student)
            if created:
                # Enroll student in a random class
                Enrollment.objects.create(
                    student=student,
                    class_enrolled=random.choice(classes),
                    academic_year=academic_year,
                )
                self.stdout.write(self.style.SUCCESS(f'  Created student: {fn} {ln}'))

        # Create attendance records
        for student in students[:20]:
            for day_offset in range(30):
                day = today - timedelta(days=day_offset)
                if day.weekday() < 5:  # Weekdays only
                    Attendance.objects.get_or_create(
                        student=student,
                        date=day,
                        defaults={
                            'class_enrolled': random.choice(classes),
                            'status': random.choices(
                                ['present', 'present', 'present', 'absent', 'late', 'excused'],
                                weights=[50, 20, 15, 10, 3, 2]
                            )[0],
                            'marked_by': random.choice(teachers),
                        }
                    )

        self.stdout.write(self.style.SUCCESS('  Created attendance records'))

        # Create exams
        exam_types = ['midterm', 'final', 'quiz', 'test']
        for i, subj in enumerate(subjects[:5]):
            for exam_type in exam_types[:2]:
                exam_date = today + timedelta(days=random.randint(-60, 60))
                Exam.objects.get_or_create(
                    name=f"{subj.name} {exam_type.title()}",
                    exam_type=exam_type,
                    class_enrolled=random.choice(classes),
                    subject=subj,
                    date=exam_date,
                    defaults={
                        'start_time': timezone.now().replace(hour=9, minute=0).time(),
                        'end_time': timezone.now().replace(hour=11, minute=0).time(),
                        'total_marks': 100,
                    }
                )

        self.stdout.write(self.style.SUCCESS('  Created exams'))

        # Create subject year plans
        topics = [
            'Introduction & Overview', 'Unit 1: Fundamentals', 'Unit 2: Core Concepts',
            'Unit 3: Advanced Topics', 'Unit 4: Applications', 'Revision & Assessment',
        ]
        for cls in classes[:5]:
            for subj in subjects[:6]:
                for i, topic in enumerate(topics):
                    term = year.terms.all()[i % 3] if year.terms.all().count() >= 3 else None
                    SubjectYearPlan.objects.get_or_create(
                        academic_year=year, subject=subj, class_enrolled=cls,
                        topic=topic, term=term,
                        defaults={
                            'no_of_periods': random.randint(4, 10),
                            'start_date': term.start_date + timedelta(days=i * 15) if term else today + timedelta(days=i * 15),
                            'end_date': term.start_date + timedelta(days=i * 15 + 10) if term else today + timedelta(days=i * 15 + 10),
                            'is_completed': random.choice([True, False]),
                            'description': f'{topic} for {subj.name} - {cls.name}',
                        }
                    )
        self.stdout.write(self.style.SUCCESS('  Created subject year plans'))

        # Create timetable entries
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        periods = [
            (timezone.now().replace(hour=9, minute=0).time(), timezone.now().replace(hour=9, minute=50).time()),
            (timezone.now().replace(hour=9, minute=50).time(), timezone.now().replace(hour=10, minute=40).time()),
            (timezone.now().replace(hour=10, minute=50).time(), timezone.now().replace(hour=11, minute=40).time()),
            (timezone.now().replace(hour=11, minute=40).time(), timezone.now().replace(hour=12, minute=30).time()),
            (timezone.now().replace(hour=13, minute=0).time(), timezone.now().replace(hour=13, minute=50).time()),
            (timezone.now().replace(hour=13, minute=50).time(), timezone.now().replace(hour=14, minute=40).time()),
        ]
        rooms = ['101', '102', '103', '201', '202', 'Lab-1', 'Lab-2']
        for cls in classes[:5]:
            for i, day in enumerate(days[:5]):
                for pi, (start, end) in enumerate(periods[:4]):
                    subject = subjects[(i + pi) % len(subjects)]
                    teacher = subject.subject_teacher or random.choice(teachers)
                    TimeTable.objects.get_or_create(
                        class_enrolled=cls, day=day, start_time=start,
                        defaults={
                            'subject': subject, 'teacher': teacher,
                            'end_time': end, 'room_number': random.choice(rooms),
                        }
                    )
        self.stdout.write(self.style.SUCCESS('  Created timetable entries'))

        # Create fee structures (5 types per class)
        fee_type_config = {
            'tuition': {'amount': (5000, 15000), 'late_fee': 200, 'annual': False},
            'library': {'amount': (500, 1500), 'late_fee': 50, 'annual': True},
            'books': {'amount': (1000, 3000), 'late_fee': 100, 'annual': True},
            'admission': {'amount': (2000, 5000), 'late_fee': 0, 'annual': False},
            'transport': {'amount': (3000, 8000), 'late_fee': 150, 'annual': False},
        }
        for cls in classes:
            for fee_type, config in fee_type_config.items():
                FeeStructure.objects.get_or_create(
                    fee_type=fee_type,
                    class_enrolled=cls,
                    defaults={
                        'amount': random.randint(*config['amount']),
                        'due_date': today + timedelta(days=30),
                        'is_annual': config['annual'],
                        'late_fee': config['late_fee'],
                    }
                )

        self.stdout.write(self.style.SUCCESS('  Created fee structures'))

        # Create library books
        book_titles = [
            ('Introduction to Algebra', 'John Smith', '978-0-1234-5678-0'),
            ('World History', 'Jane Austen', '978-0-2345-6789-1'),
            ('Physics for Beginners', 'Albert Einstein', '978-0-3456-7890-2'),
            ('English Grammar Guide', 'William Shakespeare', '978-0-4567-8901-3'),
            ('Computer Programming 101', 'Alan Turing', '978-0-5678-9012-4'),
            ('Chemistry Fundamentals', 'Marie Curie', '978-0-6789-0123-5'),
            ('Biology Basics', 'Charles Darwin', '978-0-7890-1234-6'),
            ('Art History', 'Leonardo da Vinci', '978-0-8901-2345-7'),
        ]

        for title, author, isbn in book_titles:
            LibraryBook.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title, 'author': author,
                    'publisher': 'Academic Press',
                    'published_year': random.randint(2000, 2024),
                    'category': random.choice(['academic', 'reference', 'fiction', 'non-fiction']),
                    'quantity': random.randint(3, 10),
                    'available': random.randint(1, 8),
                }
            )

        self.stdout.write(self.style.SUCCESS('  Created library books'))

        # Create events
        event_data = [
            ('Annual Sports Day', 'sports', 'School Ground', 30),
            ('Science Exhibition', 'academic', 'Science Lab', 45),
            ('Cultural Fest', 'cultural', 'Auditorium', 60),
            ('Parent-Teacher Meeting', 'meeting', 'Conference Hall', 14),
            ('Summer Break', 'holiday', '-', 120),
        ]

        for title, etype, venue, days_ahead in event_data:
            Event.objects.get_or_create(
                title=title,
                defaults={
                    'description': f'{title} event description.',
                    'event_type': etype,
                    'start_date': timezone.now() + timedelta(days=days_ahead),
                    'end_date': timezone.now() + timedelta(days=days_ahead + 1),
                    'venue': venue,
                    'is_public': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('  Created events'))

        # Create notices
        notice_data = [
            ('Exam Schedule Published', 'high', 'Mid-term exams schedule is now available.'),
            ('School Holiday Notice', 'medium', 'School will remain closed on Friday.'),
            ('New Library Books Arrived', 'low', 'New books have been added to the library.'),
            ('Urgent: Staff Meeting', 'urgent', 'All staff are requested to attend the meeting.'),
        ]

        for title, priority, content in notice_data:
            Notice.objects.get_or_create(
                title=title,
                defaults={
                    'content': content,
                    'priority': priority,
                    'publish_date': today,
                    'expire_date': today + timedelta(days=30),
                }
            )

        self.stdout.write(self.style.SUCCESS('  Created notices'))

        # Create transport vehicles
        vehicle_data = [
            ('BUS-001', 'ABC-1234', 'Toyota Coaster', 30, 'Mike Driver', 'Diesel'),
            ('BUS-002', 'XYZ-5678', 'Ford Transit', 25, 'Sarah Driver', 'Diesel'),
            ('BUS-003', 'DEF-9012', 'Mercedes Sprinter', 20, 'Tom Driver', 'Diesel'),
            ('BUS-004', 'GHI-3456', 'Volvo B7R', 40, 'Lisa Driver', 'Diesel'),
        ]

        vehicles = []
        for vnum, reg, model, cap, driver, fuel in vehicle_data:
            v, created = Vehicle.objects.get_or_create(
                vehicle_number=vnum,
                defaults={
                    'registration_number': reg, 'model_name': model,
                    'capacity': cap, 'driver_name': driver,
                    'driver_phone': f'+1555{random.randint(1000000,9999999)}',
                    'driver_license': f'DL{random.randint(100000,999999)}',
                    'insurance_valid_until': today + timedelta(days=random.randint(30, 365)),
                    'last_maintenance_date': today - timedelta(days=random.randint(1, 90)),
                    'fuel_type': fuel,
                }
            )
            vehicles.append(v)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created vehicle: {vnum}'))

        # Create routes
        route_data = [
            ('Downtown Route', 'RT-01', 15.5, 150),
            ('Suburb Express', 'RT-02', 22.0, 200),
            ('East Side Route', 'RT-03', 18.0, 175),
            ('West End Route', 'RT-04', 12.0, 125),
        ]

        routes = []
        for i, (name, code, dist, fee) in enumerate(route_data):
            r, created = Route.objects.get_or_create(
                route_code=code,
                defaults={
                    'name': name, 'description': f'{name} description.',
                    'distance_km': dist, 'fee_amount': fee,
                    'vehicle': vehicles[i % len(vehicles)],
                }
            )
            routes.append(r)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created route: {code}'))

        # Create stops for each route
        stop_names = ['Main Gate', 'Downtown Square', 'Shopping Mall', 'Central Park',
                      'Train Station', 'Hospital', 'Community Center', 'Library']
        for route in routes:
            for i, sname in enumerate(random.sample(stop_names, 3), 1):
                Stop.objects.get_or_create(
                    route=route,
                    stop_order=i,
                    defaults={
                        'name': sname,
                        'address': f'{random.randint(100,999)} {sname} Rd',
                        'morning_pickup_time': timezone.now().replace(hour=7, minute=30 + (i-1) * 10).time(),
                        'evening_drop_time': timezone.now().replace(hour=15, minute=0 + (i-1) * 10).time(),
                    }
                )

        self.stdout.write(self.style.SUCCESS('  Created stops'))

        # Create transport assignments
        for student in students[:15]:
            route = random.choice(routes)
            stop = Stop.objects.filter(route=route).order_by('?').first()
            if stop:
                TransportAssignment.objects.get_or_create(
                    student=student,
                    academic_year=academic_year,
                    defaults={
                        'vehicle': route.vehicle or random.choice(vehicles),
                        'route': route,
                        'stop': stop,
                        'fee_amount': route.fee_amount,
                        'start_date': today - timedelta(days=30),
                    }
                )

        self.stdout.write(self.style.SUCCESS('  Created transport assignments'))

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  Students: {Student.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Teachers: {Teacher.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Classes: {SchoolClass.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Subjects: {Subject.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Vehicles: {Vehicle.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Routes: {Route.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.WARNING('Login: admin / admin123'))
