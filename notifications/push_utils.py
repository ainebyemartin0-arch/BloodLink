import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import PushSubscription
import logging

logger = logging.getLogger(__name__)

def send_push_notification(subscription, title, body, url='/donor/dashboard/'):
    """Send a single push notification to one subscription."""
    try:
        data = json.dumps({
            'title': title,
            'body': body,
            'url': url,
            'icon': '/static/images/bloodlink-icon.png',
            'badge': '/static/images/bloodlink-badge.png',
        })
        
        webpush(
            subscription_info={
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh_key,
                    'auth': subscription.auth_key,
                }
            },
            data=data,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                'sub': f'mailto:{settings.VAPID_CLAIMS_EMAIL}'
            }
        )
        return True
        
    except WebPushException as e:
        logger.error(f"Push notification failed: {e}")
        # If subscription is expired or invalid, deactivate it
        if e.response and e.response.status_code in [404, 410]:
            subscription.is_active = False
            subscription.save()
        return False
    except Exception as e:
        logger.error(f"Unexpected push error: {e}")
        return False


def send_emergency_push_alerts(emergency_request):
    """
    Send push notifications to all active subscriptions
    when an emergency blood request is created.
    Called alongside existing SMS system.
    """
    blood_type = emergency_request.blood_type_needed
    units = emergency_request.units_needed
    urgency = emergency_request.get_urgency_level_display()
    
    title = f"🩸 URGENT — {blood_type} Blood Needed!"
    body = (
        f"St. Francis Hospital Nsambya urgently needs "
        f"{units} unit(s) of {blood_type} blood. "
        f"Urgency: {urgency}. Please respond immediately."
    )
    url = '/donor/dashboard/'
    
    # Get all active donor subscriptions matching blood type
    donor_subscriptions = PushSubscription.objects.filter(
        is_active=True,
        donor__blood_type=blood_type,
        donor__is_available=True,
        donor__is_active=True
    )
    
    # Also notify ALL staff subscriptions
    staff_subscriptions = PushSubscription.objects.filter(
        is_active=True,
        staff_user__isnull=False
    )
    
    sent_count = 0
    failed_count = 0
    
    all_subscriptions = list(donor_subscriptions) + list(staff_subscriptions)
    
    for subscription in all_subscriptions:
        success = send_push_notification(subscription, title, body, url)
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    return {
        'sent': sent_count,
        'failed': failed_count,
        'total': len(all_subscriptions)
    }
