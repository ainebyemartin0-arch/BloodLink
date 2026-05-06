#!/usr/bin/env python
"""
Direct test of blood stock view without middleware
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from django.http import HttpRequest
from django.contrib.auth import get_user_model
from staff_portal.views import blood_stock

def test_direct():
    """Test view directly without middleware"""
    print("🎯 Direct View Test (No Middleware)")
    print("=" * 50)
    
    User = get_user_model()
    staff_user = User.objects.filter(is_staff=True).first()
    
    if not staff_user:
        print("❌ No staff user found")
        return
    
    print(f"✅ Using staff user: {staff_user.username}")
    
    # Create request manually
    request = HttpRequest()
    request.method = 'GET'
    request.path = '/staff/blood-stock/'
    request.user = staff_user
    
    # Add required attributes
    request.META = {
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8000',
        'HTTP_HOST': '127.0.0.1:8000',
    }
    
    try:
        print("\n🔍 Testing blood_stock view directly...")
        response = blood_stock(request)
        print(f"✅ View executed successfully")
        print(f"   Status: {response.status_code}")
        print(f"   Content type: {response.get('Content-Type')}")
        
        # Check content
        content = response.content.decode('utf-8')
        if 'Bad Request' in content:
            print("❌ Contains Bad Request error")
        elif 'Error' in content:
            print("❌ Contains other error")
        else:
            print("✅ Content looks good")
            print(f"   Content length: {len(content)} characters")
            
    except Exception as e:
        print(f"❌ View execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_direct()
