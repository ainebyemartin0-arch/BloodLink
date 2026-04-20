#!/usr/bin/env python
"""
Manual login test instructions and verification
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import authenticate
from accounts.models import StaffUser
from donors.models import Donor

def verify_users_and_credentials():
    """Verify users exist and credentials work"""
    print("=" * 60)
    print("BLOODLINK LOGIN VERIFICATION")
    print("=" * 60)
    
    print("\n1. CHECKING USERS IN DATABASE:")
    print("-" * 40)
    
    staff_count = StaffUser.objects.count()
    donor_count = Donor.objects.count()
    
    print(f"Staff users: {staff_count}")
    print(f"Donors: {donor_count}")
    
    if staff_count == 0 and donor_count == 0:
        print("\n❌ NO USERS FOUND IN DATABASE")
        print("You need to create users first!")
        return False
    
    print("\n2. TESTING AUTHENTICATION:")
    print("-" * 40)
    
    # Test staff authentication
    staff_success = False
    if StaffUser.objects.exists():
        try:
            staff_user = StaffUser.objects.get(username='admin')
            auth_result = authenticate(username='admin', password='admin123')
            if auth_result:
                print(f"✅ Staff authentication: SUCCESS")
                print(f"   Username: admin")
                print(f"   Email: {staff_user.email}")
                print(f"   Active: {staff_user.is_active}")
                print(f"   Approved: {staff_user.is_approved}")
                staff_success = True
            else:
                print(f"❌ Staff authentication: FAILED")
        except StaffUser.DoesNotExist:
            print(f"❌ Staff user 'admin' not found")
    
    # Test donor authentication
    donor_success = False
    if Donor.objects.exists():
        try:
            donor = Donor.objects.get(email='donor@bloodlink.com')
            if donor.check_password('donor123'):
                print(f"✅ Donor authentication: SUCCESS")
                print(f"   Name: {donor.full_name}")
                print(f"   Email: {donor.email}")
                print(f"   Active: {donor.is_active}")
                print(f"   Available: {donor.is_available}")
                donor_success = True
            else:
                print(f"❌ Donor authentication: FAILED - wrong password")
        except Donor.DoesNotExist:
            print(f"❌ Donor 'donor@bloodlink.com' not found")
    
    print("\n3. LOGIN INSTRUCTIONS:")
    print("-" * 40)
    
    print("START THE DJANGO SERVER:")
    print("   python manage.py runserver")
    print()
    
    if staff_success:
        print("STAFF LOGIN:")
        print("   URL: http://127.0.0.1:8000/staff/secure-access/")
        print("   Username: admin")
        print("   Password: admin123")
        print()
    
    if donor_success:
        print("DONOR LOGIN:")
        print("   URL: http://127.0.0.1:8000/donor/login/")
        print("   Email: donor@bloodlink.com")
        print("   Password: donor123")
        print()
    
    print("4. TROUBLESHOOTING:")
    print("-" * 40)
    print("If login still doesn't work:")
    print("• Make sure Django server is running")
    print("• Use the exact URLs shown above")
    print("• Check browser console for errors (F12)")
    print("• Clear browser cookies and cache")
    print("• Try incognito/private browsing mode")
    print("• Disable browser extensions temporarily")
    print("• Check if CSRF token is being submitted")
    
    return staff_success or donor_success

def main():
    success = verify_users_and_credentials()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ LOGIN SYSTEM IS READY!")
        print("Users exist and authentication is working.")
        print("Start the server and use the credentials above.")
    else:
        print("❌ LOGIN SYSTEM NOT READY!")
        print("No users found or authentication failed.")
    print("=" * 60)

if __name__ == '__main__':
    main()
