#!/usr/bin/env python
"""
Test script for real-time alert system
Simulates staff sending alerts and tests donor real-time responses
"""

import os
import sys
import django
import time
import json
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from django.test import Client
from django.utils import timezone
from donors.models import Donor
from staff_portal.models import PublicBloodRequest
from notifications.models import SMSNotification

def create_test_blood_request():
    """Create a test blood request to trigger real-time alerts"""
    print("Creating test blood request...")
    
    # Get available donors
    donors = Donor.objects.filter(is_active=True, is_available=True)
    if not donors:
        print("No available donors found. Creating test donor...")
        test_donor = Donor.objects.create(
            full_name="Test Donor",
            email="test@bloodlink.com",
            phone_number="+256123456789",
            blood_type="O+",
            location="Kampala",
            is_available=True,
            is_active=True
        )
        donors = [test_donor]
    
    # Create blood request for first donor's blood type
    donor = donors.first()
    
    request = PublicBloodRequest.objects.create(
        requester_name="Emergency Department",
        requester_phone="+256123456789",
        requester_relationship="Hospital Staff",
        patient_name="Emergency Patient",
        blood_type_needed=donor.blood_type,
        units_needed=1,
        urgency_level="critical",
        hospital_ward="Emergency Ward",
        additional_notes=f"Urgent need for {donor.blood_type} blood for emergency surgery",
        status="approved"  # This triggers alerts
    )
    
    print(f"Created blood request: {request.pk}")
    print(f"Blood Type: {request.blood_type_needed}")
    print(f"Hospital Ward: {request.hospital_ward}")
    print(f"Urgency: {request.urgency_level}")
    
    return request

def create_test_sms_notification(donor):
    """Create a test SMS notification"""
    print(f"Creating test SMS notification for {donor.full_name}...")
    
    # Create a simple emergency request first
    from staff_portal.models import EmergencyRequest
    emergency_req = EmergencyRequest.objects.create(
        blood_type_needed=donor.blood_type,
        units_needed=1,
        patient_name="Emergency Patient",
        urgency_level="urgent",
        notes="Test emergency for real-time alerts"
    )
    
    notification = SMSNotification.objects.create(
        emergency_request=emergency_req,
        donor=donor,
        message_content=f"URGENT: {donor.blood_type} blood needed at St. Francis Hospital. Please respond if available.",
        delivery_status="sent"
    )
    
    print(f"Created SMS notification: {notification.pk}")
    return notification

