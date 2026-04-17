import africastalking
from django.conf import settings
from donors.models import Donor
from .models import SMSNotification

def format_phone_uganda(phone_number):
    """Convert any Uganda phone format to international +256 format."""
    phone = phone_number.strip().replace(' ', '').replace('-', '')
    if phone.startswith('+256'):
        return phone
    if phone.startswith('256'):
        return '+' + phone
    if phone.startswith('0'):
        return '+256' + phone[1:]
    return '+256' + phone

def test_africastalking_connection():
    """Test Africa's Talking API connection."""
    try:
        africastalking.initialize(
            username=settings.AT_USERNAME,
            api_key=settings.AT_API_KEY
        )
        
        # For sandbox, we'll test by checking if we can initialize the service
        if settings.AT_USERNAME == 'sandbox':
            return {
                'success': True,
                'status': 'Sandbox Mode',
                'message': 'Sandbox credentials detected - SMS will work in sandbox mode',
                'username': 'sandbox',
                'note': 'To send real SMS, update AT_USERNAME to your live username'
            }
        
        # For live credentials, test by sending a simple SMS
        sms = africastalking.SMS
        test_message = "BloodLink SMS API Test - Connection successful!"
        test_phone = "+256700000000"  # Test number
        
        response = sms.send(test_message, [test_phone], sender_id=settings.AT_SENDER_ID)
        
        if response and 'SMSMessageData' in response:
            recipients = response['SMSMessageData'].get('Recipients', [])
            if recipients:
                recipient_data = recipients[0]
                status = recipient_data.get('status', 'failed')
                
                return {
                    'success': status == 'Success',
                    'status': status,
                    'message_id': recipient_data.get('messageId', ''),
                    'cost': recipient_data.get('cost', 'UGX 0'),
                    'username': settings.AT_USERNAME,
                    'test_response': response
                }
            else:
                return {'success': False, 'error': 'No recipients in response', 'response': response}
        else:
            return {'success': False, 'error': 'Invalid response from API', 'response': response}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def check_sms_delivery_status():
    """Check delivery status of sent SMS messages and update accordingly."""
    from .models import SMSNotification
    from django.utils import timezone
    from datetime import timedelta
    
    # Check SMS sent in the last 24 hours that are still marked as 'sent'
    cutoff_time = timezone.now() - timedelta(hours=24)
    pending_notifications = SMSNotification.objects.filter(
        delivery_status='sent',
        sent_at__gte=cutoff_time,
        at_message_id__isnull=False  # Only check those with message IDs
    ).select_related('donor')
    
    for notification in pending_notifications:
        try:
            # Initialize Africa's Talking
            africastalking.initialize(
                username=settings.AT_USERNAME,
                api_key=settings.AT_API_KEY
            )
            sms_service = africastalking.SMS
            
            # Check delivery status
            response = sms_service.check_delivery_status(notification.at_message_id)
            
            if response and 'data' in response:
                delivery_data = response['data']
                if isinstance(delivery_data, list) and delivery_data:
                    status_info = delivery_data[0]
                    delivery_status = status_info.get('status', '').lower()
                    
                    # Update notification based on actual delivery status
                    if delivery_status in ['delivered', 'success']:
                        notification.delivery_status = 'delivered'
                        notification.delivered_at = timezone.now()
                        print(f"DELIVERED SMS to {notification.donor.full_name} was delivered")
                    elif delivery_status in ['failed', 'rejected']:
                        notification.delivery_status = 'failed'
                        print(f"FAILED SMS to {notification.donor.full_name} failed: {delivery_status}")
                    elif delivery_status in ['submitted', 'sent', 'queued']:
                        # Still pending, keep as 'sent'
                        print(f"PENDING SMS to {notification.donor.full_name} is still pending: {delivery_status}")
                    
                    notification.save()
                    
        except Exception as e:
            print(f"Error checking delivery status for {notification.donor.full_name}: {str(e)}")

