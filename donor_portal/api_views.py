from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .views import get_logged_in_donor
from .views import donor_login_required
from notifications.models import SMSNotification
from django.utils import timezone
from datetime import timedelta
import json

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

@require_http_methods(["POST"])
def toggle_availability(request):
    """Toggle donor availability status"""
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    try:
        import json
        data = json.loads(request.body)
        available = data.get('available', False)
        
        donor.is_available = available
        donor.save()
        
        return JsonResponse({
            'success': True,
            'available': donor.is_available,
            'message': 'Availability updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@donor_login_required
@require_http_methods(["POST"])
def respond_to_alert(request, alert_id):
    """Handle donor response to SMS alerts"""
    try:
        donor = get_logged_in_donor(request)
        alert = get_object_or_404(SMSNotification, id=alert_id, donor=donor)
        
        # Parse response data
        data = json.loads(request.body)
        response = data.get('response')  # 'confirmed' or 'declined'
        
        if response not in ['confirmed', 'declined']:
            return JsonResponse({'success': False, 'error': 'Invalid response'}, status=400)
        
        # Update alert
        alert.donor_response = response
        alert.responded_at = timezone.now()
        alert.save()
        
        # Update donor availability if confirmed
        if response == 'confirmed':
            donor.is_available = True
            donor.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Alert {response} successfully',
            'alert_id': alert_id,
            'response': response
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@donor_login_required
@require_http_methods(["GET"])
def get_alerts_list(request):
    """Get all alerts for donor"""
    try:
        donor = get_logged_in_donor(request)
        
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        status = request.GET.get('status', 'all')  # 'all', 'pending', 'confirmed', 'declined', 'read'
        
        # Filter alerts
        alerts = SMSNotification.objects.filter(donor=donor)
        
        if status != 'all':
            if status == 'pending':
                alerts = alerts.filter(donor_response='no_response', is_fulfilled=False)
            else:
                alerts = alerts.filter(donor_response=status)
        
        # Order by sent date
        alerts = alerts.order_by('-sent_at')
        
        # Pagination
        total = alerts.count()
        start = (page - 1) * limit
        end = start + limit
        alerts_page = alerts[start:end]
        
        # Format alerts
        alerts_data = []
        for alert in alerts_page:
            alert_type = 'info'
            if alert.emergency_request and alert.emergency_request.urgency_level == 'critical':
                alert_type = 'urgent'
            elif alert.emergency_request and alert.emergency_request.urgency_level == 'urgent':
                alert_type = 'normal'
            
            alerts_data.append({
                'id': alert.id,
                'type': alert_type,
                'title': alert.emergency_request.patient_name if alert.emergency_request else 'Notification',
                'content': alert.message,
                'time': alert.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                'time_ago': get_time_ago(alert.sent_at),
                'status': 'pending' if alert.donor_response == 'no_response' else alert.donor_response,
                'is_fulfilled': alert.is_fulfilled,
                'emergency_request_id': alert.emergency_request.id if alert.emergency_request else None
            })
        
        return JsonResponse({
            'success': True,
            'alerts': alerts_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def get_time_ago(dt):
    """Get human-readable time ago string"""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
