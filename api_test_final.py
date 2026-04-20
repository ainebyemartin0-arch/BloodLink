#!/usr/bin/env python
"""
Final API testing and verification for BloodLink system
Tests all API endpoints and provides comprehensive status report
"""

import os
import sys
import django
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Import models after Django setup
from donors.models import Donor
from accounts.models import StaffUser
from staff_portal.models import PublicBloodRequest, DonationRecord, EmergencyRequest
from notifications.models import SMSNotification

User = get_user_model()

class FinalAPITester:
    def __init__(self):
        self.test_results = []
        self.api_endpoints = []
        
    def log_result(self, category, test_name, status, details=None):
        """Log test result"""
        result = {
            'category': category,
            'test': test_name,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        
        status_icon = "PASS" if status == "PASS" else "FAIL"
        print(f"[{status_icon}] {category} - {test_name}")
        if details:
            print(f"    {details}")
    
    def create_test_data(self):
        """Create test data for API testing"""
        # Create test staff user
        self.staff_user = StaffUser.objects.create_user(
            username='teststaff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True,
            is_active=True,
            is_approved=True
        )
        
        # Create test donor
        from datetime import date
        self.donor = Donor.objects.create(
            full_name='Test Donor',
            email='donor@test.com',
            phone_number='+256700000001',
            blood_type='O+',
            location='Kampala Central',
            gender='Male',
            date_of_birth=date(1990, 1, 1),
            is_available=True,
            is_active=True
        )
        self.donor.set_password('donorpass123')
        self.donor.save()
        
        # Create test blood request
        self.blood_request = PublicBloodRequest.objects.create(
            requester_name='Test Requester',
            requester_phone='+256700000002',
            requester_relationship='Family Member',
            patient_name='Test Patient',
            blood_type_needed='O+',
            units_needed=2,
            urgency_level='urgent',
            hospital_ward='Test Ward',
            status='pending'
        )
        
        # Create test emergency request
        self.emergency_request = EmergencyRequest.objects.create(
            patient_name='Test Emergency Patient',
            blood_type_needed='O+',
            units_needed=2,
            urgency_level='critical',
            ward='Emergency Ward',
            created_by=self.staff_user
        )
        
        # Create test SMS notification
        self.sms_notification = SMSNotification.objects.create(
            donor=self.donor,
            emergency_request=self.emergency_request,
            message_content='Test SMS notification',
            delivery_status='sent'
        )
        
        print("Test data created successfully")
    
    def catalog_all_api_endpoints(self):
        """Catalog all API endpoints in the system"""
        print("\n=== API ENDPOINTS CATALOG ===")
        
        # Donor Portal APIs
        donor_apis = [
            {
                'name': 'Urgent Alerts API',
                'url': '/donor/api/urgent-alerts/',
                'method': 'GET',
                'description': 'Get urgent SMS alerts for logged-in donor',
                'auth_required': True,
                'category': 'Donor Portal'
            },
            {
                'name': 'Notification Stats API',
                'url': '/donor/api/notification-stats/',
                'method': 'GET',
                'description': 'Get notification statistics',
                'auth_required': True,
                'category': 'Donor Portal'
            },
            {
                'name': 'Toggle Availability API',
                'url': '/donor/api/toggle-availability/',
                'method': 'POST',
                'description': 'Toggle donor availability status',
                'auth_required': True,
                'category': 'Donor Portal'
            },
            {
                'name': 'Alerts List API',
                'url': '/donor/api/alerts/',
                'method': 'GET',
                'description': 'Get list of blood alerts',
                'auth_required': True,
                'category': 'Donor Portal'
            },
            {
                'name': 'Respond to Alert API',
                'url': '/donor/api/alerts/<int:alert_id>/respond/',
                'method': 'POST',
                'description': 'Respond to a blood alert',
                'auth_required': True,
                'category': 'Donor Portal'
            }
        ]
        
        # Staff Portal APIs
        staff_apis = [
            {
                'name': 'Check Shortage API',
                'url': '/staff/api/check-shortage/',
                'method': 'POST',
                'description': 'Check for blood shortages',
                'auth_required': True,
                'category': 'Staff Portal'
            },
            {
                'name': 'Dashboard Stats API',
                'url': '/staff/api/dashboard-stats/',
                'method': 'GET',
                'description': 'Get dashboard statistics',
                'auth_required': True,
                'category': 'Staff Portal'
            },
            {
                'name': 'Check Notifications API',
                'url': '/staff/api/notifications/check/',
                'method': 'GET',
                'description': 'Check for new notifications',
                'auth_required': True,
                'category': 'Staff Portal'
            },
            {
                'name': 'Mark Notification Read API',
                'url': '/staff/api/notifications/mark-read/',
                'method': 'POST',
                'description': 'Mark notification as read',
                'auth_required': True,
                'category': 'Staff Portal'
            },
            {
                'name': 'Clear Session Notification API',
                'url': '/staff/api/notifications/clear-session/',
                'method': 'POST',
                'description': 'Clear session notifications',
                'auth_required': True,
                'category': 'Staff Portal'
            },
            {
                'name': 'System Stats API',
                'url': '/staff/api/stats/',
                'method': 'GET',
                'description': 'Get system statistics',
                'auth_required': True,
                'category': 'Staff Portal'
            }
        ]
        
        # Notifications APIs
        notification_apis = [
            {
                'name': 'Notification List API',
                'url': '/notifications/',
                'method': 'GET',
                'description': 'List all notifications',
                'auth_required': True,
                'category': 'Notifications'
            },
            {
                'name': 'Update Response API',
                'url': '/notifications/<int:pk>/update-response/',
                'method': 'POST',
                'description': 'Update notification response',
                'auth_required': True,
                'category': 'Notifications'
            },
            {
                'name': 'Test Connection API',
                'url': '/notifications/test-connection/',
                'method': 'GET',
                'description': 'Test notification connection',
                'auth_required': True,
                'category': 'Notifications'
            },
            {
                'name': 'Test SMS API',
                'url': '/notifications/test-sms-api/',
                'method': 'GET',
                'description': 'Test SMS API connection',
                'auth_required': True,
                'category': 'Notifications'
            }
        ]
        
        self.api_endpoints = donor_apis + staff_apis + notification_apis
        
        print(f"Found {len(self.api_endpoints)} API endpoints:")
        for category in ['Donor Portal', 'Staff Portal', 'Notifications']:
            category_endpoints = [api for api in self.api_endpoints if api['category'] == category]
            print(f"\n{category}:")
            for api in category_endpoints:
                print(f"  - {api['name']} ({api['method']})")
                print(f"    URL: {api['url']}")
                print(f"    {api['description']}")
                print(f"    Auth Required: {api['auth_required']}")
    
    def test_api_views_exist(self):
        """Test that all API view functions exist"""
        print("\n=== TESTING API VIEWS ===")
        
        # Test donor portal API views
        try:
            from donor_portal.api_views import (
                urgent_alerts, notification_stats, toggle_availability,
                get_alerts_list, respond_to_alert
            )
            self.log_result('API Views', 'Donor Portal Views', 'PASS', 'All 5 views imported successfully')
        except Exception as e:
            self.log_result('API Views', 'Donor Portal Views', 'FAIL', str(e))
        
        # Test staff portal API views
        try:
            from staff_portal.views import check_shortage_api, dashboard_stats_api
            from staff_portal.api_views import (
                check_notifications, mark_notification_read, clear_session_notification, get_system_stats
            )
            self.log_result('API Views', 'Staff Portal Views', 'PASS', 'All 6 views imported successfully')
        except Exception as e:
            self.log_result('API Views', 'Staff Portal Views', 'FAIL', str(e))
        
        # Test notifications API views
        try:
            from notifications.views import (
                notification_list, update_response, test_connection, test_sms_api
            )
            self.log_result('API Views', 'Notifications Views', 'PASS', 'All 4 views imported successfully')
        except Exception as e:
            self.log_result('API Views', 'Notifications Views', 'FAIL', str(e))
    
    def test_api_functionality(self):
        """Test API functionality with mock requests"""
        print("\n=== TESTING API FUNCTIONALITY ===")
        
        # Test donor portal API functionality
        try:
            from donor_portal.api_views import urgent_alerts
            from django.test import RequestFactory
            from django.contrib.sessions.middleware import SessionMiddleware
            
            # Create mock request
            factory = RequestFactory()
            request = factory.get('/donor/api/urgent-alerts/')
            request.user = self.donor
            
            # Test urgent alerts functionality
            try:
                result = urgent_alerts(request)
                if isinstance(result, dict) and 'alerts' in result:
                    self.log_result('Functionality', 'Urgent Alerts', 'PASS', 'Returns proper JSON response')
                else:
                    self.log_result('Functionality', 'Urgent Alerts', 'FAIL', 'Invalid response type')
            except Exception as e:
                self.log_result('Functionality', 'Urgent Alerts', 'FAIL', str(e))
                
        except Exception as e:
            self.log_result('Functionality', 'Urgent Alerts', 'FAIL', str(e))
        
        # Test staff portal API functionality
        try:
            from staff_portal.views import dashboard_stats_api
            from django.test import RequestFactory
            
            # Create mock request
            factory = RequestFactory()
            request = factory.get('/staff/api/dashboard-stats/')
            request.user = self.staff_user
            
            # Test dashboard stats functionality
            try:
                result = dashboard_stats_api(request)
                if isinstance(result, dict) and 'total_donors' in result:
                    self.log_result('Functionality', 'Dashboard Stats', 'PASS', 'Returns proper JSON response')
                else:
                    self.log_result('Functionality', 'Dashboard Stats', 'FAIL', 'Invalid response type')
            except Exception as e:
                self.log_result('Functionality', 'Dashboard Stats', 'FAIL', str(e))
                
        except Exception as e:
            self.log_result('Functionality', 'Dashboard Stats', 'FAIL', str(e))
    
    def test_database_integration(self):
        """Test database integration for APIs"""
        print("\n=== TESTING DATABASE INTEGRATION ===")
        
        # Test donor queries
        try:
            donors = Donor.objects.filter(is_active=True, is_available=True)
            self.log_result('Database', 'Donor Queries', 'PASS', f'Found {donors.count()} available donors')
        except Exception as e:
            self.log_result('Database', 'Donor Queries', 'FAIL', str(e))
        
        # Test emergency requests
        try:
            requests = EmergencyRequest.objects.filter(status='open')
            self.log_result('Database', 'Emergency Requests', 'PASS', f'Found {requests.count()} open requests')
        except Exception as e:
            self.log_result('Database', 'Emergency Requests', 'FAIL', str(e))
        
        # Test SMS notifications
        try:
            notifications = SMSNotification.objects.filter(delivery_status='sent')
            self.log_result('Database', 'SMS Notifications', 'PASS', f'Found {notifications.count()} sent notifications')
        except Exception as e:
            self.log_result('Database', 'SMS Notifications', 'FAIL', str(e))
    
    def test_url_patterns(self):
        """Test URL patterns are correctly configured"""
        print("\n=== TESTING URL PATTERNS ===")
        
        # Test donor portal URL patterns
        donor_patterns = [
            'donor:api_urgent_alerts',
            'donor:api_notification_stats',
            'donor:api_toggle_availability',
            'donor:api_alerts',
            'donor:api_respond_alert'
        ]
        
        for pattern in donor_patterns:
            try:
                url = reverse(pattern, args=[1]) if 'alert_id' in pattern else reverse(pattern)
                self.log_result('URL Patterns', f'Donor: {pattern}', 'PASS', f'Resolves to {url}')
            except Exception as e:
                self.log_result('URL Patterns', f'Donor: {pattern}', 'FAIL', str(e))
        
        # Test staff portal URL patterns
        staff_patterns = [
            'staff:api_check_shortage',
            'staff:dashboard_stats_api',
            'staff:api_check_notifications',
            'staff:api_mark_notification_read',
            'staff:api_clear_session_notification',
            'staff:api_system_stats'
        ]
        
        for pattern in staff_patterns:
            try:
                url = reverse(pattern)
                self.log_result('URL Patterns', f'Staff: {pattern}', 'PASS', f'Resolves to {url}')
            except Exception as e:
                self.log_result('URL Patterns', f'Staff: {pattern}', 'FAIL', str(e))
        
        # Test notifications URL patterns
        notification_patterns = [
            'notifications:list',
            'notifications:update_response',
            'notifications:test_connection',
            'notifications:test_sms_api'
        ]
        
        for pattern in notification_patterns:
            try:
                url = reverse(pattern, args=[1]) if 'pk' in pattern else reverse(pattern)
                self.log_result('URL Patterns', f'Notifications: {pattern}', 'PASS', f'Resolves to {url}')
            except Exception as e:
                self.log_result('URL Patterns', f'Notifications: {pattern}', 'FAIL', str(e))
    
    def generate_api_documentation(self):
        """Generate comprehensive API documentation"""
        print("\n" + "="*60)
        print("BLOODLINK API DOCUMENTATION")
        print("="*60)
        
        print("\n# OVERVIEW")
        print("The BloodLink system provides RESTful APIs for donor and staff portals.")
        print("All APIs return JSON responses and require authentication.")
        
        print("\n# AUTHENTICATION")
        print("All API endpoints require authentication:")
        print("- Donor Portal APIs: Donor login session")
        print("- Staff Portal APIs: Staff user login")
        print("- Notifications APIs: Staff user login")
        
        print("\n# RESPONSE FORMAT")
        print("All APIs return JSON responses with standard HTTP status codes:")
        print("- 200: Success")
        print("- 400: Bad Request")
        print("- 401: Unauthorized")
        print("- 403: Forbidden")
        print("- 404: Not Found")
        print("- 500: Server Error")
        
        print("\n# RATE LIMITING")
        print("No explicit rate limiting is implemented.")
        print("Consider implementing rate limiting for production use.")
        
        print("\n# ERROR HANDLING")
        print("All APIs include proper error handling with descriptive messages.")
        print("Errors are logged and returned in JSON format.")
        
        print("\n# SECURITY")
        print("- All APIs use Django's built-in CSRF protection")
        print("- Authentication is required for all endpoints")
        print("- Input validation is implemented in views")
        print("- SQL injection protection is provided by Django ORM")
        
        print("\n# MONITORING")
        print("- API requests are logged in Django admin")
        print("- Database queries are monitored")
        print("- Error tracking is implemented")
        
        print("\n# ENDPOINTS SUMMARY")
        print(f"Total API Endpoints: {len(self.api_endpoints)}")
        print(f"Categories: Donor Portal ({len([a for a in self.api_endpoints if a['category'] == 'Donor Portal'])}), Staff Portal ({len([a for a in self.api_endpoints if a['category'] == 'Staff Portal'])}), Notifications ({len([a for a in self.api_endpoints if a['category'] == 'Notifications'])})")
        
        print("\nFor detailed endpoint information, see the catalog above.")
    
    def run_comprehensive_test(self):
        """Run comprehensive API testing"""
        print("Starting BloodLink Comprehensive API Testing...")
        print("=" * 60)
        
        try:
            self.create_test_data()
            self.catalog_all_api_endpoints()
            self.test_api_views_exist()
            self.test_api_functionality()
            self.test_database_integration()
            self.test_url_patterns()
            self.generate_api_documentation()
            
            # Summary
            print("\n" + "="*60)
            print("COMPREHENSIVE API TESTING SUMMARY")
            print("="*60)
            
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results if result['status'] == 'PASS')
            failed_tests = total_tests - passed_tests
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {failed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            if failed_tests > 0:
                print("\nFAILED TESTS:")
                for result in self.test_results:
                    if result['status'] == 'FAIL':
                        print(f"  - {result['category']} - {result['test']}")
                        if result['details']:
                            print(f"    {result['details']}")
            
            print(f"\nAPI Testing Status: {'SUCCESS' if failed_tests == 0 else 'PARTIAL'}")
            
            return failed_tests == 0
            
        except Exception as e:
            print(f"Error during testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Clean up test data
            try:
                SMSNotification.objects.all().delete()
                PublicBloodRequest.objects.all().delete()
                EmergencyRequest.objects.all().delete()
                DonationRecord.objects.all().delete()
                Donor.objects.all().delete()
                StaffUser.objects.all().delete()
                print("\nTest data cleaned up")
            except Exception as e:
                print(f"Error cleaning up test data: {str(e)}")
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    tester = FinalAPITester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)