def send_emergency_sms(emergency_request):
    """
    Send SMS alerts to all matching available donors.
    Returns dict with sent_count and failed_count.
    """
    result = {'sent_count': 0, 'failed_count': 0, 'total_matched': 0}
    
    try:
        # Initialize Africa's Talking
        africastalking.initialize(
            username=settings.AT_USERNAME,
            api_key=settings.AT_API_KEY
        )
        sms_service = africastalking.SMS
        
        # Define priority locations (within 10km radius)
        priority_locations = ['Nsambya', 'Kabalagala', 'Namuwongo', 'Makindye', 'Kibuli']
        
        # Find all matching available donors
        matching_donors = Donor.objects.filter(
            blood_type=emergency_request.blood_type_needed,
            is_available=True,
            is_active=True
        )
        
        # Separate priority and other donors
        priority_donors = matching_donors.filter(location__in=priority_locations)
        other_donors = matching_donors.exclude(location__in=priority_locations)
        
        # Combine: priority donors first, then others
        ordered_donors = list(priority_donors) + list(other_donors)
        
        result['total_matched'] = matching_donors.count()
        result['priority_count'] = priority_donors.count()
        result['other_count'] = other_donors.count()
        
        if matching_donors.count() == 0:
            print(f"No matching donors found for blood type {emergency_request.blood_type_needed}")
            return result
        
        # Build message
        urgency_text = emergency_request.get_urgency_level_display()
        message = (
            f"BLOODLINK ALERT - St. Francis Hospital Nsambya urgently needs "
            f"{emergency_request.units_needed} unit(s) of {emergency_request.blood_type_needed} blood. "
            f"Urgency: {urgency_text}. "
            f"Please report to blood bank immediately if you are available. "
            f"Thank you for saving a life! - BloodLink"
        )
        
        print(f"Sending SMS to {len(ordered_donors)} donors with blood type {emergency_request.blood_type_needed}")
        print(f"Priority donors: {result['priority_count']}, Other donors: {result['other_count']}")
        
        for donor in ordered_donors:
            # Create notification record first
            notification = SMSNotification.objects.create(
                emergency_request=emergency_request,
                donor=donor,
                message_content=message,
                delivery_status='pending'
            )
            
            try:
                phone = format_phone_uganda(donor.phone_number)
                print(f"Sending SMS to {donor.full_name} at {phone}")
            except Exception as e:
                print(f"Error formatting phone number: {e}")
                phone = donor.phone_number
            
            response = sms_service.send(message, [phone], sender_id=settings.AT_SENDER_ID)
            
            # Parse response
            if response and 'SMSMessageData' in response:
                recipients = response['SMSMessageData'].get('Recipients', [])
                if recipients:
                    recipient_data = recipients[0]
                    status = recipient_data.get('status', 'failed')
                    message_id = recipient_data.get('messageId', '')
                    cost = recipient_data.get('cost', 'UGX 0').replace('UGX ', '')
                    
                    # Enhanced status tracking
                    if status == 'Success':
                        notification.delivery_status = 'sent'
                        notification.at_message_id = message_id
                    elif status == 'Submitted':
                        notification.delivery_status = 'sent'
                        notification.at_message_id = message_id
                    else:
                        notification.delivery_status = 'failed'
                    
                    notification.at_message_id = message_id
                    try:
                        notification.cost = float(cost)
                    except (ValueError, TypeError):
                        notification.cost = 0.0
                    notification.save()
                    
                    if status in ['Success', 'Submitted']:
                        result['sent_count'] += 1
                        print(f"SUCCESS SMS sent successfully to {donor.full_name}")
                    else:
                        result['failed_count'] += 1
                        print(f"SMS failed for {donor.full_name}: {status}")
                else:
                    notification.delivery_status = 'failed'
                    notification.save()
                    result['failed_count'] += 1
                    print(f"SMS failed for {donor.full_name}: No recipients data")
            else:
                notification.delivery_status = 'failed'
                notification.save()
                result['failed_count'] += 1
                print(f"SMS failed for {donor.full_name}: Invalid API response")
                    
    except Exception as e:
        notification.delivery_status = 'failed'
        notification.save()
        result['failed_count'] += 1
        print(f"SMS failed for donor {donor.full_name}: {str(e)}")
        
        print(f"SMS Summary: {result['sent_count']} sent, {result['failed_count']} failed")
        return result
