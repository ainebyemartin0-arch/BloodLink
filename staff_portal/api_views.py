from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import EmergencyRequest
from notifications.models import SMSNotification
from donors.models import Donor
import json

@require_http_methods(["GET"])
@login_required
def check_notifications(request):
    """Check for new notifications and return them as JSON"""
    notifications = []
    
    # Check for new emergency requests
    recent_requests = EmergencyRequest.objects.filter(
        created_at__gte=timezone.now() - timedelta(minutes=5),
        status='open'
    ).order_by('-created_at')
    
    for req in recent_requests:
        notifications.append({
            'type': 'danger',
            'title': f'🚨 Emergency Blood Request',
            'message': f'{req.units_needed} units of {req.blood_type_needed} blood needed urgently in {req.ward}',
            'sound': 'urgent',
            'urgent': True,
            'duration': 0,
            'actions': [
                {
                    'text': 'View Request',
                    'type': 'primary',
                    'action': 'redirect',
                    'url': f'/staff/requests/{req.pk}/'
                }
            ]
        })
    
    # Check for donor responses
    recent_responses = SMSNotification.objects.filter(
        donor_response__in=['confirmed', 'declined'],
        opened_at__gte=timezone.now() - timedelta(minutes=10)
    ).order_by('-opened_at')
    
    for sms in recent_responses:
        response_type = '✅ Confirmed' if sms.donor_response == 'confirmed' else '❌ Declined'
        notification_type = 'success' if sms.donor_response == 'confirmed' else 'warning'
        
        notifications.append({
            'type': notification_type,
            'title': f'Donor Response: {response_type}',
            'message': f'{sms.donor.full_name} has {sms.donor_response} the blood donation request',
            'sound': 'success' if sms.donor_response == 'confirmed' else 'warning',
            'actions': [
                {
                    'text': 'View Donor',
                    'type': 'primary',
                    'action': 'redirect',
                    'url': f'/staff/donors/{sms.donor.pk}/'
                },
                {
                    'text': 'View SMS',
                    'type': 'secondary',
                    'action': 'redirect',
                    'url': f'/notifications/#sms-{sms.pk}'
                }
            ]
        })
    
    return JsonResponse({
        'notifications': notifications,
        'count': len(notifications)
    })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def mark_notification_read(request):
    """Mark a notification as read"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        # Here you would typically mark the notification as read in your database
        # For now, we'll just return success
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clear_session_notification(request):
    """Clear emergency notification from session"""
    try:
        if 'emergency_notification' in request.session:
            del request.session['emergency_notification']
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["GET"])
@login_required
def get_system_stats(request):
    """Get system statistics for dashboard notifications"""
    stats = {
        'total_donors': Donor.objects.count(),
        'available_donors': Donor.objects.filter(is_available=True, is_active=True).count(),
        'open_requests': EmergencyRequest.objects.filter(status='open').count(),
        'pending_sms': SMSNotification.objects.filter(donor_response='no_response').count(),
        'confirmed_today': SMSNotification.objects.filter(
            donor_response='confirmed',
            opened_at__date=timezone.now().date()
        ).count()
    }
    
    return JsonResponse(stats)
