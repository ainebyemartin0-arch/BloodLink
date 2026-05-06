#!/usr/bin/env python
"""
Comprehensive BloodLink System Error Audit
Identifies and fixes all potential server errors (500) and system issues
"""

import os
import sys
import django
import traceback
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"🔍 {title}")
    print("="*80)

def print_section(title):
    """Print formatted section"""
    print(f"\n📋 {title}")
    print("-" * 60)

def check_imports():
    """Check all critical imports"""
    print_section("Checking Critical Imports")
    
    import_checks = {
        'Django Core': ['django.db', 'django.http', 'django.urls'],
        'BloodLink Models': ['donors.models', 'staff_portal.models', 'notifications.models'],
        'Views': ['donor_portal.views', 'staff_portal.views'],
        'Utils': ['staff_portal.utils'],
        'PDF Generation': ['reportlab'],
        'SMS': ['notifications.mock_sms'],
    }
    
    issues = []
    
    for category, modules in import_checks.items():
        print(f"\n🔎 {category}:")
        for module in modules:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError as e:
                print(f"  ❌ {module} - {str(e)}")
                issues.append(f"{category}: {module} - {str(e)}")
    
    return issues

def check_models():
    """Check all model definitions and relationships"""
    print_section("Checking Model Definitions")
    
    issues = []
    
    try:
        from donors.models import Donor
        from staff_portal.models import EmergencyRequest, BloodStock, DonationRecord
        from notifications.models import SMSNotification
        
        print("✅ All model imports successful")
        
        # Check model fields
        print("\n🔎 Checking model fields:")
        
        # Donor model
        donor_fields = [f.name for f in Donor._meta.fields]
        required_donor_fields = ['full_name', 'phone_number', 'blood_type', 'is_available']
        for field in required_donor_fields:
            if field in donor_fields:
                print(f"  ✅ Donor.{field}")
            else:
                print(f"  ❌ Donor.{field} - Missing field")
                issues.append(f"Donor model missing field: {field}")
        
        # EmergencyRequest model
        emergency_fields = [f.name for f in EmergencyRequest._meta.fields]
        required_emergency_fields = ['blood_type_needed', 'units_needed', 'urgency_level', 'status']
        for field in required_emergency_fields:
            if field in emergency_fields:
                print(f"  ✅ EmergencyRequest.{field}")
            else:
                print(f"  ❌ EmergencyRequest.{field} - Missing field")
                issues.append(f"EmergencyRequest model missing field: {field}")
        
        # BloodStock model
        stock_fields = [f.name for f in BloodStock._meta.fields]
        required_stock_fields = ['blood_type', 'current_units', 'critical_level', 'minimum_level', 'optimal_level']
        for field in required_stock_fields:
            if field in stock_fields:
                print(f"  ✅ BloodStock.{field}")
            else:
                print(f"  ❌ BloodStock.{field} - Missing field")
                issues.append(f"BloodStock model missing field: {field}")
        
    except Exception as e:
        print(f"❌ Model check failed: {str(e)}")
        issues.append(f"Model import error: {str(e)}")
    
    return issues

def check_views():
    """Check all view functions for potential errors"""
    print_section("Checking View Functions")
    
    issues = []
    
    try:
        from donor_portal.views import fulfill_emergency_request
        from staff_portal.views import export_reports_pdf, request_fulfill
        from staff_portal.utils import check_request_fulfillment, auto_fulfill_request_from_donor_response
        
        print("✅ All view imports successful")
        
        # Check function signatures
        print("\n🔎 Checking function signatures:")
        
        functions_to_check = [
            ('donor_portal.views.fulfill_emergency_request', fulfill_emergency_request),
            ('staff_portal.views.export_reports_pdf', export_reports_pdf),
            ('staff_portal.views.request_fulfill', request_fulfill),
            ('staff_portal.utils.check_request_fulfillment', check_request_fulfillment),
            ('staff_portal.utils.auto_fulfill_request_from_donor_response', auto_fulfill_request_from_donor_response),
        ]
        
        for func_name, func in functions_to_check:
            if callable(func):
                print(f"  ✅ {func_name}")
            else:
                print(f"  ❌ {func_name} - Not callable")
                issues.append(f"Function not callable: {func_name}")
        
    except ImportError as e:
        print(f"❌ View import error: {str(e)}")
        issues.append(f"View import error: {str(e)}")
    except Exception as e:
        print(f"❌ View check failed: {str(e)}")
        issues.append(f"View check error: {str(e)}")
    
    return issues

