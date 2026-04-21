#!/usr/bin/env python
"""
Test and fix donor requests link
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from donors.models import Donor
from staff_portal.models import PublicBloodRequest

def test_donor_requests():
    """Test donor requests endpoint"""
    print("TESTING DONOR REQUESTS ENDPOINT")
    print("=" * 40)
    
    client = Client()
    client.defaults['HTTP_HOST'] = '127.0.0.1:8000'
    
    # Check donor exists
    donor = Donor.objects.filter(email='donor@bloodlink.com').first()
    if not donor:
        print("Creating test donor...")
        from datetime import date
        donor = Donor.objects.create(
            full_name='Test Donor',
            email='donor@bloodlink.com',
            phone_number='+256700000001',
            blood_type='O+',
            location='Kampala',
            gender='Male',
            date_of_birth=date(1990, 1, 1),
            is_available=True,
            is_active=True
        )
        donor.set_password('donor123')
        donor.save()
        print("Test donor created")
    else:
        print("Donor already exists")
    
    # Create a test blood request
    if PublicBloodRequest.objects.count() == 0:
        print("Creating test blood request...")
        request = PublicBloodRequest.objects.create(
            patient_name='Test Patient',
            blood_type_needed='O+',
            units_needed=2,
            requester_name='Test Requester',
            requester_phone='+256700000002',
            requester_relationship='Family',
            urgency_level='critical',
            status='pending'
        )
        print("Test blood request created")
    
    # Test login
    print("Testing donor login...")
    response = client.post('/donor/login/', {
        'email': 'donor@bloodlink.com',
        'password': 'donor123'
    }, follow=True)
    
    if response.status_code == 200:
        print("Login successful")
        
        # Manually set session to ensure donor is logged in
        donor = Donor.objects.get(email='donor@bloodlink.com')
        session = client.session
        session['donor_id'] = donor.pk
        session.save()
        print("Session set manually")
        
        # Test requests page
        print("Testing requests page...")
        response = client.get('/donor/requests/')
        
        if response.status_code == 200:
            print("SUCCESS: Donor requests page is working!")
            print("Page content length:", len(response.content))
        elif response.status_code == 302:
            print(f"Redirected to: {response.url}")
            # Follow the redirect
            follow_response = client.get(response.url)
            print(f"Follow redirect status: {follow_response.status_code}")
            if follow_response.status_code == 200:
                print("SUCCESS: Page works after redirect!")
            else:
                print("ERROR: Even the redirect failed")
        else:
            print(f"ERROR: Requests page returned {response.status_code}")
            if response.status_code == 404:
                print("Template not found or URL not configured")
            elif response.status_code == 500:
                print("Server error - check view code")
            elif response.status_code == 400:
                print("Bad request - check form data")
            
            print("Error content:", response.content.decode()[:500])
    else:
        print(f"Login failed with status {response.status_code}")
        print("Login response:", response.content.decode()[:300])

if __name__ == '__main__':
    test_donor_requests()
