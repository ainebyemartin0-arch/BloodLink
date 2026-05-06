#!/usr/bin/env python
"""
Debug remaining frontend pages
"""

import os
import sys
import django
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from accounts.models import StaffUser
from donors.models import Donor

def test_remaining_pages():
    """Test pages that might have issues"""
    print("🔍 Testing Remaining Frontend Pages")
    print("=" * 50)
    
    client = Client()
    
    # Test staff pages
    print("\n📋 STAFF PORTAL - Remaining Pages:")
    staff_user = StaffUser.objects.filter(is_staff=True).first()
    if staff_user:
        client.force_login(staff_user)
        
        staff_pages = [
            ('Donor Requests', '/staff/donor-requests/'),
            ('Emergency Requests', '/staff/emergency-requests/'),
            ('Public Requests', '/staff/public-requests/'),
            ('Reports', '/staff/reports/'),
        ]
        
        for page_name, url in staff_pages:
            try:
                response = client.get(url)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} {page_name}: {response.status_code}")
                if response.status_code != 200:
                    error_content = response.content.decode()[:200]
                    print(f"      Error: {error_content}")
            except Exception as e:
                print(f"   ❌ {page_name}: Exception - {e}")
    
    # Test donor pages
    print("\n📋 DONOR PORTAL - Remaining Pages:")
    donor = Donor.objects.first()
    if donor:
        # Create donor session
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session['donor_id'] = donor.id
        session.save()
        client.cookies['sessionid'] = session.session_key
        
        donor_pages = [
            ('Donor Requests', '/donor/requests/'),
            ('Profile', '/donor/profile/'),
            ('About', '/donor/about/'),
            ('FAQ', '/donor/faq/'),
            ('Contact', '/donor/contact/'),
            ('Register', '/donor/register/'),
            ('Login', '/donor/login/'),
        ]
        
        for page_name, url in donor_pages:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"   ✅ {page_name}: {response.status_code}")
                elif response.status_code == 302:
                    print(f"   ✅ {page_name}: {response.status_code} (Redirect expected)")
                else:
                    print(f"   ❌ {page_name}: {response.status_code}")
                    error_content = response.content.decode()[:200]
                    print(f"      Error: {error_content}")
            except Exception as e:
                print(f"   ❌ {page_name}: Exception - {e}")
    
    # Test public pages
    print("\n📋 PUBLIC PAGES:")
    client = Client()  # Clear session
    
    public_pages = [
        ('Home', '/'),
        ('Staff Login', '/staff/login/'),
    ]
    
    for page_name, url in public_pages:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"   ✅ {page_name}: {response.status_code}")
            elif response.status_code == 302:
                print(f"   ✅ {page_name}: {response.status_code} (Redirect expected)")
            else:
                print(f"   ❌ {page_name}: {response.status_code}")
                error_content = response.content.decode()[:200]
                print(f"      Error: {error_content}")
        except Exception as e:
            print(f"   ❌ {page_name}: Exception - {e}")

def check_static_files():
    """Check static file accessibility"""
    print("\n📁 STATIC FILES:")
    
    client = Client()
    static_files = [
        ('CSS', '/static/css/style.css'),
        ('JS', '/static/js/main.js'),
        ('Logo', '/static/images/logo.png'),
        ('Bootstrap CSS', '/static/css/bootstrap.min.css'),
    ]
    
    for file_type, url in static_files:
        try:
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {file_type}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {file_type}: Exception - {e}")

def main():
    """Main function"""
    test_remaining_pages()
    check_static_files()

if __name__ == '__main__':
    main()