def check_urls():
    """Check URL patterns for potential issues"""
    print_section("Checking URL Patterns")
    
    issues = []
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        # Test critical URLs
        critical_urls = [
            'staff:dashboard',
            'staff:blood_stock',
            'staff:public_requests_list',
            'staff:export_reports_pdf',
            'donor:dashboard',
            'donor:donor_requests',
        ]
        
        print("\n🔎 Testing URL reversals:")
        for url_name in critical_urls:
            try:
                url = reverse(url_name)
                print(f"  ✅ {url_name} -> {url}")
            except Exception as e:
                print(f"  ❌ {url_name} - {str(e)}")
                issues.append(f"URL reversal failed: {url_name} - {str(e)}")
        
    except Exception as e:
        print(f"❌ URL check failed: {str(e)}")
        issues.append(f"URL check error: {str(e)}")
    
    return issues

def check_templates():
    """Check template files for syntax errors"""
    print_section("Checking Template Syntax")
    
    issues = []
    
    template_dirs = [
        'templates/staff_portal',
        'templates/donor_portal',
        'templates/base',
    ]
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            print(f"\n🔎 Checking {template_dir}:")
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Check for common template errors
                            if '{% url ' in content and ' %}' not in content:
                                print(f"  ⚠️  {file} - Possible URL tag syntax error")
                                issues.append(f"Template syntax error: {file}")
                            else:
                                print(f"  ✅ {file}")
                        
                        except Exception as e:
                            print(f"  ❌ {file} - {str(e)}")
                            issues.append(f"Template read error: {file} - {str(e)}")
    
    return issues

def check_database():
    """Check database connectivity and data integrity"""
    print_section("Checking Database")
    
    issues = []
    
    try:
        from django.db import connection
        from donors.models import Donor
        from staff_portal.models import EmergencyRequest, BloodStock
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
        
        # Check data counts
        print("\n🔎 Checking data counts:")
        donor_count = Donor.objects.count()
        emergency_count = EmergencyRequest.objects.count()
        stock_count = BloodStock.objects.count()
        
        print(f"  ✅ Donors: {donor_count}")
        print(f"  ✅ Emergency Requests: {emergency_count}")
        print(f"  ✅ Blood Stock: {stock_count}")
        
        # Check BloodStock data integrity
        print("\n🔎 Checking BloodStock data integrity:")
        for stock in BloodStock.objects.all():
            if stock.current_units < 0:
                print(f"  ❌ {stock.blood_type} - Negative units: {stock.current_units}")
                issues.append(f"Negative stock units: {stock.blood_type}")
            elif stock.current_units > stock.optimal_level * 2:
                print(f"  ⚠️  {stock.blood_type} - Very high units: {stock.current_units}")
            else:
                print(f"  ✅ {stock.blood_type} - {stock.current_units} units")
        
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        issues.append(f"Database error: {str(e)}")
    
    return issues

def check_settings():
    """Check Django settings for potential issues"""
    print_section("Checking Django Settings")
    
    issues = []
    
    try:
        from django.conf import settings
        
        print("🔎 Checking critical settings:")
        
        critical_settings = {
            'DEBUG': getattr(settings, 'DEBUG', 'False'),
            'ALLOWED_HOSTS': getattr(settings, 'ALLOWED_HOSTS', []),
            'DATABASES': getattr(settings, 'DATABASES', {}),
            'STATIC_URL': getattr(settings, 'STATIC_URL', '/static/'),
            'MEDIA_URL': getattr(settings, 'MEDIA_URL', '/media/'),
        }
        
        for setting_name, setting_value in critical_settings.items():
            if setting_name == 'DEBUG':
                print(f"  ✅ {setting_name}: {setting_value}")
            elif setting_value:
                print(f"  ✅ {setting_name}")
            else:
                print(f"  ⚠️  {setting_name} - Not configured")
                issues.append(f"Missing setting: {setting_name}")
        
        # Check database configuration
        db_config = settings.DATABASES.get('default', {})
        if db_config.get('ENGINE') == 'django.db.backends.sqlite3':
            print("  ✅ Using SQLite database")
        elif db_config.get('ENGINE') == 'django.db.backends.postgresql':
            print("  ✅ Using PostgreSQL database")
        else:
            print(f"  ⚠️  Unknown database engine: {db_config.get('ENGINE')}")
            issues.append(f"Unknown database engine: {db_config.get('ENGINE')}")
        
    except Exception as e:
        print(f"❌ Settings check failed: {str(e)}")
        issues.append(f"Settings error: {str(e)}")
    
    return issues

