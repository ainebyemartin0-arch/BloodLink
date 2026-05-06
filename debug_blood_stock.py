#!/usr/bin/env python
"""
Debug script for blood stock page issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from staff_portal.views import blood_stock
from staff_portal.models import BloodStock

def debug_blood_stock():
    """Debug the blood stock view"""
    print("🔍 Debugging Blood Stock View")
    print("=" * 50)
    
    # Create request factory
    factory = RequestFactory()
    
    # Get staff user
    User = get_user_model()
    staff_user = User.objects.filter(is_staff=True).first()
    
    if not staff_user:
        print("❌ No staff user found")
        return
    
    print(f"✅ Using staff user: {staff_user.username}")
    
    # Create request
    request = factory.get('/staff/blood-stock/')
    request.user = staff_user
    
    try:
        # Test the view
        print("\n🧪 Testing blood_stock view...")
        response = blood_stock(request)
        print(f"✅ View executed successfully")
        print(f"   Status: {response.status_code}")
        print(f"   Content type: {response.get('Content-Type')}")
        
        # Check context data
        if hasattr(response, 'context_data'):
            context = response.context_data
            print(f"\n📊 Context Data:")
            print(f"   blood_stocks count: {len(context.get('blood_stocks', []))}")
            print(f"   total_units: {context.get('total_units', 'N/A')}")
            print(f"   critical_count: {context.get('critical_count', 'N/A')}")
            print(f"   empty_types: {context.get('empty_types', 'N/A')}")
            
            # Check blood stocks data
            blood_stocks = context.get('blood_stocks', [])
            if blood_stocks:
                print(f"\n🩸 Blood Stock Data:")
                for stock in blood_stocks:
                    print(f"   {stock.blood_type}: {stock.current_units} units")
        
        # Test template rendering
        print(f"\n🎨 Testing template rendering...")
        content = response.content.decode('utf-8')
        if 'Bad Request' in content:
            print("❌ Template rendering failed - Bad Request")
            # Look for template errors
            if 'TemplateDoesNotExist' in content:
                print("   Error: Template does not exist")
            elif 'TemplateSyntaxError' in content:
                print("   Error: Template syntax error")
            else:
                print("   Error: Unknown template error")
        else:
            print("✅ Template rendering successful")
            print(f"   Content length: {len(content)} characters")
            
    except Exception as e:
        print(f"❌ View execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

def check_blood_stock_data():
    """Check blood stock data integrity"""
    print("\n🩸 Checking Blood Stock Data")
    print("=" * 50)
    
    try:
        stocks = BloodStock.objects.all()
        print(f"✅ Found {stocks.count()} blood stock records")
        
        for stock in stocks:
            print(f"   {stock.blood_type}: {stock.current_units} units (critical: {stock.critical_level})")
            
        # Check for data issues
        issues = []
        for stock in stocks:
            if stock.current_units < 0:
                issues.append(f"Negative units for {stock.blood_type}")
            if stock.critical_level > stock.minimum_level:
                issues.append(f"Critical level > minimum level for {stock.blood_type}")
        
        if issues:
            print(f"\n❌ Data issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print(f"\n✅ No data issues found")
            
    except Exception as e:
        print(f"❌ Data check failed: {str(e)}")

if __name__ == '__main__':
    check_blood_stock_data()
    debug_blood_stock()
