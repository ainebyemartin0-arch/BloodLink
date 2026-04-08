from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from staff_portal.models import BloodShortageAlert, EmergencyRequest
from donors.models import Donor
from notifications.models import SMSNotification
import math

class Command(BaseCommand):
    help = 'Check for blood shortages and create automatic alerts'

    def handle(self, *args, **options):
        self.stdout.write('Checking for blood shortages...')
        
        # Define blood types
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for blood_type in blood_types:
            self.check_blood_type_shortage(blood_type)
        
        self.stdout.write(self.style.SUCCESS('Blood shortage check completed'))

    def check_blood_type_shortage(self, blood_type):
        """Check for shortage of a specific blood type"""
        
        # Get current statistics
        total_donors = Donor.objects.filter(blood_type=blood_type, is_active=True).count()
        available_donors = Donor.objects.filter(blood_type=blood_type, is_available=True, is_active=True).count()
        open_requests = EmergencyRequest.objects.filter(blood_type_needed=blood_type, status='open').count()
        
        # Calculate shortage metrics
        if total_donors == 0:
            shortage_percentage = 100.0
        else:
            availability_rate = (available_donors / total_donors) * 100
            shortage_percentage = 100 - availability_rate
        
        # Determine alert level
        alert_level = self.determine_alert_level(available_donors, open_requests, shortage_percentage)
        
        # Check if alert already exists and is active
        existing_alert = BloodShortageAlert.objects.filter(
            blood_type=blood_type,
            is_active=True
        ).first()
        
        # Create or update alert if needed
        if alert_level != 'normal' and (not existing_alert or existing_alert.alert_level != alert_level):
            message = self.generate_alert_message(blood_type, alert_level, available_donors, open_requests, shortage_percentage)
            
            if existing_alert:
                # Update existing alert
                existing_alert.alert_level = alert_level
                existing_alert.available_donors = available_donors
                existing_alert.total_requests = open_requests
                existing_alert.shortage_percentage = shortage_percentage
                existing_alert.message = message
                existing_alert.save()
                self.stdout.write(f'Updated {blood_type} alert: {alert_level}')
            else:
                # Create new alert
                BloodShortageAlert.objects.create(
                    blood_type=blood_type,
                    alert_level=alert_level,
                    available_donors=available_donors,
                    total_requests=open_requests,
                    shortage_percentage=shortage_percentage,
                    message=message
                )
                self.stdout.write(f'Created {blood_type} alert: {alert_level}')
                
                # Send immediate notification to staff
                self.send_staff_notification(blood_type, alert_level, message)
        
        # Resolve alert if condition improved
        elif alert_level == 'normal' and existing_alert:
            existing_alert.is_active = False
            existing_alert.resolved_at = timezone.now()
            existing_alert.save()
            self.stdout.write(f'Resolved {blood_type} alert')

    def determine_alert_level(self, available_donors, open_requests, shortage_percentage):
        """Determine the alert level based on current conditions"""
        
        # Emergency shortage: No available donors OR high demand with no supply
        if available_donors == 0 or (open_requests >= 5 and available_donors <= 2):
            return 'emergency'
        
        # Critical shortage: Very low availability OR high demand
        elif available_donors <= 3 or (open_requests >= 3 and available_donors <= 5):
            return 'critical'
        
        # Low stock: Moderate availability issues
        elif available_donors <= 10 or shortage_percentage >= 70:
            return 'low'
        
        # Normal: Adequate availability
        else:
            return 'normal'

    def generate_alert_message(self, blood_type, alert_level, available_donors, open_requests, shortage_percentage):
        """Generate alert message based on conditions"""
        
        if alert_level == 'emergency':
            return f"🚨 EMERGENCY: {blood_type} blood critically low! Only {available_donors} donors available with {open_requests} pending requests. Immediate action required!"
        
        elif alert_level == 'critical':
            return f"⚠️ CRITICAL: {blood_type} blood shortage detected! Only {available_donors} donors available for {open_requests} requests. Urgent attention needed!"
        
        elif alert_level == 'low':
            return f"📊 LOW STOCK: {blood_type} blood running low. {available_donors} donors available ({shortage_percentage:.1f}% shortage). Monitor closely."
        
        return ""

    def send_staff_notification(self, blood_type, alert_level, message):
        """Send immediate notification to all staff users"""
        
        try:
            # Get all active staff users
            staff_users = User.objects.filter(is_staff=True, is_active=True)
            
            for staff in staff_users:
                # Create SMS notification for staff
                SMSNotification.objects.create(
                    donor=None,  # This is a system notification
                    phone_number=staff.profile.phone if hasattr(staff, 'profile') else '',
                    message=f"BloodLink Alert: {message}",
                    delivery_status='sent',
                    donor_response='no_response',
                    emergency_request=None
                )
            
            self.stdout.write(f'Sent staff notifications for {blood_type} {alert_level} alert')
            
        except Exception as e:
            self.stdout.write(f'Error sending staff notifications: {str(e)}')
