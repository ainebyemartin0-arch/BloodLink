"""
Mock SMS service for testing when Africa's Talking API is not accessible
"""

import time
import random
from django.conf import settings
from django.utils import timezone
from .models import SMSNotification

class MockSMSService:
    """Mock SMS service that simulates SMS sending without actual API calls"""
    
    def __init__(self):
        self.username = getattr(settings, 'AT_USERNAME', 'sandbox')
        self.api_key = getattr(settings, 'AT_API_KEY', 'mock_key')
        self.sender_id = getattr(settings, 'AT_SENDER_ID', 'BloodLink')
    
    def send(self, message, recipients, sender_id=None):
        """Mock SMS sending"""
        if not recipients:
            return {'SMSMessageData': {'Recipients': []}}
        
        sender = sender_id or self.sender_id
        results = []
        
        for recipient in recipients:
            # Simulate different response statuses
            statuses = ['Success', 'Submitted', 'Failed']
            weights = [0.7, 0.2, 0.1]  # 70% success, 20% submitted, 10% failed
            status = random.choices(statuses, weights=weights)[0]
            
            # Generate mock message ID
            message_id = f"MSG_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Generate mock cost
            cost = round(random.uniform(50, 150), 2)
            
            result = {
                'statusCode': status,
                'status': status,
                'messageId': message_id,
                'cost': f"UGX {cost}",
                'number': recipient
            }
            
            results.append(result)
            
            print(f"MOCK SMS: {status} - {recipient} - {message_id}")
        
        return {
            'SMSMessageData': {
                'Message': 'Mock SMS sent successfully',
                'Recipients': results
            }
        }
    
    def check_delivery_status(self, message_id):
        """Mock delivery status check"""
        statuses = ['delivered', 'sent', 'failed']
        status = random.choice(statuses)
        
        return {
            'data': [{
                'status': status,
                'messageId': message_id,
                'timestamp': timezone.now().isoformat()
            }]
        }

def send_emergency_sms_mock(emergency_request):
    """
    Mock version of send_emergency_sms function for testing
    """
    from donors.models import Donor
    
    result = {'sent_count': 0, 'failed_count': 0, 'total_matched': 0}
    
    try:
        # Initialize mock SMS service
        sms_service = MockSMSService()
        
        # Define priority locations
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
        
        print(f"MOCK SMS: Sending to {len(ordered_donors)} donors with blood type {emergency_request.blood_type_needed}")
        print(f"Priority donors: {result['priority_count']}, Other donors: {result['other_count']}")
        
        for donor in ordered_donors:
            # Create notification record first
            notification = SMSNotification.objects.create(
                emergency_request=emergency_request,
                donor=donor,
                message_content=message,
                delivery_status='pending'
            )
            
            # Format phone number
            from .utils import format_phone_uganda
            try:
                phone = format_phone_uganda(donor.phone_number)
                print(f"MOCK SMS: Sending to {donor.full_name} at {phone}")
            except Exception as e:
                print(f"Error formatting phone number: {e}")
                phone = donor.phone_number
            
            # Send mock SMS
            response = sms_service.send(message, [phone], sender_id=settings.AT_SENDER_ID)
            
            # Parse response
            if response and 'SMSMessageData' in response:
                recipients = response['SMSMessageData'].get('Recipients', [])
                if recipients:
                    recipient_data = recipients[0]
                    status = recipient_data.get('status', 'failed')
                    message_id = recipient_data.get('messageId', '')
                    cost_str = recipient_data.get('cost', 'UGX 0')
                    cost = float(cost_str.replace('UGX ', '')) if cost_str != 'UGX 0' else 0.0
                    
                    # Update notification based on status
                    if status in ['Success', 'Submitted']:
                        notification.delivery_status = 'sent'
                        notification.at_message_id = message_id
                        result['sent_count'] += 1
                        print(f"MOCK SMS SUCCESS: Sent to {donor.full_name}")
                    else:
                        notification.delivery_status = 'failed'
                        result['failed_count'] += 1
                        print(f"MOCK SMS FAILED: {status} for {donor.full_name}")
                    
                    notification.cost = cost
                    notification.save()
                else:
                    notification.delivery_status = 'failed'
                    notification.save()
                    result['failed_count'] += 1
                    print(f"MOCK SMS FAILED: No recipients data for {donor.full_name}")
            else:
                notification.delivery_status = 'failed'
                notification.save()
                result['failed_count'] += 1
                print(f"MOCK SMS FAILED: Invalid response for {donor.full_name}")
        
        print(f"MOCK SMS Summary: {result['sent_count']} sent, {result['failed_count']} failed")
        return result
        
    except Exception as e:
        print(f"Error in mock SMS sending: {str(e)}")
        print(f"MOCK SMS Summary: {result['sent_count']} sent, {result['failed_count']} failed")
        return result

def test_mock_sms_connection():
    """Test mock SMS connection"""
    return {
        'success': True,
        'status': 'Mock Mode',
        'message': 'Mock SMS service is active - perfect for testing',
        'username': 'mock_service',
        'note': 'This simulates SMS sending without real API calls',
        'advantages': [
            'No network dependency',
            'No API key required',
            'Instant responses',
            'Predictable behavior',
            'Cost-free testing'
        ]
    }
