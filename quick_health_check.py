#!/usr/bin/env python
"""
Quick system health check for BloodLink
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from accounts.models import StaffUser
from donors.models import Donor
from staff_portal.models import EmergencyRequest
from notifications.models import SMSNotification

def quick_health_check():
    """Quick health check without unicode issues"""
    print("BLOODLINK SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    # Initialize client
    client = Client()
    client.defaults['HTTP_HOST'] = '127.0.0.1:8000'
    
    # Database check
    print("1. DATABASE")
    staff_count = StaffUser.objects.count()
    donor_count = Donor.objects.count()
    print(f"   Staff Users: {staff_count}")
    print(f"   Donors: {donor_count}")
    
    # URL routing check
    print("2. URL ROUTING")
    try:
        response = client.get('/staff/secure-access/')
        print(f"   Staff Login: {response.status_code}")
        
        response = client.get('/donor/login/')
        print(f"   Donor Login: {response.status_code}")
    except Exception as e:
        print(f"   URL Error: {e}")
    
    # Static files check
    print("3. STATIC FILES")
    try:
        response = client.get('/static/css/bloodlink.css')
        print(f"   CSS: {response.status_code}")
        
        response = client.get('/static/js/bloodlink.js')
        print(f"   JavaScript: {response.status_code}")
    except Exception as e:
        print(f"   Static Error: {e}")
    
    # SMS system check
    print("4. SMS SYSTEM")
    try:
        from notifications.utils import test_africastalking_connection
        result = test_africastalking_connection()
        status = result.get('success', False)
        print(f"   SMS API: {'OK' if status else 'ERROR'}")
    except Exception as e:
        print(f"   SMS Error: {e}")
    
    # Summary
    print("5. SUMMARY")
    database_ok = staff_count > 0 and donor_count > 0
    print(f"   Database: {'OK' if database_ok else 'ERROR'}")
    print(f"   System Ready: {'YES' if database_ok else 'NO'}")
    
    print("\nNext Steps:")
    print("   1. python manage.py runserver")
    print("   2. Test in browser")
    print("   3. Use login credentials")

if __name__ == '__main__':
    quick_health_check()
