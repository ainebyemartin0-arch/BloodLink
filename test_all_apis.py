#!/usr/bin/env python
"""
Comprehensive API testing script for BloodLink system
Tests all API endpoints to ensure they're working properly
"""

import os
import sys
import django
import json
from django.test import Client, TestCase
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

class APITester:
    def __init__(self):
        self.client = Client()
        self.test_results = []
        
        # Override default client settings
        self.client.defaults['HTTP_HOST'] = '127.0.0.1:8000'
        
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
        
        # Create test emergency request first
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
    
    def test_donor_portal_apis(self):
        """Test donor portal API endpoints"""
        print("\n=== Testing Donor Portal APIs ===")
        
        # Test urgent alerts API (without login)
        response = self.client.get('/donor/api/urgent-alerts/', HTTP_HOST='127.0.0.1:8000')
        self.log_result('/donor/api/urgent-alerts/', 'GET', response.status_code, 
                       response.status_code == 200)
        
        # Test urgent alerts API (with donor login)
        self.client.login(email='donor@test.com', password='donorpass123')
        response = self.client.get('/donor/api/urgent-alerts/')
        self.log_result('/donor/api/urgent-alerts/', 'GET (authenticated)', response.status_code,
                       response.status_code == 200)
        
        # Test notification stats API
        response = self.client.get('/donor/api/notification-stats/')
        self.log_result('/donor/api/notification-stats/', 'GET', response.status_code,
                       response.status_code == 200)
        
        # Test toggle availability API (GET)
        response = self.client.get('/donor/api/toggle-availability/')
        self.log_result('/donor/api/toggle-availability/', 'GET', response.status_code,
                       response.status_code in [200, 405])  # 405 if only POST allowed
        
        # Test toggle availability API (POST)
        response = self.client.post('/donor/api/toggle-availability/', 
                                   {'available': 'true'})
        self.log_result('/donor/api/toggle-availability/', 'POST', response.status_code,
                       response.status_code == 200)
        
        # Test alerts list API
        response = self.client.get('/donor/api/alerts/')
        self.log_result('/donor/api/alerts/', 'GET', response.status_code,
                       response.status_code == 200)
        
        # Test respond to alert API
        response = self.client.post(f'/donor/api/alerts/{self.sms_notification.pk}/respond/',
                                   {'response': 'confirmed'})
        self.log_result('/donor/api/alerts/respond/', 'POST', response.status_code,
                       response.status_code in [200, 404])  # 404 if alert not found
        
        self.client.logout()
    
    def test_staff_portal_apis(self):
        """Test staff portal API endpoints"""
        print("\n=== Testing Staff Portal APIs ===")
        
        # Login as staff
        self.client.login(username='teststaff', password='testpass123')
        
        # Test shortage check API
        response = self.client.get('/staff/api/check-shortage/')
        self.log_result('/staff/api/check-shortage/', 'GET', response.status_code,
                       response.status_code == 200)
        
        # Test dashboard stats API
        response = self.client.get('/staff/api/dashboard-stats/')
        self.log_result('/staff/api/dashboard-stats/', 'GET', response.status_code,
                       response.status_code == 200)
        
        # Test notifications check API
        response = self.client.get('/staff/api/notifications/check/')
        self.log_result('/staff/api/notifications/check/', 'GET', response.status_code,
                       response.status_code == 200)
        
        # Test mark notification read API
        response = self.client.post('/staff/api/notifications/mark-read/',
                                   {'notification_id': self.sms_notification.pk})
        self.log_result('/staff/api/notifications/mark-read/', 'POST', response.status_code,
                       response.status_code in [200, 404])
        
        # Test clear session notification API
        response = self.client.post('/staff/api/notifications/clear-session/')
        self.log_result('/staff/api/notifications/clear-session/', 'POST', response.status_code,
                       response.status_code == 200)
        
        # Test system stats API
        response = self.client.get('/staff/api/stats/')
        self.log_result('/staff/api/stats/', 'GET', response.status_code,
                       response.status_code == 200)
        
        self.client.logout()
    
    def test_notifications_apis(self):
        """Test notifications API endpoints"""
        print("\n=== Testing Notifications APIs ===")
        
        # Login as staff
        self.client.login(username='teststaff', password='testpass123')
        
        # Test notification list
        response = self.client.get('/notifications/')
        self.log_result('/notifications/', 'GET', response.status_code,
                       response.status_code == 200)
        
        # Test update response
        response = self.client.post(f'/notifications/{self.sms_notification.pk}/update-response/',
                                   {'response': 'confirmed'})
        self.log_result('/notifications/update-response/', 'POST', response.status_code,
                       response.status_code in [200, 302])  # 302 if redirect after update
        
        # Test connection
        response = self.client.get('/notifications/test-connection/')
        self.log_result('/notifications/test-connection/', 'GET', response.status_code,
                       response.status_code == 200)
        
        # Test SMS API
        response = self.client.get('/notifications/test-sms-api/')
        self.log_result('/notifications/test-sms-api/', 'GET', response.status_code,
                       response.status_code == 200)
        
        self.client.logout()
    
    def test_authentication_apis(self):
        """Test authentication-related API endpoints"""
        print("\n=== Testing Authentication APIs ===")
        
        # Test Google login API (POST)
        response = self.client.post('/donor/google-login/', {
            'google_id': 'test_google_123',
            'email': 'google@test.com',
            'name': 'Google User'
        })
        self.log_result('/donor/google-login/', 'POST', response.status_code,
                       response.status_code == 200)
        
        # Test phone login API (POST)
        response = self.client.post('/donor/phone-login/', {
            'phone_number': '+256700000002'
        })
        self.log_result('/donor/phone-login/', 'POST', response.status_code,
                       response.status_code == 200)
        
        # Test toggle availability (direct API call)
        response = self.client.post('/donor/toggle-availability/', 
                                   {'available': 'true'})
        self.log_result('/donor/toggle-availability/', 'POST', response.status_code,
                       response.status_code in [200, 302])  # 302 if redirect after login
    
    def test_error_handling(self):
        """Test API error handling"""
        print("\n=== Testing Error Handling ===")
        
        # Test 404 for non-existent alert
        self.client.login(email='donor@test.com', password='donorpass123')
        response = self.client.post('/donor/api/alerts/99999/respond/', {'response': 'confirmed'})
        self.log_result('/donor/api/alerts/99999/respond/', 'POST (404 test)', response.status_code,
                       response.status_code == 404)
        
        # Test unauthorized access
        self.client.logout()
        response = self.client.get('/staff/api/dashboard-stats/')
        self.log_result('/staff/api/dashboard-stats/', 'GET (unauthorized)', response.status_code,
                       response.status_code == 302)  # Redirect to login
        
        # Test invalid method
        self.client.login(username='teststaff', password='testpass123')
        response = self.client.delete('/staff/api/check-shortage/')
        self.log_result('/staff/api/check-shortage/', 'DELETE (invalid method)', response.status_code,
                       response.status_code == 405)
        
        self.client.logout()
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Starting BloodLink API Testing...")
        print("=" * 50)
        
        try:
            self.create_test_data()
            self.test_donor_portal_apis()
            self.test_staff_portal_apis()
            self.test_notifications_apis()
            self.test_authentication_apis()
            self.test_error_handling()
            
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
                DonationRecord.objects.all().delete()
                Donor.objects.all().delete()
                StaffUser.objects.all().delete()
                print("\nTest data cleaned up")
            except Exception as e:
                print(f"Error cleaning up test data: {str(e)}")

if __name__ == '__main__':
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
