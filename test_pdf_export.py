#!/usr/bin/env python
"""
Test script to verify PDF export functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

def test_pdf_export():
    """Test the PDF export functionality"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from io import BytesIO
        from datetime import datetime
        
        # Create a simple PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        story.append(Paragraph("BloodLink Test Report", styles['Title']))
        story.append(Paragraph(f"Generated on: {datetime.now()}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF value
        pdf_value = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF export test successful! Generated {len(pdf_value)} bytes")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

def test_database_data():
    """Test database data access"""
    try:
        from staff_portal.models import BloodStock, EmergencyRequest, DonationRecord
        from donors.models import Donor
        from notifications.models import SMSNotification
        
        # Test data access
        donor_count = Donor.objects.count()
        request_count = EmergencyRequest.objects.count()
        stock_count = BloodStock.objects.count()
        sms_count = SMSNotification.objects.count()
        
        print(f"✅ Database access successful:")
        print(f"   Donors: {donor_count}")
        print(f"   Requests: {request_count}")
        print(f"   Stock: {stock_count}")
        print(f"   SMS: {sms_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing PDF Export Functionality")
    print("=" * 40)
    
    # Test database access
    print("\n1. Testing database access...")
    db_ok = test_database_data()
    
    # Test PDF generation
    print("\n2. Testing PDF generation...")
    pdf_ok = test_pdf_export()
    
    # Summary
    print("\n" + "=" * 40)
    if db_ok and pdf_ok:
        print("✅ All tests passed! PDF export should work.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("\nTo test the PDF export in your browser:")
    print("1. Start the server: python manage.py runserver")
    print("2. Login as staff")
    print("3. Go to: http://127.0.0.1:8000/staff/reports/")
    print("4. Click 'Download PDF'")
