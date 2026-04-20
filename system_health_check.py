#!/usr/bin/env python
"""
Comprehensive system health check and fix for BloodLink
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from django.conf import settings
from django.core.management import call_command
from accounts.models import StaffUser
from donors.models import Donor
from staff_portal.models import EmergencyRequest, PublicBloodRequest
from notifications.models import SMSNotification

class SystemHealthChecker:
    def __init__(self):
        self.client = Client()
        self.client.defaults['HTTP_HOST'] = '127.0.0.1:8000'
        self.issues = []
        self.fixes = []
    
    def log_issue(self, component, issue, fix=None):
        """Log an issue and its fix"""
        self.issues.append(f"{component}: {issue}")
        if fix:
            self.fixes.append(f"{component}: {fix}")
    
    def check_database_connectivity(self):
        """Check database connectivity"""
        print("1. DATABASE CONNECTIVITY")
        print("-" * 40)
        
        try:
            # Test basic database operations
            staff_count = StaffUser.objects.count()
            donor_count = Donor.objects.count()
            print(f"✅ Database connected successfully")
            print(f"   Staff users: {staff_count}")
            print(f"   Donors: {donor_count}")
            return True
        except Exception as e:
            self.log_issue("Database", f"Connection failed: {e}", "Check database configuration")
            print(f"❌ Database connection failed: {e}")
            return False
    
    def check_user_authentication(self):
        """Check user authentication system"""
        print("\n2. USER AUTHENTICATION")
        print("-" * 40)
        
        try:
            # Check if users exist
            staff_users = StaffUser.objects.filter(is_active=True)
            donors = Donor.objects.filter(is_active=True)
            
            if staff_users.count() == 0:
                self.log_issue("Staff Users", "No active staff users found")
                print("❌ No active staff users found")
            else:
                print(f"✅ Staff users: {staff_users.count()}")
            
            if donors.count() == 0:
                self.log_issue("Donors", "No active donors found")
                print("❌ No active donors found")
            else:
                print(f"✅ Donors: {donors.count()}")
            
            # Test authentication
            if staff_users.exists():
                staff_user = staff_users.first()
                from django.contrib.auth import authenticate
                auth_user = authenticate(username=staff_user.username, password='admin123')
                if auth_user:
                    print("✅ Staff authentication working")
                else:
                    self.log_issue("Staff Auth", "Authentication failed", "Check user passwords")
            
            return staff_users.count() > 0 and donors.count() > 0
            
        except Exception as e:
            self.log_issue("Authentication", f"System error: {e}")
            print(f"❌ Authentication system error: {e}")
            return False
    
    def check_url_routing(self):
        """Check URL routing"""
        print("\n3. URL ROUTING")
        print("-" * 40)
        
        critical_urls = [
            ('Home', '/'),
            ('Staff Login', '/staff/secure-access/'),
            ('Donor Login', '/donor/login/'),
            ('Staff Dashboard', '/staff/dashboard/'),
            ('Donor Dashboard', '/donor/dashboard/'),
            ('Notifications', '/notifications/'),
        ]
        
        working_urls = 0
        for name, url in critical_urls:
            try:
                response = self.client.get(url)
                if response.status_code in [200, 302]:
                    print(f"✅ {name}: {response.status_code}")
                    working_urls += 1
                else:
                    print(f"❌ {name}: {response.status_code}")
                    self.log_issue("URL Routing", f"{name} returns {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
                self.log_issue("URL Routing", f"{name} error: {e}")
        
        return working_urls == len(critical_urls)
    
    def check_static_files(self):
        """Check static file serving"""
        print("\n4. STATIC FILES")
        print("-" * 40)
        
        static_files = [
            ('CSS', '/static/css/bloodlink.css'),
            ('JavaScript', '/static/js/bloodlink.js'),
            ('Manifest', '/static/manifest.json'),
        ]
        
        working_files = 0
        for name, path in static_files:
            try:
                response = self.client.get(path)
                if response.status_code == 200:
                    print(f"✅ {name}: 200")
                    working_files += 1
                else:
                    print(f"❌ {name}: {response.status_code}")
                    self.log_issue("Static Files", f"{name} returns {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
                self.log_issue("Static Files", f"{name} error: {e}")
        
        return working_files == len(static_files)
    
    def check_api_endpoints(self):
        """Check API endpoints"""
        print("\n5. API ENDPOINTS")
        print("-" * 40)
        
        api_endpoints = [
            ('Staff Dashboard API', '/staff/api/dashboard-stats/'),
            ('Donor Alerts API', '/donor/api/alerts/'),
            ('Notifications API', '/notifications/'),
        ]
        
        working_apis = 0
        for name, endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 302, 400]:  # 400 is OK for unauthenticated
                    print(f"✅ {name}: {response.status_code}")
                    working_apis += 1
                else:
                    print(f"❌ {name}: {response.status_code}")
                    self.log_issue("API Endpoints", f"{name} returns {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
                self.log_issue("API Endpoints", f"{name} error: {e}")
        
        return working_apis >= len(api_endpoints) * 0.8  # 80% success rate
    
    def check_sms_system(self):
        """Check SMS system"""
        print("\n6. SMS SYSTEM")
        print("-" * 40)
        
        try:
            from notifications.utils import test_africastalking_connection
            result = test_africastalking_connection()
            
            if result.get('success'):
                print(f"✅ SMS API: {result.get('status', 'Unknown')}")
                return True
            else:
                print(f"❌ SMS API: Failed")
                self.log_issue("SMS System", "API connection failed")
                return False
        except Exception as e:
            print(f"❌ SMS System: Error - {e}")
            self.log_issue("SMS System", f"Error: {e}")
            return False
    
    def check_template_system(self):
        """Check template system"""
        print("\n7. TEMPLATE SYSTEM")
        print("-" * 40)
        
        try:
            from django.template.loader import get_template
            
            critical_templates = [
                'base.html',
                'staff_portal/login.html',
                'donor_portal/login_enhanced.html',
            ]
            
            working_templates = 0
            for template_name in critical_templates:
                try:
                    template = get_template(template_name)
                    print(f"✅ {template_name}: Loaded")
                    working_templates += 1
                except Exception as e:
                    print(f"❌ {template_name}: Error - {e}")
                    self.log_issue("Templates", f"{template_name}: {e}")
            
            return working_templates == len(critical_templates)
        except Exception as e:
            print(f"❌ Template system: Error - {e}")
            self.log_issue("Templates", f"System error: {e}")
            return False
    
    def check_middleware_security(self):
        """Check middleware and security"""
        print("\n8. MIDDLEWARE & SECURITY")
        print("-" * 40)
        
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        
        configured_middleware = settings.MIDDLEWARE
        missing_middleware = []
        
        for middleware in required_middleware:
            if middleware not in configured_middleware:
                missing_middleware.append(middleware)
        
        if not missing_middleware:
            print("✅ All required middleware configured")
            return True
        else:
            print(f"❌ Missing middleware: {missing_middleware}")
            self.log_issue("Middleware", f"Missing: {missing_middleware}")
            return False
    
    def run_health_check(self):
        """Run complete health check"""
        print("=" * 80)
        print("BLOODLINK SYSTEM HEALTH CHECK")
        print("=" * 80)
        
        checks = [
            ("Database", self.check_database_connectivity),
            ("Authentication", self.check_user_authentication),
            ("URL Routing", self.check_url_routing),
            ("Static Files", self.check_static_files),
            ("API Endpoints", self.check_api_endpoints),
            ("SMS System", self.check_sms_system),
            ("Templates", self.check_template_system),
            ("Middleware", self.check_middleware_security),
        ]
        
        passed_checks = 0
        total_checks = len(checks)
        
        for name, check_func in checks:
            try:
                if check_func():
                    passed_checks += 1
            except Exception as e:
                print(f"❌ {name} check failed: {e}")
                self.log_issue(name, f"Check failed: {e}")
        
        # Generate report
        print("\n" + "=" * 80)
        print("HEALTH CHECK SUMMARY")
        print("=" * 80)
        
        health_score = (passed_checks / total_checks) * 100
        status = "HEALTHY" if health_score >= 80 else "NEEDS ATTENTION" if health_score >= 60 else "CRITICAL"
        
        print(f"Overall Health: {health_score:.1f}% - {status}")
        print(f"Checks Passed: {passed_checks}/{total_checks}")
        
        if self.issues:
            print(f"\nIssues Found ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        if self.fixes:
            print(f"\nRecommended Fixes ({len(self.fixes)}):")
            for i, fix in enumerate(self.fixes, 1):
                print(f"  {i}. {fix}")
        
        print("\n" + "=" * 80)
        
        return health_score >= 80

def main():
    """Run system health check and apply fixes"""
    checker = SystemHealthChecker()
    
    # Run health check
    is_healthy = checker.run_health_check()
    
    # Apply automatic fixes if needed
    if not is_healthy:
        print("\nApplying automatic fixes...")
        
        # Fix 1: Ensure static files are collected
        try:
            call_command('collectstatic', ['--noinput'], verbosity=0)
            print("✅ Static files collected")
        except Exception as e:
            print(f"❌ Failed to collect static files: {e}")
        
        # Fix 2: Create missing users if needed
        if StaffUser.objects.count() == 0:
            try:
                StaffUser.objects.create_user(
                    username='admin',
                    email='admin@bloodlink.com',
                    password='admin123',
                    first_name='System',
                    last_name='Administrator',
                    designation='admin',
                    is_staff=True,
                    is_active=True,
                    is_approved=True
                )
                print("✅ Admin user created")
            except Exception as e:
                print(f"❌ Failed to create admin user: {e}")
        
        if Donor.objects.count() == 0:
            try:
                from datetime import date
                Donor.objects.create(
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
                donor = Donor.objects.get(email='donor@bloodlink.com')
                donor.set_password('donor123')
                donor.save()
                print("✅ Test donor created")
            except Exception as e:
                print(f"❌ Failed to create test donor: {e}")
        
        print("\nRe-running health check after fixes...")
        checker = SystemHealthChecker()
        final_health = checker.run_health_check()
        
        if final_health >= 80:
            print("\n🎉 System is now HEALTHY and ready for use!")
        else:
            print("\n⚠️ System still needs attention. Please review issues above.")
    else:
        print("\n🎉 System is HEALTHY and ready for use!")
    
    print("\nNext Steps:")
    print("1. Start server: python manage.py runserver")
    print("2. Access in browser: http://127.0.0.1:8000")
    print("3. Login with credentials from previous tests")
    print("4. Test all functionality")

if __name__ == '__main__':
    main()
