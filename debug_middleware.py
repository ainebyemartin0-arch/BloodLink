#!/usr/bin/env python
"""
Debug middleware issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.middleware.common import CommonMiddleware
from staff_portal.views import blood_stock

def debug_middleware():
    """Debug what CommonMiddleware is doing"""
    print("🔍 Debugging CommonMiddleware")
    print("=" * 50)
    
    User = get_user_model()
    staff_user = User.objects.filter(is_staff=True).first()
    
    if not staff_user:
        print("❌ No staff user found")
        return
    
    print(f"✅ Using staff user: {staff_user.username}")
    
    # Create request
    factory = RequestFactory()
    request = factory.get('/staff/blood-stock/')
    request.user = staff_user
    
    print(f"\n📋 Original request:")
    print(f"   Path: {request.path}")
    print(f"   Method: {request.method}")
    print(f"   META: {dict(list(request.META.items())[:5])}")  # First 5 items
    
    # Apply CommonMiddleware
    middleware = CommonMiddleware(lambda req: blood_stock(req))
    
    try:
        print(f"\n🔄 Applying CommonMiddleware...")
        response = middleware(request)
        print(f"✅ Middleware processed successfully")
        print(f"   Response status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Middleware failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_middleware()
