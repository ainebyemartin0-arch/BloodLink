from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import SMSNotification
from .utils import check_sms_delivery_status

@csrf_exempt
@require_POST
def check_delivery_status(request, notification_id):
    """API endpoint to check delivery status for a specific notification"""
    try:
        notification = get_object_or_404(SMSNotification, pk=notification_id)
        
        # Check the delivery status using our enhanced function
        check_sms_delivery_status()
        
        # Get updated notification
        updated_notification = SMSNotification.objects.get(pk=notification_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Delivery status checked for notification #{notification_id}',
            'delivery_status': updated_notification.delivery_status,
            'delivered_at': updated_notification.delivered_at.isoformat() if updated_notification.delivered_at else None,
            'opened_at': updated_notification.opened_at.isoformat() if updated_notification.opened_at else None,
            'status_display': updated_notification.get_delivery_status_display()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error checking delivery status: {str(e)}'
        })
