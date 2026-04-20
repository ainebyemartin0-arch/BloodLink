#!/usr/bin/env python
"""
Test login with existing users in the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import authenticate
from accounts.models import StaffUser
from donors.models import Donor

def test_existing_staff_login():
    """Test login with existing staff user"""
    print("=== Testing Existing Staff User Login ===")
    
    # Get existing staff user
    try:
        staff_user = StaffUser.objects.get(username='admin')
        print(f"Found staff user: {staff_user.username} ({staff_user.email})")
        print(f"Active: {staff_user.is_active}, Approved: {staff_user.is_approved}")
        
        # Test Django authentication
        auth_user = authenticate(username='admin', password='admin123')
        if auth_user:
            print("✅ Django authentication successful")
            
            # Test with Django test client
            client = Client()
            response = client.post('/staff/secure-access/', {
                'username': 'admin',
                'password': 'admin123'
            }, follow=True)
            
            print(f"Login response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Staff login successful!")
                # Check if we're on the dashboard
                if 'dashboard' in response.request['PATH_INFO']:
                    print("✅ Redirected to dashboard correctly")
                else:
                    print(f"Current page: {response.request['PATH_INFO']}")
            else:
                print("❌ Staff login failed in test client")
                if hasattr(response, 'context') and response.context:
                    if 'form' in response.context:
                        print("Form errors:", response.context['form'].errors)
        else:
            print("❌ Django authentication failed")
            
    except StaffUser.DoesNotExist:
        print("❌ No staff user found with username 'admin'")
    except Exception as e:
        print(f"❌ Error testing staff login: {e}")

def test_existing_donor_login():
    """Test login with existing donor"""
    print("\n=== Testing Existing Donor Login ===")
    
    # Get existing donor
    try:
        donor = Donor.objects.get(email='donor@bloodlink.com')
        print(f"Found donor: {donor.full_name} ({donor.email})")
        print(f"Active: {donor.is_active}, Available: {donor.is_available}")
        
        # Test password check
        if donor.check_password('donor123'):
            print("✅ Password verification successful")
            
            # Test with Django test client
            client = Client()
            response = client.post('/donor/login/', {
                'email': 'donor@bloodlink.com',
                'password': 'donor123'
            }, follow=True)
            
            print(f"Login response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Donor login successful!")
                # Check if we're on the dashboard
                if 'dashboard' in response.request['PATH_INFO']:
                    print("✅ Redirected to dashboard correctly")
                else:
                    print(f"Current page: {response.request['PATH_INFO']}")
            else:
                print("❌ Donor login failed in test client")
                if hasattr(response, 'context') and response.context:
                    if 'form' in response.context:
                        print("Form errors:", response.context['form'].errors)
        else:
            print("❌ Password verification failed")
            
    except Donor.DoesNotExist:
        print("❌ No donor found with email 'donor@bloodlink.com'")
    except Exception as e:
        print(f"❌ Error testing donor login: {e}")

def test_direct_authentication():
    """Test direct authentication methods"""
    print("\n=== Testing Direct Authentication ===")
    
    # Test staff authentication
    print("Testing staff authentication...")
    staff_auth = authenticate(username='admin', password='admin123')
    if staff_auth:
        print(f"✅ Staff auth successful: {staff_auth.username}")
    else:
        print("❌ Staff auth failed")
    
    # Test donor authentication (custom method)
    print("Testing donor authentication...")
    try:
        donor = Donor.objects.get(email='donor@bloodlink.com')
        if donor.check_password('donor123'):
            print(f"✅ Donor auth successful: {donor.full_name}")
        else:
            print("❌ Donor auth failed - wrong password")
    except Donor.DoesNotExist:
        print("❌ Donor not found")

def check_login_urls():
    """Check if login URLs are accessible"""
    print("\n=== Checking Login URLs ===")
    
    client = Client()
    
    # Test staff login page
    response = client.get('/staff/secure-access/')
    print(f"Staff login page status: {response.status_code}")
    
    # Test donor login page
    response = client.get('/donor/login/')
    print(f"Donor login page status: {response.status_code}")

def main():
    print("Testing Login with Existing Database Users")
    print("=" * 50)
    
    check_login_urls()
    test_direct_authentication()
    test_existing_staff_login()
    test_existing_donor_login()
    
    print("\n" + "=" * 50)
    print("Login Testing Complete!")
    print("\nIf login still fails:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Try the credentials manually in browser")
    print("3. Check browser console for errors")
    print("4. Clear browser cookies and cache")
    print("5. Verify CSRF tokens are working")

if __name__ == '__main__':
    main()