def check_static_files():
    """Check static file configuration"""
    print_section("Checking Static Files")
    
    issues = []
    
    try:
        from django.conf import settings
        from django.templatetags.static import static
        
        print("🔎 Checking static file configuration:")
        
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        static_root = getattr(settings, 'STATIC_ROOT', None)
        
        print(f"  ✅ STATIC_URL: {static_url}")
        print(f"  ✅ STATIC_ROOT: {static_root or 'Not set'}")
        
        # Check if static directory exists
        if os.path.exists('static'):
            print("  ✅ Static directory exists")
        else:
            print("  ⚠️  Static directory not found")
            issues.append("Static directory not found")
        
    except Exception as e:
        print(f"❌ Static files check failed: {str(e)}")
        issues.append(f"Static files error: {str(e)}")
    
    return issues

def check_dependencies():
    """Check all required dependencies"""
    print_section("Checking Dependencies")
    
    issues = []
    
    try:
        try:
            from importlib import metadata
        except ImportError:
            import importlib_metadata as metadata
        
        # Read requirements.txt
        requirements_file = 'requirements.txt'
        if os.path.exists(requirements_file):
            with open(requirements_file, 'r') as f:
                requirements = f.read().splitlines()
            
            print("🔎 Checking installed packages:")
            
            for requirement in requirements:
                if requirement.strip() and not requirement.startswith('#'):
                    try:
                        # Extract package name (remove version specs)
                        package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        metadata.version(package_name)
                        print(f"  ✅ {requirement}")
                    except metadata.PackageNotFoundError:
                        print(f"  ❌ {requirement} - Not installed")
                        issues.append(f"Missing package: {requirement}")
                    except Exception as e:
                        print(f"  ⚠️  {requirement} - Version conflict: {str(e)}")
                        issues.append(f"Version conflict: {requirement} - {str(e)}")
        
    except Exception as e:
        print(f"❌ Dependencies check failed: {str(e)}")
        issues.append(f"Dependencies error: {str(e)}")
    
    return issues

def run_comprehensive_audit():
    """Run comprehensive system audit"""
    print_header("BloodLink Comprehensive System Error Audit")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_issues = []
    
    # Run all checks
    checks = [
        ('Dependencies', check_dependencies),
        ('Settings', check_settings),
        ('Imports', check_imports),
        ('Models', check_models),
        ('Views', check_views),
        ('URLs', check_urls),
        ('Database', check_database),
        ('Static Files', check_static_files),
        ('Templates', check_templates),
    ]
    
    for check_name, check_func in checks:
        try:
            issues = check_func()
            all_issues.extend(issues)
        except Exception as e:
            print(f"❌ {check_name} check failed: {str(e)}")
            all_issues.append(f"{check_name} check failed: {str(e)}")
    
    # Summary
    print_header("Audit Summary")
    
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✅ No issues found! System is healthy.")
    
    # Recommendations
    print("\n📋 Recommendations:")
    if all_issues:
        print("1. Fix all identified issues before deployment")
        print("2. Test the system thoroughly after fixes")
        print("3. Monitor system after deployment")
    else:
        print("1. System is ready for deployment")
        print("2. Continue monitoring for new issues")
        print("3. Regular system audits recommended")
    
    print(f"\nAudit completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_issues

if __name__ == '__main__':
    issues = run_comprehensive_audit()
    sys.exit(1 if issues else 0)
