from django.conf import settings


def school_settings(request):
    return {
        'SCHOOL_NAME': settings.SCHOOL_NAME,
        'SCHOOL_TAGLINE': settings.SCHOOL_TAGLINE,
        'SCHOOL_ADDRESS': settings.SCHOOL_ADDRESS,
        'SCHOOL_PHONE': settings.SCHOOL_PHONE,
        'SCHOOL_EMAIL': settings.SCHOOL_EMAIL,
        'SCHOOL_LOGO': settings.SCHOOL_LOGO,
    }
