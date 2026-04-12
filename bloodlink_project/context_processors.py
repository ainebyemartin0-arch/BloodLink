def admin_custom_context(request):
    """
    Custom context processor to handle Python 3.14 compatibility issues
    with Django admin template context copying.
    """
    return {
        'admin_custom_context': True,
    }

from django.conf import settings

def vapid_context(request):
    return {
        'VAPID_PUBLIC_KEY': getattr(settings, 'VAPID_PUBLIC_KEY', '')
    }
