from .models import ActivityLog, EmergencyRequest, BloodStock, DonationRecord
from django.utils import timezone
from django.db import models
from notifications.models import SMSNotification

def log_activity(request, action, description, 
                 donor_id=None, request_id=None):
    """
    Helper function to log staff activities.
    Call this after important actions in views.
    """
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        ActivityLog.objects.create(
            staff_user=request.user if request.user.is_authenticated else None,
            action=action,
            description=description,
            ip_address=ip,
            related_donor_id=donor_id,
            related_request_id=request_id,
        )
    except Exception:
        pass  # Never let logging crash the main action

def check_request_fulfillment(emergency_request):
    """
    Check if an emergency request is fulfilled and update automatically.
    This function is called when a donation is recorded.
    """
    try:
        # Get all donations for this request
        total_donated = DonationRecord.objects.filter(
            emergency_request=emergency_request
        ).aggregate(
            total=models.Sum('units_donated')
        )['total'] or 0
        
        # Update the fulfilled units
        emergency_request.units_fulfilled = total_donated
        
        # Check if request is fully fulfilled
        if total_donated >= emergency_request.units_needed:
            emergency_request.status = 'fulfilled'
            emergency_request.fulfilled_at = timezone.now()
            
            # Update blood stock automatically
            update_blood_stock_from_donation(emergency_request.blood_type_needed, total_donated)
            
            # Mark related SMS notifications as fulfilled
            SMSNotification.objects.filter(
                emergency_request=emergency_request
            ).update(
                is_fulfilled=True,
                fulfilled_at=timezone.now()
            )
        
        emergency_request.save()
        return True
        
    except Exception as e:
        print(f"Error checking request fulfillment: {e}")
        return False

def update_blood_stock_from_donation(blood_type, units_donated):
    """
    Automatically update blood stock when a donation is fulfilled.
    This function increases the blood stock when donations are recorded.
    """
    try:
        # Get or create blood stock record
        stock, created = BloodStock.objects.get_or_create(
            blood_type=blood_type,
            defaults={
                'current_units': 0,
                'optimal_level': 50,
                'minimum_level': 10,
                'critical_level': 5,
            }
        )
        
        # Add donated units to stock
        stock.current_units += units_donated
        stock.last_updated = timezone.now()
        stock.save()
        
        return True
        
    except Exception as e:
        print(f"Error updating blood stock: {e}")
        return False

def auto_fulfill_request_from_donor_response(emergency_request, donor, units_donated=1):
    """
    Automatically fulfill a request when a donor responds positively.
    This creates a donation record and updates everything automatically.
    """
    try:
        # Create donation record
        donation = DonationRecord.objects.create(
            donor=donor,
            emergency_request=emergency_request,
            units_donated=units_donated,
            donation_date=timezone.now().date(),
            donation_time=timezone.now(),
            recorded_by=None,  # System recorded
            status='completed'
        )
        
        # Update donor's donation history
        donor.record_donation(units_donated)
        
        # Check if request is fulfilled
        check_request_fulfillment(emergency_request)
        
        return donation
        
    except Exception as e:
        print(f"Error auto-fulfilling request: {e}")
        return None
