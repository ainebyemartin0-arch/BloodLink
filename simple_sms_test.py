#!/usr/bin/env python
"""
Simple SMS Test - No Unicode Characters
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

def test_sms():
    print("BloodLink SMS Test")
    print("=" * 30)
    
    try:
        from notifications.utils import test_africastalking_connection
        
        result = test_africastalking_connection()
        
        print(f"Success: {result.get('success', False)}")
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('success'):
            print("SMS Connection: WORKING")
        else:
            print("SMS Connection: FAILED")
            print(f"Error: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"Test Error: {str(e)}")

if __name__ == "__main__":
    test_sms()
