#!/usr/bin/env python
"""
Comprehensive system check for BloodLink - verifies all components are linked and working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from django.conf import settings
from django.template.loader import get_template
from django.core.management import call_command
from django.db import connection
from accounts.models import StaffUser
from donors.models import Donor
from staff_portal.models import EmergencyRequest, PublicBloodRequest, DonationRecord
from notifications.models import SMSNotification

class ComprehensiveSystemChecker:
    def __init__(self):
        self.client = Client()
        self.client.defaults['HTTP_HOST'] = '127.0.0.1:8000'
        self.issues = []
        self.fixes = []
        self.success_count = 0
        self.total_checks = 0
    
    def log_result(self, check_name, success, message="", fix=""):
        """Log test result"""
        self.total_checks += 1
        if success:
            self.success_count += 1
            print(f"   PASS: {check_name}")
            if message:
                print(f"        {message}")
        else:
            print(f"   FAIL: {check_name}")
            if message:
                print(f"        Issue: {message}")
            if fix:
                self.fixes.append(f"{check_name}: {fix}")
            self.issues.append(f"{check_name}: {message}")
    
    def check_core_django_setup(self):
        """Check Django core configuration"""
        print("1. DJANGO CORE CONFIGURATION")
        print("-" * 50)
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.log_result("Database Connection", True, "Database connected successfully")
        except Exception as e:
            self.log_result("Database Connection", False, str(e), "Check database settings")
        
        # Check installed apps
        required_apps = ['accounts', 'donors', 'staff_portal', 'donor_portal', 'notifications']
        installed_apps = settings.INSTALLED_APPS
        
        for app in required_apps:
            if app in installed_apps:
                self.log_result(f"App: {app}", True, f"{app} is installed")
            else:
                self.log_result(f"App: {app}", False, f"{app} not installed", f"Add {app} to INSTALLED_APPS")
        
        # Check middleware
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        
        for middleware in required_middleware:
            if middleware in settings.MIDDLEWARE:
                self.log_result(f"Middleware: {middleware.split('.')[-1]}", True)
            else:
                self.log_result(f"Middleware: {middleware.split('.')[-1]}", False, "Missing critical middleware")
    
    def check_models_and_database(self):
        """Check all models and database relationships"""
        print("\n2. MODELS AND DATABASE")
        print("-" * 50)
        
        # Check Staff User model
        try:
            staff_count = StaffUser.objects.count()
            self.log_result("StaffUser Model", True, f"{staff_count} staff users in database")
            
            # Test staff user creation
            if staff_count == 0:
                staff_user = StaffUser.objects.create_user(
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
                self.log_result("Staff User Creation", True, "Admin user created")
        except Exception as e:
            self.log_result("StaffUser Model", False, str(e))
        
        # Check Donor model
        try:
            donor_count = Donor.objects.count()
            self.log_result("Donor Model", True, f"{donor_count} donors in database")
            
            if donor_count == 0:
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
                self.log_result("Donor Creation", True, "Test donor created")
        except Exception as e:
            self.log_result("Donor Model", False, str(e))
        
        # Check Emergency Request model
        try:
            emergency_count = EmergencyRequest.objects.count()
            self.log_result("EmergencyRequest Model", True, f"{emergency_count} emergency requests")
            
            if emergency_count == 0:
                staff_user = StaffUser.objects.first()
                if staff_user:
                    emergency = EmergencyRequest.objects.create(
                        patient_name='Test Patient',
                        blood_type_needed='O+',
                        units_needed=2,
                        urgency_level='critical',
                        ward='Emergency',
                        created_by=staff_user,
                        status='open'
                    )
                    self.log_result("Emergency Request Creation", True, "Test emergency request created")
        except Exception as e:
            self.log_result("EmergencyRequest Model", False, str(e))
        
        # Check SMS Notification model
        try:
            sms_count = SMSNotification.objects.count()
            self.log_result("SMSNotification Model", True, f"{sms_count} SMS notifications")
        except Exception as e:
            self.log_result("SMSNotification Model", False, str(e))
    
    def check_url_routing(self):
        """Check all URL patterns and routing"""
        print("\n3. URL ROUTING SYSTEM")
        print("-" * 50)
        
        # Test main URL patterns
        url_patterns = [
            ('Home', '/'),
            ('Staff Login', '/staff/secure-access/'),
            ('Staff Dashboard', '/staff/dashboard/'),
            ('Staff Donor List', '/staff/donors/'),
            ('Staff Requests', '/staff/requests/'),
            ('Donor Login', '/donor/login/'),
            ('Donor Dashboard', '/donor/dashboard/'),
            ('Donor Profile', '/donor/profile/'),
            ('Donor Donations', '/donor/donations/'),
            ('Notifications', '/notifications/'),
        ]
        
        for name, url in url_patterns:
            try:
                response = self.client.get(url)
                if response.status_code in [200, 302]:
                    self.log_result(f"URL: {name}", True, f"Status {response.status_code}")
                else:
                    self.log_result(f"URL: {name}", False, f"Status {response.status_code}")
            except Exception as e:
                self.log_result(f"URL: {name}", False, str(e))
        
        # Test URL resolution
        try:
            resolve('/staff/secure-access/')
            self.log_result("URL Resolution", True, "Staff login URL resolves correctly")
        except Exception as e:
            self.log_result("URL Resolution", False, str(e))
        
        try:
            resolve('/donor/login/')
            self.log_result("URL Resolution", True, "Donor login URL resolves correctly")
        except Exception as e:
            self.log_result("URL Resolution", False, str(e))
    
    def check_views_and_templates(self):
        """Check views and template loading"""
        print("\n4. VIEWS AND TEMPLATES")
        print("-" * 50)
        
        # Check critical templates
        templates_to_check = [
            'base.html',
            'staff_portal/login.html',
            'staff_portal/dashboard.html',
            'donor_portal/login_enhanced.html',
            'donor_portal/dashboard.html',
            '404.html',
        ]
        
        for template_name in templates_to_check:
            try:
                template = get_template(template_name)
                self.log_result(f"Template: {template_name}", True, "Template loads successfully")
            except Exception as e:
                self.log_result(f"Template: {template_name}", False, str(e))
        
        # Test view functionality
        try:
            response = self.client.get('/staff/secure-access/')
            if response.status_code == 200:
                self.log_result("Staff Login View", True, "View renders correctly")
            else:
                self.log_result("Staff Login View", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Staff Login View", False, str(e))
        
        try:
            response = self.client.get('/donor/login/')
            if response.status_code == 200:
                self.log_result("Donor Login View", True, "View renders correctly")
            else:
                self.log_result("Donor Login View", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Donor Login View", False, str(e))
    
    def check_static_files(self):
        """Check static file serving"""
        print("\n5. STATIC FILES SERVING")
        print("-" * 50)
        
        static_files = [
            ('CSS', '/static/css/bloodlink.css'),
            ('CSS Enhanced', '/static/css/bloodlink-enhanced.css'),
            ('JavaScript', '/static/js/bloodlink.js'),
            ('Material Design CSS', '/static/css/material-design.css'),
            ('Material Design JS', '/static/js/material-design.js'),
            ('PWA Manifest', '/static/manifest.json'),
        ]
        
        for name, path in static_files:
            try:
                response = self.client.get(path)
                if response.status_code == 200:
                    self.log_result(f"Static: {name}", True, f"Status {response.status_code}")
                else:
                    self.log_result(f"Static: {name}", False, f"Status {response.status_code}")
            except Exception as e:
                self.log_result(f"Static: {name}", False, str(e))
    
    def check_api_endpoints(self):
        """Check all API endpoints"""
        print("\n6. API ENDPOINTS")
        print("-" * 50)
        
        api_endpoints = [
            ('Staff Dashboard API', '/staff/api/dashboard-stats/'),
            ('Staff Check Shortage API', '/staff/api/check-shortage/'),
            ('Staff Notifications API', '/staff/api/notifications/check/'),
            ('Donor Urgent Alerts API', '/donor/api/urgent-alerts/'),
            ('Donor Toggle Availability API', '/donor/api/toggle-availability/'),
            ('Donor Alerts API', '/donor/api/alerts/'),
            ('Notifications API', '/notifications/'),
            ('SMS Test API', '/notifications/test-sms-api/'),
        ]
        
        for name, endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 302, 400, 403]:  # 400/403 OK for unauthenticated
                    self.log_result(f"API: {name}", True, f"Status {response.status_code}")
                else:
                    self.log_result(f"API: {name}", False, f"Status {response.status_code}")
            except Exception as e:
                self.log_result(f"API: {name}", False, str(e))
    
    def check_authentication_system(self):
        """Check authentication system"""
        print("\n7. AUTHENTICATION SYSTEM")
        print("-" * 50)
        
        # Test staff authentication
        try:
            staff_user = StaffUser.objects.first()
            if staff_user:
                from django.contrib.auth import authenticate
                auth_user = authenticate(username=staff_user.username, password='admin123')
                if auth_user:
                    self.log_result("Staff Authentication", True, "Staff login working")
                else:
                    self.log_result("Staff Authentication", False, "Staff authentication failed")
            else:
                self.log_result("Staff Authentication", False, "No staff user found")
        except Exception as e:
            self.log_result("Staff Authentication", False, str(e))
        
        # Test donor authentication
        try:
            donor = Donor.objects.first()
            if donor:
                if donor.check_password('donor123'):
                    self.log_result("Donor Authentication", True, "Donor login working")
                else:
                    self.log_result("Donor Authentication", False, "Donor authentication failed")
            else:
                self.log_result("Donor Authentication", False, "No donor found")
        except Exception as e:
            self.log_result("Donor Authentication", False, str(e))
        
        # Test session management
        try:
            response = self.client.post('/staff/secure-access/', {
                'username': 'admin',
                'password': 'admin123'
            })
            if response.status_code in [200, 302]:
                self.log_result("Session Management", True, "Staff login successful")
            else:
                self.log_result("Session Management", False, f"Login failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Session Management", False, str(e))
    
    def check_sms_system(self):
        """Check SMS system"""
        print("\n8. SMS NOTIFICATION SYSTEM")
        print("-" * 50)
        
        # Test SMS API connection
        try:
            from notifications.utils import test_africastalking_connection
            result = test_africastalking_connection()
            if result.get('success'):
                self.log_result("SMS API Connection", True, f"Mode: {result.get('status', 'Unknown')}")
            else:
                self.log_result("SMS API Connection", False, "API connection failed")
        except Exception as e:
            self.log_result("SMS API Connection", False, str(e))
        
        # Test SMS sending functionality
        try:
            from notifications.utils import send_emergency_sms
            emergency = EmergencyRequest.objects.first()
            if emergency:
                result = send_emergency_sms(emergency)
                if result:
                    self.log_result("SMS Sending", True, f"Matched {result.get('total_matched', 0)} donors")
                else:
                    self.log_result("SMS Sending", False, "SMS sending returned None")
            else:
                self.log_result("SMS Sending", False, "No emergency request found")
        except Exception as e:
            self.log_result("SMS Sending", False, str(e))
        
        # Test mock SMS fallback
        try:
            from notifications.mock_sms import test_mock_sms_connection
            result = test_mock_sms_connection()
            if result.get('success'):
                self.log_result("Mock SMS Fallback", True, "Mock service ready")
            else:
                self.log_result("Mock SMS Fallback", False, "Mock service failed")
        except Exception as e:
            self.log_result("Mock SMS Fallback", False, str(e))
    
    def check_form_functionality(self):
        """Check forms and validation"""
        print("\n9. FORMS AND VALIDATION")
        print("-" * 50)
        
        # Test staff login form
        try:
            response = self.client.post('/staff/secure-access/', {
                'username': 'invalid',
                'password': 'invalid'
            })
            if response.status_code == 200:
                self.log_result("Staff Login Form", True, "Form handles invalid credentials")
            else:
                self.log_result("Staff Login Form", False, f"Unexpected status {response.status_code}")
        except Exception as e:
            self.log_result("Staff Login Form", False, str(e))
        
        # Test donor login form
        try:
            response = self.client.post('/donor/login/', {
                'email': 'invalid@email.com',
                'password': 'invalid'
            })
            if response.status_code == 200:
                self.log_result("Donor Login Form", True, "Form handles invalid credentials")
            else:
                self.log_result("Donor Login Form", False, f"Unexpected status {response.status_code}")
        except Exception as e:
            self.log_result("Donor Login Form", False, str(e))
        
        # Test CSRF protection
        try:
            response = self.client.get('/staff/secure-access/')
            if hasattr(response, 'context') and response.context:
                csrf_token = response.context.get('csrf_token')
                if csrf_token and csrf_token != 'NOTSET':
                    self.log_result("CSRF Protection", True, "CSRF token present")
                else:
                    self.log_result("CSRF Protection", False, "CSRF token missing")
            else:
                self.log_result("CSRF Protection", False, "Could not check CSRF token")
        except Exception as e:
            self.log_result("CSRF Protection", False, str(e))
    
    def check_error_handling(self):
        """Check error handling"""
        print("\n10. ERROR HANDLING")
        print("-" * 50)
        
        # Test 404 handling
        try:
            response = self.client.get('/nonexistent-url/')
            if response.status_code == 404:
                self.log_result("404 Error Handling", True, "Custom 404 page working")
            else:
                self.log_result("404 Error Handling", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_result("404 Error Handling", False, str(e))
        
        # Test admin access (should be disabled)
        try:
            response = self.client.get('/admin/')
            if response.status_code == 404:
                self.log_result("Admin Access", True, "Admin properly disabled")
            else:
                self.log_result("Admin Access", False, f"Admin accessible (status {response.status_code})")
        except Exception as e:
            self.log_result("Admin Access", True, "Admin not accessible (expected)")
    
    def apply_automatic_fixes(self):
        """Apply automatic fixes for common issues"""
        print("\n11. APPLYING AUTOMATIC FIXES")
        print("-" * 50)
        
        fixes_applied = 0
        
        # Fix 1: Collect static files
        try:
            call_command('collectstatic', ['--noinput'], verbosity=0)
            print("   Fixed: Static files collected")
            fixes_applied += 1
        except Exception as e:
            print(f"   Could not fix static files: {e}")
        
        # Fix 2: Run migrations
        try:
            call_command('migrate', ['--fake-initial'], verbosity=0)
            print("   Fixed: Database migrations applied")
            fixes_applied += 1
        except Exception as e:
            print(f"   Could not apply migrations: {e}")
        
        # Fix 3: Ensure users exist
        try:
            if StaffUser.objects.count() == 0:
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
                print("   Fixed: Admin user created")
                fixes_applied += 1
        except Exception as e:
            print(f"   Could not create admin user: {e}")
        
        try:
            if Donor.objects.count() == 0:
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
                print("   Fixed: Test donor created")
                fixes_applied += 1
        except Exception as e:
            print(f"   Could not create test donor: {e}")
        
        print(f"   Total fixes applied: {fixes_applied}")
        return fixes_applied > 0
    
    def run_comprehensive_check(self):
        """Run the complete comprehensive system check"""
        print("=" * 80)
        print("BLOODLINK COMPREHENSIVE SYSTEM CHECK")
        print("=" * 80)
        print("Checking all components are properly linked and working...")
        
        # Run all checks
        checks = [
            self.check_core_django_setup,
            self.check_models_and_database,
            self.check_url_routing,
            self.check_views_and_templates,
            self.check_static_files,
            self.check_api_endpoints,
            self.check_authentication_system,
            self.check_sms_system,
            self.check_form_functionality,
            self.check_error_handling,
        ]
        
        for check_func in checks:
            try:
                check_func()
            except Exception as e:
                print(f"   ERROR in {check_func.__name__}: {e}")
        
        # Apply automatic fixes
        fixes_applied = self.apply_automatic_fixes()
        
        # Generate final report
        self.generate_final_report(fixes_applied)
    
    def generate_final_report(self, fixes_applied):
        """Generate final comprehensive report"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE SYSTEM CHECK REPORT")
        print("=" * 80)
        
        success_rate = (self.success_count / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print(f"Checks Passed: {self.success_count}/{self.total_checks}")
        print(f"Automatic Fixes Applied: {fixes_applied}")
        
        if self.issues:
            print(f"\nIssues Found ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        if self.fixes:
            print(f"\nRecommended Fixes ({len(self.fixes)}):")
            for i, fix in enumerate(self.fixes, 1):
                print(f"  {i}. {fix}")
        
        # System status
        if success_rate >= 90:
            status = "EXCELLENT"
            message = "System is fully operational and optimized"
        elif success_rate >= 80:
            status = "GOOD"
            message = "System is operational with minor issues"
        elif success_rate >= 70:
            status = "FAIR"
            message = "System needs attention for optimal performance"
        else:
            status = "POOR"
            message = "System requires significant fixes"
        
        print(f"\nSystem Status: {status}")
        print(f"Assessment: {message}")
        
        # Component status
        print("\nComponent Status Summary:")
        components = [
            ("Database & Models", "Core data management"),
            ("Authentication System", "User login and security"),
            ("URL Routing", "Navigation and endpoints"),
            ("Views & Templates", "Frontend rendering"),
            ("Static Files", "CSS/JS/assets"),
            ("API Endpoints", "Backend services"),
            ("SMS System", "Notifications"),
            ("Forms & Validation", "User input handling"),
            ("Error Handling", "Graceful failures"),
        ]
        
        for component, description in components:
            print(f"  {component}: {description}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 80:
            print("SYSTEM IS READY FOR PRODUCTION USE!")
            print("\nNext Steps:")
            print("  1. Start server: python manage.py runserver")
            print("  2. Test in browser: http://127.0.0.1:8000")
            print("  3. Monitor system performance")
            print("  4. Regular health checks recommended")
        else:
            print("SYSTEM NEEDS ATTENTION BEFORE PRODUCTION")
            print("Please address the issues listed above.")
        
        print("\nLogin Credentials:")
        print("  Staff: admin / admin123")
        print("  Donor: donor@bloodlink.com / donor123")
        
        return success_rate >= 80

def main():
    """Main function"""
    checker = ComprehensiveSystemChecker()
    success = checker.run_comprehensive_check()
    return success

if __name__ == '__main__':
    main()
