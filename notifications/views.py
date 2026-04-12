from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import SMSNotification, PushSubscription
from .utils import test_africastalking_connection
from .push_utils import send_emergency_push_alerts

@login_required
def notification_list(request):
    notifications = SMSNotification.objects.select_related('donor', 'emergency_request').all()
    
    # Filter options
    status_filter = request.GET.get('status', '')
    response_filter = request.GET.get('response', '')
    opened_filter = request.GET.get('opened', '')
    
    if status_filter:
        notifications = notifications.filter(delivery_status=status_filter)
    if response_filter:
        notifications = notifications.filter(donor_response=response_filter)
    if opened_filter == 'opened':
        notifications = notifications.filter(opened_at__isnull=False)
    elif opened_filter == 'not_opened':
        notifications = notifications.filter(opened_at__isnull=True)
    
    # Calculate statistics
    total = SMSNotification.objects.count()
    sent = SMSNotification.objects.filter(delivery_status='sent').count()
    delivered = SMSNotification.objects.filter(delivery_status='delivered').count()
    failed = SMSNotification.objects.filter(delivery_status='failed').count()
    opened = SMSNotification.objects.filter(opened_at__isnull=False).count()
    confirmed = SMSNotification.objects.filter(donor_response='confirmed').count()
    sent_delivered = sent + delivered
    
    context = {
        'notifications': notifications,
        'total': total,
        'sent': sent,
        'delivered': delivered,
        'failed': failed,
        'opened': opened,
        'confirmed': confirmed,
        'sent_delivered': sent_delivered,
        'status_filter': status_filter,
        'response_filter': response_filter,
        'opened_filter': opened_filter,
    }
    return render(request, 'notifications/enhanced_list.html', context)

@login_required
def update_response(request, pk):
    if request.method == 'POST':
        notification = get_object_or_404(SMSNotification, pk=pk)
        new_response = request.POST.get('response')
        if new_response in ['confirmed', 'declined', 'no_response']:
            notification.donor_response = new_response
            notification.save()
            messages.success(request, f"Response updated to: {notification.get_donor_response_display()}")
        return redirect('notifications:list')
    return redirect('notifications:list')

@login_required
def test_connection(request):
    """Test Africa's Talking API connection and return JSON response."""
    result = test_africastalking_connection()
    return JsonResponse(result)

def test_sms_api(request):
    """Public test endpoint for Africa's Talking API."""
    result = test_africastalking_connection()
    return JsonResponse(result)


@require_POST
def push_subscribe(request):
    """Save a push notification subscription from browser."""
    try:
        data = json.loads(request.body)
        
        endpoint = data.get('endpoint')
        p256dh = data.get('p256dh')
        auth = data.get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return JsonResponse({'error': 'Missing fields'}, status=400)
        
        # Get donor from session or staff from Django auth
        donor = None
        staff_user = None
        
        donor_id = request.session.get('donor_id')
        if donor_id:
            from donors.models import Donor
            try:
                donor = Donor.objects.get(pk=donor_id)
            except Donor.DoesNotExist:
                pass
        
        if request.user.is_authenticated:
            staff_user = request.user
        
        # Save or update subscription
        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'p256dh_key': p256dh,
                'auth_key': auth,
                'donor': donor,
                'staff_user': staff_user,
                'is_active': True,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:300],
            }
        )
        
        return JsonResponse({
            'success': True,
            'created': created,
            'message': 'Subscribed to BloodLink alerts successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def push_unsubscribe(request):
    """Remove a push notification subscription."""
    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        
        PushSubscription.objects.filter(
            endpoint=endpoint
        ).update(is_active=False)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
