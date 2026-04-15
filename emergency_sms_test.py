#!/usr/bin/env python
"""
Emergency SMS Test
"""

import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
os.environ['AT_USERNAME'] = 'sandbox'
os.environ['AT_API_KEY'] = 'sandbox'
os.environ['AT_SENDER_ID'] = 'BloodLink'

# Initialize Django
import django
django.setup()

def test_emergency_sms():
    print("Emergency SMS Test")
    print("=" * 30)
    
    try:
        from notifications.utils import send_emergency_sms
        from staff_portal.models import EmergencyRequest
        from donors.models import Donor
        
        # Create a test emergency request
        test_request = EmergencyRequest(
            blood_type_needed="O+",
            units_needed=1,
            patient_name="Test Patient",
            ward="Test Ward",
            urgency_level="normal",
            status="open"
        )
        test_request.save()
        
        print(f"Created emergency request: #{test_request.pk}")
        
        # Check if we have matching donors
        matching_donors = Donor.objects.filter(
            blood_type="O+",
            is_available=True,
            is_active=True
        )
        
        print(f"Matching donors found: {matching_donors.count()}")
        
        if matching_donors.count() > 0:
            # Send SMS
            result = send_emergency_sms(test_request)
            
            print(f"SMS Sending Results:")
            print(f"Total Matched: {result.get('total_matched', 0)}")
            print(f"Sent Successfully: {result.get('sent_count', 0)}")
            print(f"Failed: {result.get('failed_count', 0)}")
            
            if result.get('sent_count', 0) > 0:
                print("Emergency SMS: WORKING")
            else:
                print("Emergency SMS: FAILED")
        else:
            print("No matching donors found for test blood type")
            
    except Exception as e:
        print(f"Emergency SMS Test Error: {str(e)}")

if __name__ == "__main__":
    test_emergency_sms()