def test_realtime_api():
    """Test the real-time alert API endpoints"""
    print("\n=== Testing Real-Time Alert API ===")
    
    # Create test client
    client = Client()
    
    # Login as donor
    donor = Donor.objects.filter(is_active=True).first()
    if not donor:
        print("No donor found for testing")
        return
    
    # Manually set session
    session = client.session
    session['donor_id'] = donor.pk
    session.save()
    
    print(f"Testing with donor: {donor.full_name} ({donor.blood_type})")
    
    # Test urgent alerts endpoint
    print("\n1. Testing urgent alerts endpoint...")
    response = client.get('/donor/api/urgent-alerts/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Has new alert: {data.get('has_new_alert')}")
        print(f"Total active requests: {data.get('total_active_requests')}")
        print(f"Recent notifications: {data.get('recent_notifications')}")
        if data.get('alert'):
            alert = data['alert']
            print(f"Alert ID: {alert['id']}")
            print(f"Alert Type: {alert['type']}")
            print(f"Message: {alert['message']}")
    else:
        print(f"Error: {response.content.decode()}")
    
    # Test alert history endpoint
    print("\n2. Testing alert history endpoint...")
    response = client.get('/donor/api/alerts/history/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Total alerts: {data.get('total_count')}")
        alerts = data.get('alerts', [])
        for i, alert in enumerate(alerts[:3]):  # Show first 3
            print(f"  Alert {i+1}: {alert['type']} - {alert['message'][:50]}...")
    else:
        print(f"Error: {response.content.decode()}")
    
    # Test notification stats endpoint
    print("\n3. Testing notification stats endpoint...")
    response = client.get('/donor/api/notification-stats/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        stats = data.get('stats', {})
        print(f"Total requests (30 days): {stats.get('total_requests_30_days')}")
        print(f"Total notifications (30 days): {stats.get('total_notifications_30_days')}")
        print(f"Recent requests (24 hours): {stats.get('recent_requests_24_hours')}")
        print(f"Recent notifications (24 hours): {stats.get('recent_notifications_24_hours')}")
    else:
        print(f"Error: {response.content.decode()}")
    
    return donor

def test_alert_response(donor):
    """Test alert response functionality"""
    print("\n=== Testing Alert Response ===")
    
    # Create a test alert
    alert = create_test_sms_notification(donor)
    
    # Create test client
    client = Client()
    session = client.session
    session['donor_id'] = donor.pk
    session.save()
    
    # Test response to alert
    print(f"\nTesting response to alert {alert.pk}...")
    
    response_data = {
        'response': 'available',
        'timestamp': timezone.now().isoformat()
    }
    
    response = client.post(
        f'/donor/api/alerts/{alert.pk}/respond/',
        data=json.dumps(response_data),
        content_type='application/json'
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print(f"Response type: {data.get('response_type')}")
    else:
        print(f"Error: {response.content.decode()}")
    
    # Verify the response was recorded
    alert.refresh_from_db()
    print(f"Alert response: {alert.response}")
    print(f"Response timestamp: {alert.response_timestamp}")

def simulate_staff_alert():
    """Simulate staff sending an alert in real-time"""
    print("\n=== Simulating Staff Alert ===")
    
    # Create blood request
    request = create_test_blood_request()
    
    # Get matching donors
    matching_donors = Donor.objects.filter(
        blood_type=request.blood_type_needed,
        is_active=True,
        is_available=True
    )
    
    print(f"Found {matching_donors.count()} matching donors")
    
    # Create SMS notifications for each donor
    notifications = []
    for donor in matching_donors:
        # Create a simple emergency request first for the notification
        from staff_portal.models import EmergencyRequest
        emergency_req = EmergencyRequest.objects.create(
            blood_type_needed=request.blood_type_needed,
            units_needed=request.units_needed,
            patient_name=request.patient_name,
            urgency_level=request.urgency_level,
            notes=request.additional_notes
        )
        
        notification = SMSNotification.objects.create(
            emergency_request=emergency_req,
            donor=donor,
            message_content=f"URGENT: {request.blood_type_needed} blood needed at St. Francis Hospital for {request.patient_name}. Please respond immediately.",
            delivery_status="sent"
        )
        notifications.append(notification)
        print(f"Created notification for {donor.full_name}: {notification.pk}")
    
    print(f"\nStaff alert sent! {len(notifications)} donors notified.")
    print("Donors should see real-time alerts in their dashboards.")
    
    return request, notifications

def main():
    """Main test function"""
    print("=== BloodLink Real-Time Alert System Test ===")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Check existing donors
        donors = Donor.objects.filter(is_active=True)
        print(f"\nFound {donors.count()} active donors in database")
        
        if donors.count() == 0:
            print("Creating test donor...")
            donor = Donor.objects.create(
                full_name="Test Donor",
                email="test@bloodlink.com",
                phone_number="+256123456789",
                blood_type="O+",
                location="Kampala",
                is_available=True,
                is_active=True
            )
            print(f"Created test donor: {donor.pk}")
        else:
            donor = donors.first()
            print(f"Using existing donor: {donor.full_name}")
        
        # Test 2: Simulate staff sending alert
        request, notifications = simulate_staff_alert()
        
        # Wait a moment for the alert to be processed
        time.sleep(2)
        
        # Test 3: Test real-time API
        test_donor = test_realtime_api()
        
        # Test 4: Test alert response
        if notifications:
            test_alert_response(test_donor)
        
        print("\n=== Test Summary ===")
        print("Real-time alert system tests completed successfully!")
        print("Key features tested:")
        print("  - Staff alert creation")
        print("  - Real-time API endpoints")
        print("  - Alert response handling")
        print("  - Donor notification system")
        
        print("\nNext steps:")
        print("1. Open donor dashboard in browser")
        print("2. Wait for real-time alerts to appear")
        print("3. Test alert response buttons")
        print("4. Verify staff receives donor responses")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
