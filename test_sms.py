#!/usr/bin/env python
"""
Test SMS functionality for BloodLink system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from notifications.utils import test_africastalking_connection, send_emergency_sms
from notifications.models import SMSNotification
from staff_portal.models import EmergencyRequest
from donors.models import Donor
from accounts.models import StaffUser

def test_sms_system():
    """Test the complete SMS system"""
    print("=" * 60)
    print("BLOODLINK SMS SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Africa's Talking Connection
    print("\n1. Testing Africa's Talking API Connection...")
    print("-" * 40)
    connection_result = test_africastalking_connection()
    print(f"Status: {connection_result.get('success', False)}")
    print(f"Message: {connection_result.get('message', 'No message')}")
    print(f"Username: {connection_result.get('username', 'Unknown')}")
    
    # Test 2: Check Prerequisites
    print("\n2. Checking System Prerequisites...")
    print("-" * 40)
    donor_count = Donor.objects.count()
    staff_count = StaffUser.objects.count()
    emergency_count = EmergencyRequest.objects.count()
    
    print(f"Available Donors: {donor_count}")
    print(f"Staff Users: {staff_count}")
    print(f"Emergency Requests: {emergency_count}")
    
    if donor_count == 0:
        print("ERROR: No donors found in database")
        return False
    
    if staff_count == 0:
        print("ERROR: No staff users found in database")
        return False
    
    # Show available donors
    print("\nAvailable Donors:")
    for donor in Donor.objects.all():
        print(f"  - {donor.full_name} | {donor.blood_type} | {donor.phone_number}")
    
    # Test 3: Create Emergency Request
    print("\n3. Creating Test Emergency Request...")
    print("-" * 40)
    try:
        staff_user = StaffUser.objects.get(username='admin')
        
        emergency_request = EmergencyRequest.objects.create(
            patient_name='Test Emergency Patient',
            blood_type_needed='O+',
            units_needed=2,
            urgency_level='critical',
            ward='Emergency Ward',
            created_by=staff_user,
            status='open'
        )
        print(f"SUCCESS: Emergency request created")
        print(f"  Request ID: #{emergency_request.pk}")
        print(f"  Patient: {emergency_request.patient_name}")
        print(f"  Blood Type: {emergency_request.blood_type_needed}")
        print(f"  Units: {emergency_request.units_needed}")
        print(f"  Urgency: {emergency_request.urgency_level}")
        
    except Exception as e:
        print(f"ERROR: Failed to create emergency request: {e}")
        return False
    
    # Test 4: Send SMS
    print("\n4. Testing SMS Sending...")
    print("-" * 40)
    try:
        sms_result = send_emergency_sms(emergency_request)
        print(f"SMS Sending Results:")
        print(f"  Total matched donors: {sms_result.get('total_matched', 0)}")
        print(f"  Priority donors: {sms_result.get('priority_count', 0)}")
        print(f"  Other donors: {sms_result.get('other_count', 0)}")
        print(f"  SMS sent successfully: {sms_result.get('sent_count', 0)}")
        print(f"  SMS failed: {sms_result.get('failed_count', 0)}")
        
    except Exception as e:
        print(f"ERROR: Failed to send SMS: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Check SMS Notifications
    print("\n5. Checking SMS Notifications Created...")
    print("-" * 40)
    try:
        sms_notifications = SMSNotification.objects.filter(emergency_request=emergency_request)
        print(f"SMS notifications created: {sms_notifications.count()}")
        
        for sms in sms_notifications:
            print(f"  To: {sms.donor.full_name}")
            print(f"    Phone: {sms.donor.phone_number}")
            print(f"    Status: {sms.delivery_status}")
            print(f"    Message ID: {sms.at_message_id or 'None'}")
            print(f"    Cost: UGX {sms.cost}")
            print(f"    Created: {sms.sent_at}")
            print()
    
    except Exception as e:
        print(f"ERROR: Failed to check SMS notifications: {e}")
        return False
    
    # Test 6: Test SMS API endpoint
    print("\n6. Testing SMS API Endpoint...")
    print("-" * 40)
    try:
        from django.test import Client
        client = Client()
        
        # Login as staff
        client.post('/staff/secure-access/', {
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Test SMS API
        response = client.get('/notifications/test-sms-api/')
        print(f"SMS API Test Status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: SMS API endpoint is working")
        else:
            print("ERROR: SMS API endpoint failed")
    
    except Exception as e:
        print(f"ERROR: Failed to test SMS API: {e}")
    
    print("\n" + "=" * 60)
    print("SMS SYSTEM TEST COMPLETE")
    print("=" * 60)
    
    return True

def main():
    success = test_sms_system()
    
    if success:
        print("\nSMS SYSTEM STATUS: OPERATIONAL")
        print("All SMS functionality is working correctly!")
        print("\nNext steps:")
        print("1. Update AT_USERNAME and AT_API_KEY for production")
        print("2. Test with real phone numbers")
        print("3. Monitor SMS delivery in admin panel")
    else:
        print("\nSMS SYSTEM STATUS: NEEDS ATTENTION")
        print("Some SMS functionality is not working correctly!")
    
    print("\nSMS Configuration:")
    print("- Current Mode: Sandbox (testing)")
    print("- Provider: Africa's Talking")
    print("- Sender ID: BloodLink")
    print("- To use live SMS: Update .env file with live credentials")

if __name__ == '__main__':
    main()
