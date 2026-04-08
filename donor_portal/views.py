from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import models
from donors.models import Donor, BLOOD_TYPE_CHOICES
from .forms import DonorRegistrationForm, DonorLoginForm, DonorProfileEditForm, DonorChangePasswordForm
from notifications.models import SMSNotification
from staff_portal.models import DonationRecord
from functools import wraps

def get_logged_in_donor(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return None
    try:
        return Donor.objects.get(pk=donor_id, is_active=True)
    except Donor.DoesNotExist:
        return None

def donor_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        donor = get_logged_in_donor(request)
        if not donor:
            messages.error(request, 'Please login to access your donor account.')
            return redirect('donor:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def donor_home(request):
    total_donors = Donor.objects.filter(is_active=True).count()
    available_donors = Donor.objects.filter(is_active=True, is_available=True).count()
    
    context = {
        'total_donors': total_donors,
        'available_donors': available_donors,
        'blood_types': BLOOD_TYPE_CHOICES,
    }
    return render(request, 'donor_portal/home.html', context)

def about_bloodlink(request):
    """About BloodLink page with detailed information"""
    return render(request, 'donor_portal/about.html')

def donor_register(request):
    if get_logged_in_donor(request):
        return redirect('donor:dashboard')
    
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            # Create donor
            donor = Donor.objects.create(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                gender=form.cleaned_data['gender'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                blood_type=form.cleaned_data['blood_type'],
                location=form.cleaned_data['location'],
                physical_address=form.cleaned_data['physical_address'],
                is_available=True,
                is_active=True,
                date_registered=timezone.now()
            )
            donor.set_password(form.cleaned_data['password1'])
            donor.save()
            
            # Log in the donor
            request.session['donor_id'] = donor.pk
            messages.success(request, f"Welcome {donor.full_name}! Your donor account has been created successfully.")
            return redirect('donor:dashboard')
    else:
        form = DonorRegistrationForm()
    
    return render(request, 'donor_portal/register.html', {'form': form})

def donor_login(request):
    if get_logged_in_donor(request):
        return redirect('donor:dashboard')
    
    if request.method == 'POST':
        form = DonorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                donor = Donor.objects.get(email=email, is_active=True)
                if donor.check_password(password):
                    request.session['donor_id'] = donor.pk
                    messages.success(request, f"Welcome back, {donor.full_name}!")
                    return redirect('donor:dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
            except Donor.DoesNotExist:
                messages.error(request, "Invalid email or password.")
    else:
        form = DonorLoginForm()
    
    return render(request, 'donor_portal/login.html', {'form': form})

def donor_logout(request):
    donor_id = request.session.pop('donor_id', None)
    if donor_id:
        messages.success(request, "You have been logged out safely.")
    return redirect('donor:login')

@donor_login_required
def donor_dashboard(request):
    donor = get_logged_in_donor(request)
    
    # Get SMS alerts with more detail (exclude fulfilled notifications)
    sms_alerts = donor.sms_notifications.select_related('emergency_request').filter(is_fulfilled=False).order_by('-sent_at')[:5]
    total_alerts = donor.sms_notifications.count()
    confirmed_count = donor.sms_notifications.filter(donor_response='confirmed').count()
    declined_count = donor.sms_notifications.filter(donor_response='declined').count()
    pending_response = donor.sms_notifications.filter(donor_response='no_response').count()
    donation_count = donor.donation_records.count()
    recent_donations = donor.donation_records.order_by('-donation_date')[:3]
    
    # Check for unread alerts (no response and not fulfilled) and mark as viewed
    unread_alerts = donor.sms_notifications.filter(donor_response='no_response', is_fulfilled=False).order_by('-sent_at')
    
    # Mark alerts as viewed when donor accesses dashboard
    from django.utils import timezone
    donor.sms_notifications.filter(last_viewed_at__isnull=True).update(
        last_viewed_at=timezone.now(),
        view_count=models.F('view_count') + 1
    )
    
    context = {
        'donor': donor,
        'sms_alerts': sms_alerts,
        'total_alerts': total_alerts,
        'confirmed_count': confirmed_count,
        'declined_count': declined_count,
        'pending_response': pending_response,
        'donation_count': donation_count,
        'recent_donations': recent_donations,
        'unread_alerts': unread_alerts,
    }
    return render(request, 'donor_portal/dashboard.html', context)

@donor_login_required
def donor_profile(request):
    donor = get_logged_in_donor(request)
    return render(request, 'donor_portal/profile.html', {'donor': donor})

@donor_login_required
def donor_profile_edit(request):
    donor = get_logged_in_donor(request)
    
    if request.method == 'POST':
        form = DonorProfileEditForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('donor:profile')
    else:
        form = DonorProfileEditForm(instance=donor)
    
    return render(request, 'donor_portal/profile_edit.html', {'form': form})

@donor_login_required
def donor_donations(request):
    donor = get_logged_in_donor(request)
    
    all_donations = donor.donation_records.order_by('-donation_date')
    all_alerts = donor.sms_notifications.order_by('-sent_at')
    
    context = {
        'donor': donor,
        'all_donations': all_donations,
        'all_alerts': all_alerts,
    }
    return render(request, 'donor_portal/donations.html', context)

@donor_login_required
def donor_change_password(request):
    donor = get_logged_in_donor(request)
    
    if request.method == 'POST':
        form = DonorChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password1 = form.cleaned_data['new_password1']
            
            if donor.check_password(current_password):
                donor.set_password(new_password1)
                donor.save()
                messages.success(request, "Password changed successfully.")
                return redirect('donor:profile')
            else:
                messages.error(request, "Current password is incorrect.")
    else:
        form = DonorChangePasswordForm()
    
    return render(request, 'donor_portal/change_password.html', {'form': form})

@donor_login_required
def respond_to_alert(request, pk):
    """Allow donor to respond to SMS alert"""
    donor = get_logged_in_donor(request)
    notification = get_object_or_404(SMSNotification, pk=pk, donor=donor)
    
    # Mark as opened when donor views the alert
    if notification.opened_at is None:
        notification.opened_at = timezone.now()
    
    if request.method == 'POST':
        response = request.POST.get('response')
        if response in ['confirmed', 'declined']:
            # Store original message status before updating
            original_message_status = notification.message_status
            
            # Update donor response
            notification.donor_response = response
            
            # Update message status based on donor response
            if response == 'confirmed':
                notification.message_status = 'confirmed'
                # Update delivery status based on original message status
                if original_message_status in ['delivered', 'success']:
                    notification.delivery_status = 'delivered'
                    if notification.delivered_at is None:
                        notification.delivered_at = timezone.now()
                elif original_message_status in ['sent', 'submitted']:
                    notification.delivery_status = 'sent'
                else:
                    # If message wasn't successfully delivered, still mark as sent since donor responded
                    notification.delivery_status = 'sent'
                
                # Mark the notification as "fulfilled" so it disappears from donor's active list
                notification.is_fulfilled = True
                notification.fulfilled_at = timezone.now()
                
                messages.success(request, "Thank you for confirming! The hospital will contact you soon.")
            else:
                notification.message_status = 'declined'
                # For declined responses, still mark as delivered if it was delivered
                if original_message_status in ['delivered', 'success']:
                    notification.delivery_status = 'delivered'
                    if notification.delivered_at is None:
                        notification.delivered_at = timezone.now()
                elif original_message_status in ['sent', 'submitted']:
                    notification.delivery_status = 'sent'
                else:
                    # If message wasn't successfully delivered, still mark as sent since donor responded
                    notification.delivery_status = 'sent'
                
                # Mark as fulfilled so it disappears from donor's active list
                notification.is_fulfilled = True
                notification.fulfilled_at = timezone.now()
                
                messages.info(request, "Thank you for your response. We understand you're not available at this time.")
            
            # Update last viewed and view count
            notification.last_viewed_at = timezone.now()
            notification.view_count += 1
            
            # Save all updates
            notification.save()
                
        return redirect('donor:dashboard')
    
    return redirect('donor:dashboard')

@donor_login_required
def mark_sms_opened(request, pk):
    """Mark SMS as opened when donor views details"""
    donor = get_logged_in_donor(request)
    notification = get_object_or_404(SMSNotification, pk=pk, donor=donor)
    
    if notification.opened_at is None:
        notification.opened_at = timezone.now()
        
        # Update delivery status if message was successfully sent
        if notification.message_status in ['delivered', 'success']:
            notification.delivery_status = 'delivered'
            notification.delivered_at = timezone.now()
        elif notification.message_status in ['sent', 'submitted']:
            notification.delivery_status = 'sent'
        
        # Update view tracking
        notification.last_viewed_at = timezone.now()
        notification.view_count += 1
        notification.save()
    
    return redirect('donor:donations')
