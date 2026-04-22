from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, F
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from functools import wraps

from donors.models import Donor
from donors.choices import BLOOD_TYPE_CHOICES
from notifications.models import SMSNotification
from staff_portal.models import EmergencyRequest, PublicBloodRequest, DonationRecord
from .forms import (
    DonorRegistrationForm, DonorLoginForm, DonorProfileEditForm, DonorChangePasswordForm, PublicBloodRequestForm,
    GoogleLoginForm, PhoneLoginForm, PhoneRegistrationForm, GoogleRegistrationForm
)

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
    return render(request, 'donor_portal/home_enhanced.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Here you would typically send an email
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('donor:contact')
    
    return render(request, 'donor_portal/contact.html')

def about_bloodlink(request):
    """About BloodLink page with detailed information"""
    return render(request, 'donor_portal/about.html')

def donor_register(request):
    if get_logged_in_donor(request):
        return redirect('donor:dashboard')
    
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            donor = Donor(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                gender=form.cleaned_data['gender'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                blood_type=form.cleaned_data['blood_type'],
                location=form.cleaned_data['location'],
                physical_address=form.cleaned_data['physical_address'],
                profile_picture=form.cleaned_data.get('profile_picture'),
                is_available=True,
                is_active=True,
                date_registered=timezone.now()
            )
            donor.set_password(form.cleaned_data['password1'])
            donor.save()
            
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
                    # Clear any existing session data
                    request.session.flush()
                    
                    # Set new session
                    request.session['donor_id'] = donor.pk
                    request.session['last_activity'] = timezone.now().isoformat()
                    
                    # Set session timeout (30 days if remember me is checked)
                    remember_me = request.POST.get('remember', False)
                    if remember_me:
                        request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
                    else:
                        request.session.set_expiry(24 * 60 * 60)  # 24 hours
                    
                    messages.success(request, f"Welcome back, {donor.full_name}!")
                    return redirect('donor:dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
            except Donor.DoesNotExist:
                messages.error(request, "Invalid email or password.")
        else:
            # Form validation errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = DonorLoginForm()
    
    return render(request, 'donor_portal/login_enhanced.html', {'form': form})

def donor_logout(request):
    donor_id = request.session.pop('donor_id', None)
    if donor_id:
        messages.success(request, "You have been logged out safely.")
    return redirect('donor:login')


# ===== GOOGLE AND PHONE AUTHENTICATION VIEWS =====

def google_login(request):
    """Handle Google OAuth login."""
    if get_logged_in_donor(request):
        return redirect('donor:dashboard')
    
    if request.method == 'POST':
        form = GoogleLoginForm(request.POST)
        if form.is_valid():
            google_id = form.cleaned_data['google_id']
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            picture_url = form.cleaned_data.get('picture_url')
            
            # Try to find existing donor by Google ID
            donor = Donor.get_by_google_id(google_id)
            
            if donor:
                # Existing Google user - login
                request.session['donor_id'] = donor.pk
                messages.success(request, f"Welcome back, {donor.full_name}!")
                return JsonResponse({'success': True, 'redirect': reverse('donor:dashboard')})
            else:
                # Check if donor exists with this email
                try:
                    donor = Donor.objects.get(email=email, is_active=True)
                    # Link Google account to existing donor
                    donor.authenticate_with_google(google_id, email, name, picture_url)
                    request.session['donor_id'] = donor.pk
                    messages.success(request, f"Google account linked successfully! Welcome back, {donor.full_name}!")
                    return JsonResponse({'success': True, 'redirect': reverse('donor:dashboard')})
                except Donor.DoesNotExist:
                    # New user - need to complete registration
                    request.session['google_data'] = {
                        'google_id': google_id,
                        'email': email,
                        'name': name,
                        'picture_url': picture_url
                    }
                    return JsonResponse({
                        'success': True, 
                        'redirect': reverse('donor:google_register'),
                        'message': 'Please complete your registration'
                    })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid Google data'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def google_register(request):
    """Complete registration for Google users."""
    if get_logged_in_donor(request):
        return redirect('donor:dashboard')
    
    google_data = request.session.get('google_data')
    if not google_data:
        messages.error(request, 'Google session expired. Please try again.')
        return redirect('donor:login')
    
    if request.method == 'POST':
        form = GoogleRegistrationForm(request.POST)
        if form.is_valid():
            # Create new donor with Google data
            donor = Donor(
                full_name=google_data['name'],
                email=google_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                gender=form.cleaned_data['gender'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                blood_type=form.cleaned_data['blood_type'],
                location=form.cleaned_data['location'],
                physical_address=form.cleaned_data['physical_address'],
                google_id=google_data['google_id'],
                google_profile_picture=google_data.get('picture_url'),
                auth_method='google',
                is_available=True,
                is_active=True,
                date_registered=timezone.now()
            )
            donor.save()
            
            # Clear session data
            request.session.pop('google_data', None)
            request.session['donor_id'] = donor.pk
            
            messages.success(request, f"Welcome {donor.full_name}! Your Google account has been registered successfully.")
            return redirect('donor:dashboard')
    else:
        # Pre-fill form with available data
        initial_data = {
            'google_id': google_data['google_id'],
            'email': google_data['email'],
            'name': google_data['name'],
            'picture_url': google_data.get('picture_url')
        }
        form = GoogleRegistrationForm(initial=initial_data)
    
    return render(request, 'donor_portal/google_register.html', {
        'form': form,
        'google_data': google_data
    })


def phone_login(request):
    """Handle phone number login."""
    if get_logged_in_donor(request):
        return redirect('donor:dashboard')
    
    if request.method == 'POST':
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            verification_code = form.cleaned_data.get('verification_code')
            
            donor = Donor.get_by_phone_number(phone_number)
            
            if not donor:
                return JsonResponse({'success': False, 'message': 'Phone number not registered'})
            
            if verification_code:
                # Verify code and login
                if verification_code == request.session.get('phone_verification_code'):
                    # Mark phone as verified
                    donor.phone_verified = True
                    donor.save()
                    
                    # Clear verification code
                    request.session.pop('phone_verification_code', None)
                    
                    # Login
                    request.session['donor_id'] = donor.pk
                    messages.success(request, f"Welcome back, {donor.full_name}!")
                    return JsonResponse({'success': True, 'redirect': reverse('donor:dashboard')})
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid verification code'})
            else:
                # Send verification code
                if donor.phone_verified:
                    # Already verified - login directly
                    request.session['donor_id'] = donor.pk
                    messages.success(request, f"Welcome back, {donor.full_name}!")
                    return JsonResponse({'success': True, 'redirect': reverse('donor:dashboard')})
                else:
                    # Generate and send verification code
                    form_instance = PhoneRegistrationForm()
                    code = form_instance.generate_verification_code()
                    request.session['phone_verification_code'] = code
                    request.session['phone_verification_phone'] = phone_number
                    
                    # TODO: Send SMS with verification code
                    # For now, just return the code for testing
                    return JsonResponse({
                        'success': True, 
                        'message': f'Verification code sent to {phone_number}',
                        'code': code  # Remove this in production
                    })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid phone number'})
    
    form = PhoneLoginForm()
    return render(request, 'donor_portal/phone_login.html', {'form': form})


def phone_register(request):
    """Handle phone number registration."""
    if get_logged_in_donor(request):
        return redirect('donor:dashboard')
    
    if request.method == 'POST':
        form = PhoneRegistrationForm(request.POST)
        if form.is_valid():
            # Create new donor
            donor = Donor(
                full_name=form.cleaned_data['full_name'],
                phone_number=form.cleaned_data['phone_number'],
                gender=form.cleaned_data['gender'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                blood_type=form.cleaned_data['blood_type'],
                location=form.cleaned_data['location'],
                physical_address=form.cleaned_data['physical_address'],
                auth_method='phone',
                phone_verified=False,  # Will be verified during login
                is_available=True,
                is_active=True,
                date_registered=timezone.now()
            )
            donor.save()
            
            messages.success(request, f"Registration successful! You can now login with your phone number.")
            return redirect('donor:phone_login')
    else:
        form = PhoneRegistrationForm()
    
    return render(request, 'donor_portal/phone_register.html', {'form': form})


# ===== ADDITIONAL REQUIRED VIEWS =====

def donor_dashboard(request):
    """Donor dashboard view."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    context = {
        'donor': donor,
    }
    return render(request, 'donor_portal/dashboard.html', context)

def donor_profile(request):
    """Donor profile view."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    context = {
        'donor': donor,
    }
    return render(request, 'donor_portal/profile.html', context)

def donor_profile_edit(request):
    """Donor profile edit view."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    if request.method == 'POST':
        form = DonorProfileEditForm(request.POST, request.FILES, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('donor:profile')
    else:
        form = DonorProfileEditForm(instance=donor)
    
    return render(request, 'donor_portal/profile_edit.html', {'form': form})

def donor_donations(request):
    """Donor donations view."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    # Get donor's donation records
    donations = DonationRecord.objects.filter(donor=donor).order_by('-donation_date')
    
    context = {
        'donor': donor,
        'donations': donations,
    }
    return render(request, 'donor_portal/donations.html', context)

@donor_login_required
def donor_requests(request):
    """Donor requests view."""
    donor = get_logged_in_donor(request)
    
    # Get EmergencyRequest objects from staff (open/fulfilled requests)
    emergency_requests = EmergencyRequest.objects.filter(
        blood_type_needed=donor.blood_type,
        status__in=['open', 'fulfilled']  # Show open and partially fulfilled requests
    ).order_by('-created_at')
    
    # Get PublicBloodRequest objects (patient/family requests)
    public_requests = PublicBloodRequest.objects.filter(
        blood_type_needed=donor.blood_type,
        status='pending'
    ).order_by('-submitted_at')
    
    # Combine all requests and sort by creation time
    all_requests = []
    
    # Add emergency requests with type marker
    for req in emergency_requests:
        req.request_type = 'emergency'
        req.is_staff_created = True
        req.display_name = f"Emergency Request - {req.patient_name or 'Unnamed Patient'}"
        req.display_urgency = req.urgency_level
        all_requests.append(req)
    
    # Add public requests with type marker
    for req in public_requests:
        req.request_type = 'public'
        req.is_staff_created = False
        req.display_name = f"Blood Request - {req.patient_name}"
        req.display_urgency = req.urgency_level
        all_requests.append(req)
    
    # Sort all requests by creation time (newest first)
    all_requests.sort(key=lambda x: x.created_at if hasattr(x, 'created_at') else x.submitted_at, reverse=True)
    
    # Calculate statistics
    pending_requests = len(all_requests)
    confirmed_requests = 0  # This would be for requests donor has confirmed
    completed_requests = 0  # This would be for completed donations
    total_requests = pending_requests + confirmed_requests + completed_requests
    
    context = {
        'donor': donor,
        'requests': all_requests,
        'pending_requests': pending_requests,
        'confirmed_requests': confirmed_requests,
        'completed_requests': completed_requests,
        'total_requests': total_requests,
        'pending_count': pending_requests,  # For header stats
    }
    return render(request, 'donor_portal/donor_requests_organized.html', context)

def toggle_availability(request):
    """Toggle donor availability."""
    donor = get_logged_in_donor(request)
    if not donor:
        return JsonResponse({'success': False, 'error': 'Not logged in'})
    
    if request.method == 'POST':
        is_available = request.POST.get('available') == 'true'
        donor.is_available = is_available
        donor.save()
        
        return JsonResponse({
            'success': True,
            'available': is_available,
            'message': f'You are now {"available" if is_available else "unavailable"} for donations.'
        })
        
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

def cancel_request(request, pk):
    """Cancel a blood request."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    blood_request = get_object_or_404(PublicBloodRequest, pk=pk)
    
    if blood_request.status != 'pending':
        messages.error(request, 'This request cannot be cancelled.')
        return redirect('donor:requests')
    
    blood_request.status = 'cancelled'
    blood_request.save()
    
    messages.success(request, 'Request cancelled successfully.')
    return redirect('donor:requests')

def donor_change_password(request):
    """Donor change password view."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    if request.method == 'POST':
        form = DonorChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password1']
            
            if donor.check_password(old_password):
                donor.set_password(new_password)
                donor.save()
                messages.success(request, 'Password changed successfully!')
                return redirect('donor:profile')
            else:
                messages.error(request, 'Current password is incorrect.')
    else:
        form = DonorChangePasswordForm()
    
    return render(request, 'donor_portal/change_password.html', {'form': form})

def respond_to_alert(request, pk):
    """Respond to blood donation alert."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    blood_request = get_object_or_404(PublicBloodRequest, pk=pk)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        
        if response == 'accept':
            blood_request.status = 'accepted'
            blood_request.accepted_by = donor
            blood_request.accepted_at = timezone.now()
        elif response == 'decline':
            blood_request.status = 'declined'
            blood_request.declined_by = donor
            blood_request.declined_at = timezone.now()
        
        blood_request.save()
        
        messages.success(request, f'You have {response}ed the blood donation request.')
        return redirect('donor:response_confirmation', pk=pk)
    
    context = {
        'donor': donor,
        'blood_request': blood_request,
    }
    return render(request, 'donor_portal/respond.html', context)

def response_confirmation(request, pk):
    """Response confirmation page."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    blood_request = get_object_or_404(PublicBloodRequest, pk=pk)
    
    context = {
        'donor': donor,
        'blood_request': blood_request,
    }
    return render(request, 'donor_portal/response_confirmation.html', context)

def mark_sms_opened(request, pk):
    """Mark SMS as opened (for tracking)."""
    try:
        sms = SMSNotification.objects.get(pk=pk)
        sms.is_opened = True
        sms.opened_at = timezone.now()
        sms.save()
        return JsonResponse({'success': True})
    except SMSNotification.DoesNotExist:
        return JsonResponse({'success': False})

def request_blood(request):
    """Request blood form."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    if request.method == 'POST':
        form = PublicBloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requested_by = donor
            blood_request.save()
            
            messages.success(request, 'Blood request submitted successfully!')
            return redirect('donor:request_blood_success', pk=blood_request.pk)
    else:
        form = PublicBloodRequestForm()
    
    return render(request, 'donor_portal/request_blood.html', {'form': form})

def request_blood_success(request, pk):
    """Blood request success page."""
    donor = get_logged_in_donor(request)
    if not donor:
        return redirect('donor:login')
    
    blood_request = get_object_or_404(PublicBloodRequest, pk=pk)
    
    context = {
        'donor': donor,
        'blood_request': blood_request,
    }
    return render(request, 'donor_portal/request_blood_success.html', context)

def test_page(request):
    """Test page for development."""
    return render(request, 'donor_portal/test.html')

def contact_submit(request):
    """Handle contact form submission."""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Here you would typically send an email
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('donor:contact')
    
    return redirect('donor:contact')

def faq(request):
    """FAQ page."""
    return render(request, 'donor_portal/faq.html')

def privacy(request):
    """Privacy policy page."""
    return render(request, 'donor_portal/privacy.html')

def terms(request):
    """Terms of service page."""
    return render(request, 'donor_portal/terms.html')

def password_reset(request):
    """Password reset page."""
    return render(request, 'donor_portal/password_reset.html')
