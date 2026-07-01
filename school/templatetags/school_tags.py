from django import template
from django.db.models import Sum, Count, Q
from school.models import (
    Student, Teacher, Attendance, FeePayment, LibraryBook, BookIssue, Event, Notice,
    Vehicle, Route, TransportAssignment
)
from django.utils import timezone

register = template.Library()


@register.simple_tag
def total_students():
    return Student.objects.filter(is_active=True, status=True).count()


@register.simple_tag
def total_teachers():
    return Teacher.objects.filter(is_active=True, status=True).count()


@register.simple_tag
def total_events():
    return Event.objects.filter(is_active=True, status=True, is_public=True).count()


@register.simple_tag
def total_notices():
    return Notice.objects.filter(is_active=True, status=True).count()


@register.simple_tag
def today_attendance():
    today = timezone.now().date()
    present = Attendance.objects.filter(date=today, status='present').count()
    total = Attendance.objects.filter(date=today).count()
    return {'present': present, 'total': total}


@register.simple_tag
def total_fees_collected():
    total = FeePayment.objects.filter(is_paid=True).aggregate(Sum('amount_paid'))
    return total['amount_paid__sum'] or 0


@register.simple_tag
def library_stats():
    total_books = LibraryBook.objects.filter(is_active=True).aggregate(Sum('quantity'))
    issued = BookIssue.objects.filter(is_returned=False).count()
    return {
        'total': total_books['quantity__sum'] or 0,
        'issued': issued,
    }


@register.simple_tag
def recent_notices(limit=5):
    return Notice.objects.filter(is_active=True, status=True)[:limit]


@register.simple_tag
def total_vehicles():
    return Vehicle.objects.filter(is_active=True, status=True).count()


@register.simple_tag
def total_routes():
    return Route.objects.filter(is_active=True, status=True).count()


@register.simple_tag
def active_transport_assignments():
    return TransportAssignment.objects.filter(is_active=True, status=True).count()


@register.simple_tag
def upcoming_events(limit=5):
    return Event.objects.filter(
        is_active=True, status=True, start_date__gte=timezone.now()
    )[:limit]


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
