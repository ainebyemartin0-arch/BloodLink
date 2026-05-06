#!/usr/bin/env python
"""
Comprehensive Frontend Debug Script for BloodLink System
Tests all frontend pages, templates, CSS, and functionality
"""

import os
import sys
import django
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.template import TemplateSyntaxError, TemplateDoesNotExist
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from accounts.models import StaffUser
from donors.models import Donor

class FrontendDebugger:
    def __init__(self):
        self.client = Client()
        self.results = {
            'staff_portal': {},
            'donor_portal': {},
            'public_pages': {},
            'templates': {},
            'assets': {},
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
    
    def test_staff_portal(self):
        """Test all staff portal pages"""
        print("\n🔍 Testing Staff Portal Frontend...")
        print("=" * 50)
        
        # Get staff user
        staff_user = StaffUser.objects.filter(is_staff=True).first()
        if not staff_user:
            self.log_result('staff_portal', 'Staff User Setup', 'FAIL', '', 'No staff user found')
            return
        
        self.client.force_login(staff_user)
        
        # Test staff pages
        staff_pages = [
            ('Dashboard', 'staff:dashboard', '/staff/dashboard/'),
            ('Blood Stock', 'staff:blood_stock', '/staff/blood-stock/'),
            ('Donor Requests', 'staff:donor_requests', '/staff/donor-requests/'),
            ('Emergency Requests', 'staff:emergency_requests', '/staff/emergency-requests/'),
            ('Public Requests', 'staff:public_requests_list', '/staff/public-requests/'),
            ('Reports', 'staff:reports', '/staff/reports/'),
        ]
        
        for page_name, url_name, url_path in staff_pages:
            try:
                # Test URL reversal
                try:
                    url = reverse(url_name)
                except:
                    url = url_path
                
                response = self.client.get(url)
                
                if response.status_code == 200:
                    # Check for template rendering issues
                    content = response.content.decode('utf-8')
                    if 'TemplateSyntaxError' in content or 'TemplateDoesNotExist' in content:
                        self.log_result('staff_portal', page_name, 'FAIL', '', 'Template rendering error')
                    elif '500' in content or 'Server Error' in content:
                        self.log_result('staff_portal', page_name, 'FAIL', '', 'Server error in response')
                    else:
                        self.log_result('staff_portal', page_name, 'PASS', f'HTTP {response.status_code}')
                else:
                    self.log_result('staff_portal', page_name, 'FAIL', f'HTTP {response.status_code}', 'Non-200 response')
                    
            except Exception as e:
                self.log_result('staff_portal', page_name, 'FAIL', '', str(e))
    
    def test_donor_portal(self):
        """Test all donor portal pages"""
        print("\n🔍 Testing Donor Portal Frontend...")
        print("=" * 50)
        
        # Get donor user
        donor = Donor.objects.first()
        if not donor:
            self.log_result('donor_portal', 'Donor User Setup', 'FAIL', '', 'No donor user found')
            return
        
        # Create donor session
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session['donor_id'] = donor.id
        session.save()
        self.client.cookies['sessionid'] = session.session_key
        
        # Test donor pages
        donor_pages = [
            ('Donor Dashboard', 'donor:dashboard', '/donor/dashboard/'),
            ('Donations', 'donor:donations', '/donor/donations/'),
            ('Donor Requests', 'donor:donor_requests', '/donor/requests/'),
            ('Profile', 'donor:profile', '/donor/profile/'),
            ('About', 'donor:about', '/donor/about/'),
            ('FAQ', 'donor:faq', '/donor/faq/'),
        ]
        
        for page_name, url_name, url_path in donor_pages:
            try:
                # Test URL reversal
                try:
                    url = reverse(url_name)
                except:
                    url = url_path
                
                response = self.client.get(url)
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    if 'TemplateSyntaxError' in content or 'TemplateDoesNotExist' in content:
                        self.log_result('donor_portal', page_name, 'FAIL', '', 'Template rendering error')
                    elif '500' in content or 'Server Error' in content:
                        self.log_result('donor_portal', page_name, 'FAIL', '', 'Server error in response')
                    else:
                        self.log_result('donor_portal', page_name, 'PASS', f'HTTP {response.status_code}')
                elif response.status_code == 302:
                    self.log_result('donor_portal', page_name, 'PASS', 'Redirect to login (expected)')
                else:
                    self.log_result('donor_portal', page_name, 'FAIL', f'HTTP {response.status_code}', 'Non-200/302 response')
                    
            except Exception as e:
                self.log_result('donor_portal', page_name, 'FAIL', '', str(e))
    
    def test_public_pages(self):
        """Test public pages"""
        print("\n🔍 Testing Public Pages...")
        print("=" * 50)
        
        # Test public pages
        public_pages = [
            ('Home', '/', '/'),
            ('Donor Register', 'donor:register', '/donor/register/'),
            ('Donor Login', 'donor:login', '/donor/login/'),
            ('Staff Login', '/staff/login/', '/staff/login/'),
            ('Contact', 'donor:contact', '/donor/contact/'),
        ]
        
        for page_name, url_name, url_path in public_pages:
            try:
                # Test URL reversal
                try:
                    url = reverse(url_name) if ':' in url_name else url_path
                except:
                    url = url_path
                
                response = self.client.get(url)
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    if 'TemplateSyntaxError' in content or 'TemplateDoesNotExist' in content:
                        self.log_result('public_pages', page_name, 'FAIL', '', 'Template rendering error')
                    elif '500' in content or 'Server Error' in content:
                        self.log_result('public_pages', page_name, 'FAIL', '', 'Server error in response')
                    else:
                        self.log_result('public_pages', page_name, 'PASS', f'HTTP {response.status_code}')
                else:
                    self.log_result('public_pages', page_name, 'FAIL', f'HTTP {response.status_code}', 'Non-200 response')
                    
            except Exception as e:
                self.log_result('public_pages', page_name, 'FAIL', '', str(e))
    
    def test_templates(self):
        """Test template syntax and existence"""
        print("\n🔍 Testing Templates...")
        print("=" * 50)
        
        template_paths = [
            'base_staff_modern.html',
            'base_donor_enhanced.html',
            'staff_portal/dashboard.html',
            'staff_portal/blood_stock.html',
            'donor_portal/dashboard.html',
            'donor_portal/donations.html',
        ]
        
        for template_path in template_paths:
            try:
                template = get_template(template_path)
                self.log_result('templates', template_path, 'PASS', 'Template loads successfully')
            except TemplateDoesNotExist:
                self.log_result('templates', template_path, 'FAIL', '', 'Template not found')
            except TemplateSyntaxError as e:
                self.log_result('templates', template_path, 'FAIL', '', f'Template syntax error: {e}')
            except Exception as e:
                self.log_result('templates', template_path, 'FAIL', '', str(e))
    
    def test_static_files(self):
        """Test static file accessibility"""
        print("\n🔍 Testing Static Files...")
        print("=" * 50)
        
        static_files = [
            'css/style.css',
            'js/main.js',
            'images/logo.png',
        ]
        
        for static_file in static_files:
            try:
                response = self.client.get(f'/static/{static_file}')
                if response.status_code == 200:
                    self.log_result('assets', static_file, 'PASS', f'HTTP {response.status_code}')
                else:
                    self.log_result('assets', static_file, 'FAIL', f'HTTP {response.status_code}', 'File not accessible')
            except Exception as e:
                self.log_result('assets', static_file, 'FAIL', '', str(e))
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "=" * 60)
        print("📊 FRONTEND DEBUG REPORT")
        print("=" * 60)
        
        summary = self.results['summary']
        print(f"\n📈 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   Success Rate: {(summary['passed']/summary['total_tests']*100):.1f}%" if summary['total_tests'] > 0 else "N/A")
        
        if summary['errors']:
            print(f"\n🚨 ERRORS FOUND:")
            for error in summary['errors']:
                print(f"   • {error}")
        
        # Detailed results
        for category in ['staff_portal', 'donor_portal', 'public_pages', 'templates', 'assets']:
            if self.results[category]:
                print(f"\n📋 {category.upper().replace('_', ' ')}:")
                for test_name, result in self.results[category].items():
                    status_icon = "✅" if result['status'] == 'PASS' else "❌"
                    print(f"   {status_icon} {test_name}: {result['status']}")
                    if result['error']:
                        print(f"      Error: {result['error']}")
        
        return self.results
    
    def run_all_tests(self):
        """Run all frontend tests"""
        print("🚀 Starting Comprehensive Frontend Debug...")
        print("=" * 60)
        
        self.test_staff_portal()
        self.test_donor_portal()
        self.test_public_pages()
        self.test_templates()
        self.test_static_files()
        
        return self.generate_report()

def main():
    """Main function"""
    debugger = FrontendDebugger()
    results = debugger.run_all_tests()
    
    # Save results to file
    with open('frontend_debug_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: frontend_debug_results.json")
    
    return results

if __name__ == '__main__':
    main()
