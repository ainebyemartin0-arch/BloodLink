#!/usr/bin/env python
"""
Targeted Frontend Debug Script
Tests specific issues found in comprehensive debug
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.template.loader import get_template
from django.template import TemplateSyntaxError, TemplateDoesNotExist

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from accounts.models import StaffUser
from donors.models import Donor

def test_specific_pages():
    """Test specific pages with detailed error reporting"""
    print("🔍 Targeted Frontend Debug")
    print("=" * 50)
    
    client = Client()
    
    # Test 1: Staff Dashboard
    print("\n1. Testing Staff Dashboard...")
    staff_user = StaffUser.objects.filter(is_staff=True).first()
    if staff_user:
        client.force_login(staff_user)
        response = client.get('/staff/dashboard/')
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.content.decode()[:300]}")
        else:
            print("   ✅ Working")
    
    # Test 2: Blood Stock
    print("\n2. Testing Blood Stock...")
    response = client.get('/staff/blood-stock/')
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.content.decode()[:300]}")
    else:
        print("   ✅ Working")
    
    # Test 3: Donor Dashboard
    print("\n3. Testing Donor Dashboard...")
    donor = Donor.objects.first()
    if donor:
        # Create donor session
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session['donor_id'] = donor.id
        session.save()
        client.cookies['sessionid'] = session.session_key
        
        response = client.get('/donor/dashboard/')
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.content.decode()[:300]}")
        else:
            print("   ✅ Working")
    
    # Test 4: Donor Donations
    print("\n4. Testing Donor Donations...")
    response = client.get('/donor/donations/')
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.content.decode()[:300]}")
    else:
        print("   ✅ Working")
    
    # Test 5: Home Page
    print("\n5. Testing Home Page...")
    client = Client()  # Clear session
    response = client.get('/')
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.content.decode()[:300]}")
    else:
        print("   ✅ Working")

def check_templates():
    """Check template issues"""
    print("\n🔍 Template Issues...")
    print("=" * 30)
    
    templates_to_check = [
        'donor_portal/base_donor_enhanced.html',
        'base_donor_modern.html',
        'base_staff_modern.html',
    ]
    
    for template_path in templates_to_check:
        try:
            template = get_template(template_path)
            print(f"✅ {template_path} - OK")
        except TemplateDoesNotExist:
            print(f"❌ {template_path} - NOT FOUND")
        except Exception as e:
            print(f"❌ {template_path} - ERROR: {e}")

def check_urls():
    """Check URL patterns"""
    print("\n🔍 URL Pattern Issues...")
    print("=" * 30)
    
    from django.urls import get_resolver
    
    try:
        resolver = get_resolver()
        print("✅ URL resolver working")
        
        # Check specific URL patterns
        urls_to_check = [
            'staff:dashboard',
            'staff:blood_stock',
            'donor:dashboard',
            'donor:donations',
        ]
        
        for url_name in urls_to_check:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name} -> {url}")
            except Exception as e:
                print(f"❌ {url_name} - ERROR: {e}")
                
    except Exception as e:
        print(f"❌ URL resolver error: {e}")

def main():
    """Main function"""
    test_specific_pages()
    check_templates()
    check_urls()

if __name__ == '__main__':
    main()
