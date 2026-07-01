from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You need admin permissions to access this page.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'You need staff permissions to access this page.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper
