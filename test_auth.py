#!/usr/bin/env python
"""
Test authentication for blood stock page
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

def test_auth():
    """Test authentication flow"""
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    User = get_user_model()
    
    # Check staff user
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        print("❌ No staff user found")
        return
    
    print(f"✅ Found staff user: {staff_user.username}")
    print(f"   Is staff: {staff_user.is_staff}")
    print(f"   Is active: {staff_user.is_active}")
    print(f"   Is authenticated: {staff_user.is_authenticated}")
    
    # Test with Client
    client = Client()
    
    # Test without login
    print("\n🧪 Testing without login...")
    response = client.get('/staff/blood-stock/')
    print(f"   Status: {response.status_code}")
    
    # Test with login
    print("\n🧪 Testing with login...")
    success = client.login(username=staff_user.username, password='admin123')  # Default password
    print(f"   Login success: {success}")
    
    if success:
        response = client.get('/staff/blood-stock/')
        print(f"   Status after login: {response.status_code}")
        if response.status_code == 200:
            print("✅ Authentication working!")
        else:
            print(f"❌ Authentication failed with status {response.status_code}")
            # Check content
            content = response.content.decode('utf-8')
            if 'Bad Request' in content:
                print("   Error: Bad Request")
            elif '403' in content:
                print("   Error: Forbidden")
            elif '404' in content:
                print("   Error: Not Found")
    else:
        print("❌ Login failed")
    
    # Test with force_login
    print("\n🧪 Testing with force_login...")
    client.force_login(staff_user)
    response = client.get('/staff/blood-stock/')
    print(f"   Status with force_login: {response.status_code}")

if __name__ == '__main__':
    test_auth()
