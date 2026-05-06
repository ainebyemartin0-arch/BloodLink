#!/usr/bin/env python
"""
Simple test for blood stock page
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

def test_simple():
    """Simple test of blood stock view"""
    print("🧪 Simple Blood Stock Test")
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
        print("\n🔍 Testing blood_stock view...")
        response = blood_stock(request)
        print(f"✅ View executed successfully")
        print(f"   Status: {response.status_code}")
        print(f"   Content type: {response.get('Content-Type')}")
        
        # Check if template has any syntax errors
        content = response.content.decode('utf-8')
        if 'Bad Request' in content:
            print("❌ Template contains Bad Request")
        elif 'TemplateSyntaxError' in content:
            print("❌ Template syntax error")
        else:
            print("✅ Template rendered successfully")
            
        # Check for any remaining stock. references
        if 'stock.' in content and not 'item.stock.' in content:
            print("⚠️  Found unconverted stock. references")
        else:
            print("✅ All stock references converted")
            
    except Exception as e:
        print(f"❌ View execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple()
