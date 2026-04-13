from .models import ActivityLog

def log_activity(request, action, description, 
                 donor_id=None, request_id=None):
    """
    Helper function to log staff activities.
    Call this after important actions in views.
    """
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        ActivityLog.objects.create(
            staff_user=request.user if request.user.is_authenticated else None,
            action=action,
            description=description,
            ip_address=ip,
            related_donor_id=donor_id,
            related_request_id=request_id,
        )
    except Exception:
        pass  # Never let logging crash the main action
