# School ERP Management System

A comprehensive, production-ready School Enterprise Resource Planning (ERP) system built with Django 5.0, Bootstrap 5, and modern web technologies.

## Features

- **Authentication System**: Registration, Login, Password Reset, Profile Management
- **Public Website**: Hero section, About, Services, Gallery, Contact, Dark/Light mode
- **Admin Dashboard**: Statistics cards, Charts (Chart.js), Recent Activities, Sidebar navigation
- **Student Management**: CRUD, Search, Export (CSV/Excel/PDF), Profiles
- **Teacher Management**: CRUD, Search, Export, Profiles
- **Class Management**: Sections, Class Teachers, Capacity
- **Subject Management**: Lab settings, Pass/Fail marks, Subject-Teacher mapping
- **Enrollment Tracking**: Academic year, Student-Class mapping
- **Attendance System**: Daily marking, Status (Present/Absent/Late/Excused)
- **Exam Management**: Types, Schedule, Results with grade calculation
- **Fee Management**: Structures, Payments, Receipts, Payment methods
- **Library Management**: Books, Issues, Returns, Fine calculation
- **Event Management**: Types, Schedule, Public/Private
- **Notice Board**: Priority levels, Attachments, Target classes
- **Reporting**: Student, Attendance, Fees, Exam reports with Chart.js analytics
- **REST API**: Full CRUD API using Django REST Framework
- **Security**: CSRF, Authentication, Permission checks, Form validation
- **Responsive Design**: Mobile-first, Dark/Light mode toggle

## Tech Stack

- **Backend**: Django 5.0, Python 3.x
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Charts**: Chart.js 4.4
- **Icons**: Font Awesome 6.5
- **API**: Django REST Framework 3.15
- **PDF**: ReportLab
- **Excel**: OpenPyXL

## Installation

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd school-erp
   ```

2. **Create and activate virtual environment**
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (admin)**
   ```
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```
   python manage.py loaddata school/fixtures/sample_data.json
   ```

7. **Collect static files**
   ```
   python manage.py collectstatic
   ```

8. **Run development server**
   ```
   python manage.py runserver
   ```

9. **Access the application**
   - Website: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - Dashboard: http://127.0.0.1:8000/dashboard/
   - API: http://127.0.0.1:8000/dashboard/api/

## Default Login

- **Admin**: Create via `createsuperuser` command
- **Users**: Register via the registration page

## Project Structure

```
school-erp/
├── manage.py
├── requirements.txt
├── README.md
├── school_erp/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── school/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── api_views.py
│   ├── api_urls.py
│   ├── context_processors.py
│   ├── utils.py
│   ├── decorators.py
│   └── templatetags/
│       ├── __init__.py
│       └── school_tags.py
├── templates/
│   ├── base.html
│   ├── auth/
│   ├── public/
│   ├── dashboard/
│   └── includes/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/dashboard/api/students/` | List/Create students |
| GET/PUT/DELETE | `/dashboard/api/students/{id}/` | Retrieve/Update/Delete student |
| GET/POST | `/dashboard/api/teachers/` | List/Create teachers |
| GET/POST | `/dashboard/api/classes/` | List/Create classes |
| GET/POST | `/dashboard/api/subjects/` | List/Create subjects |
| GET/POST | `/dashboard/api/attendance/` | List/Create attendance |
| GET/POST | `/dashboard/api/exams/` | List/Create exams |
| GET/POST | `/dashboard/api/exam-results/` | List/Create exam results |
| GET/POST | `/dashboard/api/fee-structures/` | List/Create fee structures |
| GET/POST | `/dashboard/api/fee-payments/` | List/Create fee payments |
| GET/POST | `/dashboard/api/library-books/` | List/Create library books |
| GET/POST | `/dashboard/api/book-issues/` | List/Create book issues |
| GET/POST | `/dashboard/api/events/` | List/Create events |
| GET/POST | `/dashboard/api/notices/` | List/Create notices |
| GET/POST | `/dashboard/api/timetables/` | List/Create timetables |

## Export Options

- **CSV**: Export data to CSV format
- **Excel**: Export data to XLSX format
- **PDF**: Export data to PDF format with professional layout

## License

MIT License
