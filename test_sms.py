#!/usr/bin/env python
"""
SMS Functionality Test Script
Run this to test if SMS is working properly
"""

import os
import sys
import django

# Add the project path to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')

# Configure environment variables for testing
os.environ['AT_USERNAME'] = 'sandbox'
os.environ['AT_API_KEY'] = 'sandbox'
os.environ['AT_SENDER_ID'] = 'BloodLink'

# Initialize Django
django.setup()

def test_sms_connection():
    """Test SMS connection and functionality"""
    print("Testing BloodLink SMS Functionality...")
    print("=" * 50)
    
    try:
        # Import after Django setup
        from notifications.utils import test_africastalking_connection
        
        # Test connection
        result = test_africastalking_connection()
        
        print(f"Connection Test Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Username: {result.get('username', 'Unknown')}")
        
        if result.get('success'):
            print(f"   Message: {result.get('message', 'No message')}")
            if 'test_response' in result:
                response = result['test_response']
                print(f"   Test SMS Response: {response}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        return False

def test_emergency_sms():
    """Test emergency SMS sending"""
    print("\n🚨 Testing Emergency SMS Sending...")
    print("=" * 50)
    
    try:
        from notifications.utils import send_emergency_sms
        from staff_portal.models import EmergencyRequest
        from django.utils import timezone
        
        # Create a test emergency request
        test_request = EmergencyRequest(
            requester_name="Test User",
            requester_phone="+256700000000",
            patient_name="Test Patient",
            blood_type_needed="O+",
            units_needed=1,
            urgency_level="normal",
            hospital_ward="Test Ward",
            status="open",
            created_by=None  # Can be None for testing
        )
        test_request.save()
        
        print(f"📝 Created test emergency request: #{test_request.pk}")
        print(f"   Blood Type: {test_request.blood_type_needed}")
        print(f"   Urgency: {test_request.get_urgency_level_display()}")
        
        # Send SMS
        result = send_emergency_sms(test_request)
        
        print(f"📱 SMS Sending Results:")
        print(f"   Total Matched Donors: {result.get('total_matched', 0)}")
        print(f"   Sent Successfully: {result.get('sent_count', 0)}")
        print(f"   Failed: {result.get('failed_count', 0)}")
        
        if result.get('sent_count', 0) > 0:
            print("✅ Emergency SMS test completed successfully!")
        else:
            print("⚠️  No matching donors found for test blood type")
            
        return result.get('sent_count', 0) > 0
        
    except Exception as e:
        print(f"❌ Emergency SMS test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("BloodLink SMS Functionality Test")
    print("This will test the SMS system components")
    print()
    
    # Test 1: Connection
    connection_ok = test_sms_connection()
    
    # Test 2: Emergency SMS (only if connection works)
    if connection_ok:
        emergency_ok = test_emergency_sms()
        
        # Summary
        print("\n📊 Test Summary:")
        print("=" * 50)
        print(f"   Connection Test: {'✅ PASS' if connection_ok else '❌ FAIL'}")
        print(f"   Emergency SMS: {'✅ PASS' if emergency_ok else '❌ FAIL'}")
        
        if connection_ok and emergency_ok:
            print("\n🎉 SMS Functionality is WORKING!")
            print("   The system can send SMS alerts to donors")
        else:
            print("\n⚠️  SMS Functionality has ISSUES")
            print("   Check the error messages above")
    else:
        print("\n❌ Cannot test emergency SMS - connection failed")

if __name__ == "__main__":
    main()
