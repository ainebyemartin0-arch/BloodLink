from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .views import get_logged_in_donor
from notifications.models import SMSNotification
from django.utils import timezone
from datetime import timedelta

@require_http_methods(["GET"])
def urgent_alerts(request):
    """Get urgent SMS alerts for logged-in donor"""
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'alerts': [], 'count': 0})
    
    alerts = []
    
    # Check for unread urgent SMS alerts
    urgent_sms = SMSNotification.objects.filter(
        donor=donor,
        donor_response='no_response',
        emergency_request__urgency_level='critical',
        sent_at__gte=timezone.now() - timedelta(hours=2)
    ).order_by('-sent_at')
    
    for sms in urgent_sms:
        alerts.append({
            'title': '🚨 Urgent Blood Donation Request',
            'message': f'{sms.emergency_request.units_needed} units of {sms.emergency_request.blood_type_needed} blood needed urgently in {sms.emergency_request.ward}. Your blood type matches!',
            'url': f'/donor/dashboard/#alert-{sms.pk}',
            'sound': 'urgent',
            'urgent': True
        })
    
    # Check for recent confirmed requests (for acknowledgment)
    confirmed_sms = SMSNotification.objects.filter(
        donor=donor,
        donor_response='confirmed',
        opened_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-opened_at')
    
    for sms in confirmed_sms[:1]:  # Only show the most recent confirmation
        alerts.append({
            'title': '✅ Thank You for Your Response!',
            'message': f'Your confirmation for blood donation has been received. The hospital will contact you soon.',
            'url': f'/donor/dashboard/',
            'sound': 'success',
            'urgent': False
        })
    
    return JsonResponse({
        'alerts': alerts,
        'count': len(alerts)
    })

@require_http_methods(["GET"])
def notification_stats(request):
    """Get notification statistics for donor dashboard"""
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    stats = {
        'total_alerts': donor.sms_notifications.count(),
        'unread_alerts': donor.sms_notifications.filter(donor_response='no_response').count(),
        'confirmed_alerts': donor.sms_notifications.filter(donor_response='confirmed').count(),
        'declined_alerts': donor.sms_notifications.filter(donor_response='declined').count(),
        'opened_today': donor.sms_notifications.filter(
            opened_at__date=timezone.now().date()
        ).count()
    }
    
    return JsonResponse(stats)
