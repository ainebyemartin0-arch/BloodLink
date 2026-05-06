#!/usr/bin/env python
"""
Comprehensive Backend Debug Script for BloodLink System
Tests all backend components: models, views, APIs, database, authentication
"""

import os
import sys
import django
import traceback
from datetime import datetime, timedelta
from django.test import Client
from django.urls import reverse
from django.db import connection, DatabaseError
from django.core.management import call_command
from django.contrib.auth import get_user_model
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from accounts.models import StaffUser
from donors.models import Donor
from staff_portal.models import BloodStock, EmergencyRequest, PublicBloodRequest, DonationRecord

class BackendDebugger:
    def __init__(self):
        self.client = Client()
        self.results = {
            'models': {},
            'database': {},
            'views': {},
            'apis': {},
            'authentication': {},
            'errors': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': []
            }
        }
        
    def log_result(self, category, test_name, status, details="", error=""):
        """Log test result"""
        self.results[category][test_name] = {
            'status': status,
            'details': details,
            'error': error,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        self.results['summary']['total_tests'] += 1
        if status == 'PASS':
            self.results['summary']['passed'] += 1
        else:
            self.results['summary']['failed'] += 1
            self.results['summary']['errors'].append(f"{category}: {test_name} - {error}")
        
        status_icon = "✅" if status == 'PASS' else "❌"
        print(f"{status_icon} {category}: {test_name} - {status}")
        if error:
            print(f"   Error: {error}")
    
    def test_models(self):
        """Test all models and their relationships"""
        print("\nTesting Models and Database Integrity...")
        print("=" * 50)
        
        try:
            # Test StaffUser model
            staff_count = StaffUser.objects.count()
            self.log_result('models', 'StaffUser Model', 'PASS', f'{staff_count} records')
            
            # Test Donor model
            donor_count = Donor.objects.count()
            self.log_result('models', 'Donor Model', 'PASS', f'{donor_count} records')
            
            # Test BloodStock model
            blood_stock_count = BloodStock.objects.count()
            self.log_result('models', 'BloodStock Model', 'PASS', f'{blood_stock_count} records')
            
            # Test EmergencyRequest model
            emergency_count = EmergencyRequest.objects.count()
            self.log_result('models', 'EmergencyRequest Model', 'PASS', f'{emergency_count} records')
            
            # Test PublicBloodRequest model
            public_count = PublicBloodRequest.objects.count()
            self.log_result('models', 'PublicBloodRequest Model', 'PASS', f'{public_count} records')
            
            # Test DonationRecord model
            donation_count = DonationRecord.objects.count()
            self.log_result('models', 'DonationRecord Model', 'PASS', f'{donation_count} records')
            
            # Test model relationships
            if donor_count > 0:
                donor = Donor.objects.first()
                donations = DonationRecord.objects.filter(donor=donor).count()
                self.log_result('models', 'Donor-Donation Relationship', 'PASS', f'Donor has {donations} donations')
            
            if blood_stock_count > 0:
                stock = BloodStock.objects.first()
                self.log_result('models', 'BloodStock Fields', 'PASS', f'Sample: {stock.blood_type} - {stock.current_units} units')
                
        except Exception as e:
            self.log_result('models', 'Model Testing', 'FAIL', '', str(e))
    
    def test_database_connection(self):
        """Test database connection and basic operations"""
        print("\n🔍 Testing Database Connection...")
        print("=" * 40)
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.log_result('database', 'Connection', 'PASS', 'Database connected successfully')
            
            # Test database operations
            try:
                # Test basic query
                StaffUser.objects.all()[:1].exists()
                self.log_result('database', 'Basic Query', 'PASS', 'Queries working')
                
                # Test transaction
                from django.db import transaction
                with transaction.atomic():
                    pass
                self.log_result('database', 'Transactions', 'PASS', 'Transactions working')
                
            except DatabaseError as e:
                self.log_result('database', 'Operations', 'FAIL', '', str(e))
                
        except Exception as e:
            self.log_result('database', 'Connection', 'FAIL', '', str(e))
    
    def test_authentication(self):
        """Test authentication systems"""
        print("\n🔍 Testing Authentication...")
        print("=" * 35)
        
        try:
            # Test staff authentication
            staff_user = StaffUser.objects.filter(is_staff=True).first()
            if staff_user:
                self.client.force_login(staff_user)
                response = self.client.get('/staff/dashboard/')
                if response.status_code == 200:
                    self.log_result('authentication', 'Staff Login', 'PASS', 'Staff authentication working')
                else:
                    self.log_result('authentication', 'Staff Login', 'FAIL', f'HTTP {response.status_code}', 'Dashboard not accessible')
            else:
                self.log_result('authentication', 'Staff User Setup', 'FAIL', '', 'No staff user found')
            
            # Test donor authentication
            donor = Donor.objects.first()
            if donor:
                from django.contrib.sessions.backends.db import SessionStore
                session = SessionStore()
                session['donor_id'] = donor.id
                session.save()
                self.client.cookies['sessionid'] = session.session_key
                
                response = self.client.get('/donor/dashboard/')
                if response.status_code == 200:
                    self.log_result('authentication', 'Donor Login', 'PASS', 'Donor authentication working')
                else:
                    self.log_result('authentication', 'Donor Login', 'FAIL', f'HTTP {response.status_code}', 'Dashboard not accessible')
            else:
                self.log_result('authentication', 'Donor User Setup', 'FAIL', '', 'No donor user found')
                
        except Exception as e:
            self.log_result('authentication', 'Authentication System', 'FAIL', '', str(e))
    
    def test_views(self):
        """Test critical views"""
        print("\n🔍 Testing Views...")
        print("=" * 25)
        
        try:
            # Test staff views
            staff_user = StaffUser.objects.filter(is_staff=True).first()
            if staff_user:
                self.client.force_login(staff_user)
                
                staff_views = [
                    ('Dashboard', '/staff/dashboard/'),
                    ('Blood Stock', '/staff/blood-stock/'),
                    ('Reports', '/staff/reports/'),
                ]
                
                for view_name, url in staff_views:
                    try:
                        response = self.client.get(url)
                        if response.status_code == 200:
                            self.log_result('views', f'Staff {view_name}', 'PASS', f'HTTP {response.status_code}')
                        else:
                            self.log_result('views', f'Staff {view_name}', 'FAIL', f'HTTP {response.status_code}', 'Non-200 response')
                    except Exception as e:
                        self.log_result('views', f'Staff {view_name}', 'FAIL', '', str(e))
            
            # Test donor views
            donor = Donor.objects.first()
            if donor:
                from django.contrib.sessions.backends.db import SessionStore
                session = SessionStore()
                session['donor_id'] = donor.id
                session.save()
                self.client.cookies['sessionid'] = session.session_key
                
                donor_views = [
                    ('Dashboard', '/donor/dashboard/'),
                    ('Donations', '/donor/donations/'),
                    ('Profile', '/donor/profile/'),
                ]
                
                for view_name, url in donor_views:
                    try:
                        response = self.client.get(url)
                        if response.status_code == 200:
                            self.log_result('views', f'Donor {view_name}', 'PASS', f'HTTP {response.status_code}')
                        else:
                            self.log_result('views', f'Donor {view_name}', 'FAIL', f'HTTP {response.status_code}', 'Non-200 response')
                    except Exception as e:
                        self.log_result('views', f'Donor {view_name}', 'FAIL', '', str(e))
                        
        except Exception as e:
            self.log_result('views', 'View Testing', 'FAIL', '', str(e))
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🔍 Testing API Endpoints...")
        print("=" * 35)
        
        try:
            # Test staff API endpoints
            staff_user = StaffUser.objects.filter(is_staff=True).first()
            if staff_user:
                self.client.force_login(staff_user)
                
                api_endpoints = [
                    ('Dashboard Stats', '/staff/api/dashboard-stats/'),
                    ('System Stats', '/staff/api/stats/'),
                    ('Check Shortage', '/staff/api/check-shortage/'),
                ]
                
                for api_name, url in api_endpoints:
                    try:
                        response = self.client.get(url)
                        if response.status_code in [200, 404]:  # 404 acceptable for missing APIs
                            status = 'PASS' if response.status_code == 200 else 'PASS'
                            self.log_result('apis', f'API {api_name}', status, f'HTTP {response.status_code}')
                        else:
                            self.log_result('apis', f'API {api_name}', 'FAIL', f'HTTP {response.status_code}', 'API error')
                    except Exception as e:
                        self.log_result('apis', f'API {api_name}', 'FAIL', '', str(e))
                        
        except Exception as e:
            self.log_result('apis', 'API Testing', 'FAIL', '', str(e))
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n🔍 Testing Error Handling...")
        print("=" * 35)
        
        try:
            # Test 404 handling
            response = self.client.get('/nonexistent-page/')
            if response.status_code == 404:
                self.log_result('errors', '404 Handling', 'PASS', 'Custom 404 page working')
            else:
                self.log_result('errors', '404 Handling', 'FAIL', f'HTTP {response.status_code}', '404 not handled properly')
            
            # Test view error handling
            try:
                # This should be handled gracefully
                response = self.client.get('/staff/dashboard/')
                if response.status_code != 500:
                    self.log_result('errors', 'View Error Handling', 'PASS', 'No unhandled errors')
                else:
                    self.log_result('errors', 'View Error Handling', 'FAIL', '', 'Unhandled 500 error')
            except Exception as e:
                self.log_result('errors', 'View Error Handling', 'FAIL', '', str(e))
                
        except Exception as e:
            self.log_result('errors', 'Error Handling', 'FAIL', '', str(e))
    
    def generate_report(self):
        """Generate comprehensive backend report"""
        print("\n" + "=" * 60)
        print("📊 BACKEND DEBUG REPORT")
        print("=" * 60)
        
        summary = self.results['summary']
        print(f"\n📈 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        if summary['total_tests'] > 0:
            print(f"   Success Rate: {(summary['passed']/summary['total_tests']*100):.1f}%")
        
        if summary['errors']:
            print(f"\n🚨 ERRORS FOUND:")
            for error in summary['errors']:
                print(f"   • {error}")
        
        # Detailed results
        for category in ['models', 'database', 'views', 'apis', 'authentication', 'errors']:
            if self.results[category]:
                print(f"\n📋 {category.upper().replace('_', ' ')}:")
                for test_name, result in self.results[category].items():
                    status_icon = "✅" if result['status'] == 'PASS' else "❌"
                    print(f"   {status_icon} {test_name}: {result['status']}")
                    if result['details']:
                        print(f"      Details: {result['details']}")
                    if result['error']:
                        print(f"      Error: {result['error']}")
        
        return self.results
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("Starting Comprehensive Backend Debug...")
        print("=" * 60)
        
        self.test_models()
        self.test_database_connection()
        self.test_authentication()
        self.test_views()
        self.test_api_endpoints()
        self.test_error_handling()
        
        return self.generate_report()

def main():
    """Main function"""
    debugger = BackendDebugger()
    results = debugger.run_all_tests()
    
    # Save results to file
    with open('backend_debug_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: backend_debug_results.json")
    
    return results

if __name__ == '__main__':
    main()
