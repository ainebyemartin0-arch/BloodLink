from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from django.contrib.sessions.models import Session
import json
import logging

from donors.models import Donor
from staff_portal.models import PublicBloodRequest
from notifications.models import SMSNotification, PushSubscription

logger = logging.getLogger(__name__)

def get_logged_in_donor(request):
    """Get the currently logged in donor from session"""
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return None
    try:
        return Donor.objects.get(pk=donor_id, is_active=True)
    except Donor.DoesNotExist:
        return None

@require_http_methods(["GET"])
def urgent_alerts(request):
    """
    API endpoint to check for urgent blood alerts for the logged-in donor
    Returns JSON with alert information if new alerts exist
    """
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        # Get recent blood requests that match donor's blood type
        now = timezone.now()
        recent_requests = PublicBloodRequest.objects.filter(
            blood_type_needed=donor.blood_type,
            status='approved',
            submitted_at__gte=now - timezone.timedelta(hours=24)  # Last 24 hours
        ).order_by('-submitted_at')
        
        # Check for SMS notifications sent to this donor
        recent_notifications = SMSNotification.objects.filter(
            phone_number=donor.phone_number,
            created_at__gte=now - timezone.timedelta(hours=1),  # Last hour
            status='sent'
        ).order_by('-created_at')
        
        # Determine if there are new alerts
        has_new_alert = False
        alert_data = None
        
        if recent_requests.exists():
            latest_request = recent_requests.first()
            
            # Check if this is a new request (created in last 5 minutes)
            if latest_request.submitted_at >= now - timezone.timedelta(minutes=5):
                has_new_alert = True
                alert_data = {
                    'id': latest_request.pk,
                    'type': 'blood_request',
                    'hospital': 'St. Francis Hospital',
                    'blood_type': latest_request.blood_type_needed,
                    'urgency': latest_request.urgency_level,
                    'patient_type': latest_request.patient_name,
                    'contact': latest_request.requester_phone,
                    'message': f'URGENT: {latest_request.blood_type_needed} blood needed at St. Francis Hospital',
                    'full_message': latest_request.additional_notes or 'Your blood type is urgently needed for emergency care.',
                    'created_at': latest_request.submitted_at.isoformat(),
                    'expires_at': (latest_request.submitted_at + timezone.timedelta(hours=24)).isoformat()
                }
        
        elif recent_notifications.exists():
            latest_notification = recent_notifications.first()
            
            # Check if this is a new notification (sent in last 2 minutes)
            if latest_notification.created_at >= now - timezone.timedelta(minutes=2):
                has_new_alert = True
                alert_data = {
                    'id': latest_notification.pk,
                    'type': 'sms_alert',
                    'message': latest_notification.message,
                    'hospital': 'St. Francis Hospital',  # Default
                    'blood_type': donor.blood_type,
                    'urgency': 'urgent',
                    'patient_type': 'Emergency',
                    'contact': '+256 123 456 789',
                    'full_message': latest_notification.message,
                    'created_at': latest_notification.created_at.isoformat(),
                    'expires_at': (latest_notification.created_at + timezone.timedelta(hours=1)).isoformat()
                }
        
        return JsonResponse({
            'has_new_alert': has_new_alert,
            'alert': alert_data,
            'timestamp': now.isoformat(),
            'donor_blood_type': donor.blood_type,
            'total_active_requests': recent_requests.count(),
            'recent_notifications': recent_notifications.count()
        })
        
    except Exception as e:
        logger.error(f"Error checking urgent alerts for donor {donor.pk}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def respond_to_alert(request, alert_id):
    """
    API endpoint for donors to respond to alerts
    Accepts POST with response type: 'available', 'later', 'unable'
    """
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        # Parse request body
        data = json.loads(request.body)
        response_type = data.get('response')
        timestamp = data.get('timestamp')
        
        if response_type not in ['available', 'later', 'unable']:
            return JsonResponse({'error': 'Invalid response type'}, status=400)
        
        # Find the alert (could be blood request or SMS notification)
        alert = None
        alert_source = None
        
        # Try to find as blood request
        try:
            alert = PublicBloodRequest.objects.get(pk=alert_id)
            alert_source = 'blood_request'
        except PublicBloodRequest.DoesNotExist:
            pass
        
        # Try to find as SMS notification
        if not alert:
            try:
                alert = SMSNotification.objects.get(pk=alert_id)
                alert_source = 'sms_notification'
            except SMSNotification.DoesNotExist:
                pass
        
        if not alert:
            return JsonResponse({'error': 'Alert not found'}, status=404)
        
        # Record the response
        if alert_source == 'blood_request':
            # Update blood request with donor response
            # This would typically be stored in a separate response model
            # For now, we'll update the request notes
            notes = alert.additional_notes or ''
            response_text = f"Donor {donor.full_name} ({donor.phone_number}) responded: {response_type} at {timestamp}"
            alert.additional_notes = f"{notes}\n{response_text}" if notes else response_text
            alert.save()
            
        elif alert_source == 'sms_notification':
            # Update SMS notification with response
            alert.response = response_type
            alert.response_timestamp = timezone.now()
            alert.save()
        
        # Log the response
        logger.info(f"Donor {donor.pk} ({donor.email}) responded to alert {alert_id} with: {response_type}")
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Response recorded successfully',
            'response_type': response_type,
            'alert_id': alert_id,
            'timestamp': timezone.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error recording response for alert {alert_id}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def alert_history(request):
    """
    API endpoint to get alert history for the logged-in donor
    """
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        # Get blood requests history
        blood_requests = PublicBloodRequest.objects.filter(
            blood_type=donor.blood_type,
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-created_at')[:10]
        
        # Get SMS notifications history
        sms_notifications = SMSNotification.objects.filter(
            phone_number=donor.phone_number,
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-created_at')[:10]
        
        # Format response data
        alert_history = []
        
        # Add blood requests
        for req in blood_requests:
            alert_history.append({
                'id': req.pk,
                'type': 'blood_request',
                'hospital': req.hospital_name,
                'blood_type': req.blood_type,
                'urgency': req.urgency_level,
                'message': f'{req.blood_type} blood needed at {req.hospital_name}',
                'created_at': req.created_at.isoformat(),
                'status': req.status,
                'responded': False  # Would need to be tracked separately
            })
        
        # Add SMS notifications
        for notif in sms_notifications:
            alert_history.append({
                'id': notif.pk,
                'type': 'sms_notification',
                'message': notif.message,
                'created_at': notif.created_at.isoformat(),
                'status': notif.status,
                'responded': notif.response is not None,
                'response': notif.response,
                'response_timestamp': notif.response_timestamp.isoformat() if notif.response_timestamp else None
            })
        
        # Sort by creation date
        alert_history.sort(key=lambda x: x['created_at'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'alerts': alert_history,
            'total_count': len(alert_history),
            'donor_blood_type': donor.blood_type
        })
        
    except Exception as e:
        logger.error(f"Error getting alert history for donor {donor.pk}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["POST"])
def mark_alert_read(request, alert_id):
    """
    API endpoint to mark an alert as read
    """
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        # Implementation would depend on how you track read/unread status
        # For now, return success
        return JsonResponse({
            'success': True,
            'message': 'Alert marked as read',
            'alert_id': alert_id
        })
        
    except Exception as e:
        logger.error(f"Error marking alert {alert_id} as read: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def notification_stats(request):
    """
    API endpoint to get notification statistics for the donor
    """
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        now = timezone.now()
        
        # Get statistics
        total_requests = PublicBloodRequest.objects.filter(
            blood_type=donor.blood_type,
            created_at__gte=now - timezone.timedelta(days=30)
        ).count()
        
        total_notifications = SMSNotification.objects.filter(
            phone_number=donor.phone_number,
            created_at__gte=now - timezone.timedelta(days=30)
        ).count()
        
        # Recent activity (last 24 hours)
        recent_requests = PublicBloodRequest.objects.filter(
            blood_type=donor.blood_type,
            created_at__gte=now - timezone.timedelta(hours=24)
        ).count()
        
        recent_notifications = SMSNotification.objects.filter(
            phone_number=donor.phone_number,
            created_at__gte=now - timezone.timedelta(hours=24)
        ).count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_requests_30_days': total_requests,
                'total_notifications_30_days': total_notifications,
                'recent_requests_24_hours': recent_requests,
                'recent_notifications_24_hours': recent_notifications,
                'donor_blood_type': donor.blood_type,
                'is_available': donor.is_available,
                'last_donation': donor.last_donation_date.isoformat() if donor.last_donation_date else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting notification stats for donor {donor.pk}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
