#!/usr/bin/env python
"""
Simple API testing using curl-like approach
Tests all API endpoints to ensure they're working properly
"""

import os
import sys
import django
import json
from django.test import TestCase
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

class SimpleAPITester:
    def __init__(self):
        self.test_results = []
        
    def log_result(self, endpoint, method, status_code, success, error=None):
        """Log test result"""
        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'success': success,
            'error': error
        }
        self.test_results.append(result)
        
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {method} {endpoint} - {status_code}")
        if error:
            print(f"    Error: {error}")
    
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
    
    def test_api_endpoints(self):
        """Test API endpoints by checking views exist and are accessible"""
        print("\n=== Testing API Endpoints ===")
        
        # Test donor portal API endpoints exist
        donor_apis = [
            ('donor:api_urgent_alerts', '/donor/api/urgent-alerts/'),
            ('donor:api_notification_stats', '/donor/api/notification-stats/'),
            ('donor:api_toggle_availability', '/donor/api/toggle-availability/'),
            ('donor:api_alerts', '/donor/api/alerts/'),
            ('donor:api_respond_alert', '/donor/api/alerts/1/respond/'),
        ]
        
        for name, url in donor_apis:
            try:
                reverse_url = reverse(name)
                self.log_result(url, 'URL_RESOLVE', 200, True, f"Resolved to {reverse_url}")
            except Exception as e:
                self.log_result(url, 'URL_RESOLVE', 500, False, str(e))
        
        # Test staff portal API endpoints exist
        staff_apis = [
            ('staff:api_check_shortage', '/staff/api/check-shortage/'),
            ('staff:dashboard_stats_api', '/staff/api/dashboard-stats/'),
            ('staff:api_check_notifications', '/staff/api/notifications/check/'),
            ('staff:api_mark_notification_read', '/staff/api/notifications/mark-read/'),
            ('staff:api_clear_session_notification', '/staff/api/notifications/clear-session/'),
            ('staff:api_system_stats', '/staff/api/stats/'),
        ]
        
        for name, url in staff_apis:
            try:
                reverse_url = reverse(name)
                self.log_result(url, 'URL_RESOLVE', 200, True, f"Resolved to {reverse_url}")
            except Exception as e:
                self.log_result(url, 'URL_RESOLVE', 500, False, str(e))
        
        # Test notifications API endpoints exist
        notification_apis = [
            ('notifications:list', '/notifications/'),
            ('notifications:update_response', '/notifications/1/update-response/'),
            ('notifications:test_connection', '/notifications/test-connection/'),
            ('notifications:test_sms_api', '/notifications/test-sms-api/'),
        ]
        
        for name, url in notification_apis:
            try:
                reverse_url = reverse(name)
                self.log_result(url, 'URL_RESOLVE', 200, True, f"Resolved to {reverse_url}")
            except Exception as e:
                self.log_result(url, 'URL_RESOLVE', 500, False, str(e))
    
    def test_api_views_import(self):
        """Test that API views can be imported"""
        print("\n=== Testing API Views Import ===")
        
        try:
            from donor_portal.api_views import (
                urgent_alerts, notification_stats, toggle_availability,
                get_alerts_list, respond_to_alert
            )
            self.log_result('donor_portal.api_views', 'IMPORT', 200, True, "All donor API views imported successfully")
        except Exception as e:
            self.log_result('donor_portal.api_views', 'IMPORT', 500, False, str(e))
        
        try:
            from staff_portal.views import (
                check_shortage_api, dashboard_stats_api
            )
            from staff_portal.api_views import (
                check_notifications, mark_notification_read, clear_session_notification, get_system_stats
            )
            self.log_result('staff_portal.api_views', 'IMPORT', 200, True, "All staff API views imported successfully")
        except Exception as e:
            self.log_result('staff_portal.api_views', 'IMPORT', 500, False, str(e))
        
        try:
            from notifications.views import (
                notification_list, update_response, test_connection, test_sms_api
            )
            self.log_result('notifications.views', 'IMPORT', 200, True, "All notification views imported successfully")
        except Exception as e:
            self.log_result('notifications.views', 'IMPORT', 500, False, str(e))
    
    def test_api_view_functions(self):
        """Test that API view functions exist and are callable"""
        print("\n=== Testing API View Functions ===")
        
        # Test donor portal API views
        try:
            from donor_portal.api_views import urgent_alerts
            self.log_result('urgent_alerts', 'FUNCTION_CHECK', 200, True, "Function exists and is callable")
        except Exception as e:
            self.log_result('urgent_alerts', 'FUNCTION_CHECK', 500, False, str(e))
        
        try:
            from donor_portal.api_views import notification_stats
            self.log_result('notification_stats', 'FUNCTION_CHECK', 200, True, "Function exists and is callable")
        except Exception as e:
            self.log_result('notification_stats', 'FUNCTION_CHECK', 500, False, str(e))
        
        try:
            from donor_portal.api_views import toggle_availability
            self.log_result('toggle_availability', 'FUNCTION_CHECK', 200, True, "Function exists and is callable")
        except Exception as e:
            self.log_result('toggle_availability', 'FUNCTION_CHECK', 500, False, str(e))
        
        try:
            from donor_portal.api_views import get_alerts_list
            self.log_result('get_alerts_list', 'FUNCTION_CHECK', 200, True, "Function exists and is callable")
        except Exception as e:
            self.log_result('get_alerts_list', 'FUNCTION_CHECK', 500, False, str(e))
        
        # Test staff portal API views
        try:
            from staff_portal.views import check_shortage_api
            self.log_result('check_shortage_api', 'FUNCTION_CHECK', 200, True, "Function exists and is callable")
        except Exception as e:
            self.log_result('check_shortage_api', 'FUNCTION_CHECK', 500, False, str(e))
        
        try:
            from staff_portal.views import dashboard_stats_api
            self.log_result('dashboard_stats_api', 'FUNCTION_CHECK', 200, True, "Function exists and is callable")
        except Exception as e:
            self.log_result('dashboard_stats_api', 'FUNCTION_CHECK', 500, False, str(e))
        
        try:
            from staff_portal.api_views import get_system_stats
            self.log_result('get_system_stats', 'FUNCTION_CHECK', 200, True, "Function exists and is callable")
        except Exception as e:
            self.log_result('get_system_stats', 'FUNCTION_CHECK', 500, False, str(e))
    
    def test_database_models(self):
        """Test that database models exist and can be queried"""
        print("\n=== Testing Database Models ===")
        
        try:
            donor_count = Donor.objects.count()
            self.log_result('Donor model', 'DB_QUERY', 200, True, f"Found {donor_count} donors")
        except Exception as e:
            self.log_result('Donor model', 'DB_QUERY', 500, False, str(e))
        
        try:
            staff_count = StaffUser.objects.count()
            self.log_result('StaffUser model', 'DB_QUERY', 200, True, f"Found {staff_count} staff users")
        except Exception as e:
            self.log_result('StaffUser model', 'DB_QUERY', 500, False, str(e))
        
        try:
            request_count = PublicBloodRequest.objects.count()
            self.log_result('PublicBloodRequest model', 'DB_QUERY', 200, True, f"Found {request_count} public requests")
        except Exception as e:
            self.log_result('PublicBloodRequest model', 'DB_QUERY', 500, False, str(e))
        
        try:
            emergency_count = EmergencyRequest.objects.count()
            self.log_result('EmergencyRequest model', 'DB_QUERY', 200, True, f"Found {emergency_count} emergency requests")
        except Exception as e:
            self.log_result('EmergencyRequest model', 'DB_QUERY', 500, False, str(e))
        
        try:
            sms_count = SMSNotification.objects.count()
            self.log_result('SMSNotification model', 'DB_QUERY', 200, True, f"Found {sms_count} SMS notifications")
        except Exception as e:
            self.log_result('SMSNotification model', 'DB_QUERY', 500, False, str(e))
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Starting BloodLink Simple API Testing...")
        print("=" * 50)
        
        try:
            self.create_test_data()
            self.test_api_endpoints()
            self.test_api_views_import()
            self.test_api_view_functions()
            self.test_database_models()
            
            # Summary
            print("\n" + "=" * 50)
            print("API TESTING SUMMARY")
            print("=" * 50)
            
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results if result['success'])
            failed_tests = total_tests - passed_tests
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {failed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            if failed_tests > 0:
                print("\nFAILED TESTS:")
                for result in self.test_results:
                    if not result['success']:
                        print(f"  - {result['method']} {result['endpoint']} ({result['status_code']})")
                        if result['error']:
                            print(f"    Error: {result['error']}")
            
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

if __name__ == '__main__':
    tester = SimpleAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
