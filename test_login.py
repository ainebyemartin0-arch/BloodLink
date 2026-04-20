#!/usr/bin/env python
"""
Test login functionality for both staff and donor portals
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import authenticate, login
from accounts.models import StaffUser
from donors.models import Donor

def test_staff_login():
    """Test staff login functionality"""
    print("=== Testing Staff Login ===")
    
    client = Client()
    
    # Test staff login with created credentials
    response = client.post('/staff/secure-access/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    print(f"Staff login response status: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Staff login successful - redirecting to dashboard")
        print(f"Redirect location: {response.get('Location', 'No redirect')}")
    else:
        print("❌ Staff login failed")
        if response.context and 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
    
    # Test accessing dashboard after login
    if response.status_code == 302:
        response = client.get('/staff/dashboard/')
        print(f"Dashboard access status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Dashboard accessible after login")
        else:
            print("❌ Dashboard not accessible after login")

def test_donor_login():
    """Test donor login functionality"""
    print("\n=== Testing Donor Login ===")
    
    client = Client()
    
    # Test donor login with created credentials
    response = client.post('/donor/login/', {
        'email': 'donor@bloodlink.com',
        'password': 'donor123'
    })
    
    print(f"Donor login response status: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Donor login successful - redirecting to dashboard")
        print(f"Redirect location: {response.get('Location', 'No redirect')}")
    else:
        print("❌ Donor login failed")
        if response.context and 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
    
    # Test accessing dashboard after login
    if response.status_code == 302:
        response = client.get('/donor/dashboard/')
        print(f"Dashboard access status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Dashboard accessible after login")
        else:
            print("❌ Dashboard not accessible after login")

def check_users():
    """Check if users exist in database"""
    print("=== Checking Users ===")
    
    staff_count = StaffUser.objects.count()
    donor_count = Donor.objects.count()
    
    print(f"Staff users in database: {staff_count}")
    print(f"Donors in database: {donor_count}")
    
    if staff_count > 0:
        print("Staff users:")
        for staff in StaffUser.objects.all():
            print(f"  - {staff.username} ({staff.email})")
    
    if donor_count > 0:
        print("Donors:")
        for donor in Donor.objects.all():
            print(f"  - {donor.full_name} ({donor.email})")

def main():
    print("BloodLink Login Test")
    print("=" * 40)
    
    check_users()
    test_staff_login()
    test_donor_login()
    
    print("\n" + "=" * 40)
    print("Login test completed!")
    print("\nIf login still doesn't work:")
    print("1. Check if the Django server is running")
    print("2. Verify the URLs are correct")
    print("3. Check browser console for JavaScript errors")
    print("4. Clear browser cookies and cache")
    print("5. Check if CSRF token is being included")

if __name__ == '__main__':
    main()
