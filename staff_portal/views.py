from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, F, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db import transaction

from donors.models import Donor
from donors.choices import BLOOD_TYPE_CHOICES, LOCATION_CHOICES
from .models import EmergencyRequest, DonationRecord, BloodStock, PublicBloodRequest, ActivityLog
from notifications.models import SMSNotification
from .utils import log_activity

# Import from whichever app actually has these models:
from staff_portal.models import EmergencyRequest, DonationRecord, BloodShortageAlert, BloodStock
from .forms import StaffLoginForm, StaffRegistrationForm, DonorForm, EmergencyRequestForm, DonationRecordForm
from notifications.utils import send_emergency_sms

def redirect_root(request):
    if request.user.is_authenticated:
        return redirect('staff:dashboard')
    else:
        return redirect('staff:login')

def staff_login(request):
    if request.method == 'POST':
        form = StaffLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Log the activity
                log_activity(request, 'login', f'Staff login: {username}')
                
                return redirect('staff:dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = StaffLoginForm()
    
    return render(request, 'staff_portal/login.html', {'form': form})

def staff_logout(request):
    logout(request)
    return redirect('staff:login')

@login_required
def dashboard(request):
    # Donor Statistics - ACCURATE
    total_donors = Donor.objects.filter(is_active=True).count()
    available_donors = Donor.objects.filter(is_available=True, is_active=True).count()
    unavailable_donors = Donor.objects.filter(is_available=False, is_active=True).count()
    
    # Emergency Request Statistics - ACCURATE
    total_requests = EmergencyRequest.objects.count()
    open_requests = EmergencyRequest.objects.filter(status='open').count()
    fulfilled_requests = EmergencyRequest.objects.filter(status='fulfilled').count()
    closed_requests = EmergencyRequest.objects.filter(status='closed').count()
    critical_requests = EmergencyRequest.objects.filter(status='open', urgency_level='critical').count()
    
    # SMS Statistics - ACCURATE AND COMPREHENSIVE
    total_sms = SMSNotification.objects.count()
    pending_sms = SMSNotification.objects.filter(delivery_status='pending').count()
    sent_sms = SMSNotification.objects.filter(delivery_status='sent').count()
    delivered_sms = SMSNotification.objects.filter(delivery_status='delivered').count()
    failed_sms = SMSNotification.objects.filter(delivery_status='failed').count()
    
    # Donor Response Statistics - ACCURATE
    confirmed_responses = SMSNotification.objects.filter(donor_response='confirmed').count()
    declined_responses = SMSNotification.objects.filter(donor_response='declined').count()
    no_response_count = SMSNotification.objects.filter(donor_response='no_response').count()
    
    # Donation Statistics - ACCURATE
    total_donations = DonationRecord.objects.count()
    donations_this_month = DonationRecord.objects.filter(
        donation_date__year=timezone.now().year,
        donation_date__month=timezone.now().month
    ).count()
    
    # Blood Type Distribution - ACCURATE
    blood_type_stats = Donor.objects.values('blood_type').annotate(count=Count('id')).order_by('blood_type')
    
    # Recent Data - ACCURATE
    recent_requests = EmergencyRequest.objects.order_by('-created_at')[:5]
    recent_donors = Donor.objects.order_by('-date_registered')[:5]
    
    # Blood Shortage Alerts - NEW
    active_alerts = BloodShortageAlert.objects.filter(is_active=True).order_by('-created_at')
    emergency_alerts = active_alerts.filter(alert_level='emergency')
    critical_alerts = active_alerts.filter(alert_level='critical')
    low_alerts = active_alerts.filter(alert_level='low')
    
    # Public Requests - NEW
    pending_public_requests = PublicBloodRequest.objects.filter(status='pending').count()
    
    # Blood Stock Alerts - NEW
    critical_stocks = BloodStock.objects.filter(
        units_available__lte=F('minimum_threshold')
    )
    
    context = {
        # Donor Stats
        'total_donors': total_donors,
        'available_donors': available_donors,
        'unavailable_donors': unavailable_donors,
        
        # Request Stats
        'total_requests': total_requests,
        'open_requests': open_requests,
        'fulfilled_requests': fulfilled_requests,
        'closed_requests': closed_requests,
        'critical_requests': critical_requests,
        
        # SMS Stats - COMPLETE AND ACCURATE
        'total_sms': total_sms,
        'pending_sms': pending_sms,
        'sent_sms': sent_sms,
        'delivered_sms': delivered_sms,
        'failed_sms': failed_sms,
        
        # Response Stats
        'confirmed_responses': confirmed_responses,
        'declined_responses': declined_responses,
        'no_response_count': no_response_count,
        
        # Donation Stats
        'total_donations': total_donations,
        'donations_this_month': donations_this_month,
        
        # Data for displays
        'recent_requests': recent_requests,
        'recent_donors': recent_donors,
        'blood_type_stats': blood_type_stats,
        'critical_stocks': critical_stocks,
        
        # Blood Shortage Alerts
        'active_alerts': active_alerts,
        'emergency_alerts': emergency_alerts,
        'critical_alerts': critical_alerts,
        'low_alerts': low_alerts,
        
        # Public Requests
        'pending_public_requests': pending_public_requests,
    }
    return render(request, 'staff_portal/dashboard.html', context)

@login_required
def register_staff(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can register new staff members.')
        return redirect('staff:dashboard')
    
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, f'Staff member {user.username} has been registered successfully.')
            return redirect('staff:dashboard')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'staff_portal/register_staff.html', {'form': form})

@login_required
def donor_list(request):
    blood_type = request.GET.get('blood_type', '')
    location = request.GET.get('location', '')
    availability = request.GET.get('availability', '')
    
    donors = Donor.objects.all()
    if blood_type:
        donors = donors.filter(blood_type=blood_type)
    if location:
        donors = donors.filter(location=location)
    if availability == 'available':
        donors = donors.filter(is_available=True, is_active=True)
    elif availability == 'unavailable':
        donors = donors.filter(is_available=False)
    
    context = {
        'donors': donors,
        'available_donors': donors.filter(is_available=True, is_active=True),
        'blood_type': blood_type,
        'location': location,
        'availability': availability,
        'blood_type_choices': BLOOD_TYPE_CHOICES,
        'location_choices': LOCATION_CHOICES,
    }
    return render(request, 'staff_portal/donor_list.html', context)

@login_required
def donor_add(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            
            # Get password based on selected option
            password = form.get_password_for_donor()
            donor.set_password(password)
            donor.save()
            
            # Show success message with password information
            password_option = form.cleaned_data.get('password_option')
            if password_option == 'auto':
                messages.success(request, f"Donor {donor.full_name} registered. Generated password: {password}")
            elif password_option == 'phone':
                messages.success(request, f"Donor {donor.full_name} registered. Password set to their phone number: {password}")
            else:
                messages.success(request, f"Donor {donor.full_name} registered with custom password.")
            
            # Log the activity
            log_activity(
                request, 'donor_added',
                f'Added donor: {donor.full_name} ({donor.blood_type})',
                donor_id=donor.pk
            )
            
            return redirect('staff:donor_list')
    else:
        form = DonorForm()
    
    return render(request, 'staff_portal/donor_form.html', {'form': form, 'title': 'Register Donor'})

@login_required
def donor_detail(request, pk):
    try:
        donor = Donor.objects.get(pk=pk)
        sms_history = donor.sms_notifications.order_by('-sent_at')[:10]
        donation_history = donor.donation_records.order_by('-donation_date')[:10]
        
        context = {
            'donor': donor,
            'sms_history': sms_history,
            'donation_history': donation_history,
        }
        return render(request, 'staff_portal/donor_detail.html', context)
    except Donor.DoesNotExist:
        messages.error(request, f"Donor #{pk} not found. The donor may have been deleted or never existed.")
        return redirect('staff:donor_list')

@login_required
def donor_edit(request, pk):
    try:
        donor = Donor.objects.get(pk=pk)
        
        if request.method == 'POST':
            form = DonorForm(request.POST, instance=donor)
            if form.is_valid():
                form.save()
                
                # Check if save and continue was clicked
                if 'save_and_continue' in request.POST:
                    messages.success(request, f"Donor {donor.full_name} updated successfully. You can continue editing.")
                    return redirect('staff:donor_edit', pk=donor.pk)
                else:
                    messages.success(request, f"Donor {donor.full_name} updated successfully.")
                    return redirect('staff:donor_detail', pk=donor.pk)
        else:
            form = DonorForm(instance=donor)
        
        return render(request, 'staff_portal/donor_form.html', {'form': form, 'title': 'Edit Donor', 'donor': donor})
    except Donor.DoesNotExist:
        messages.error(request, f"Donor #{pk} not found. The donor may have been deleted or never existed.")
        return redirect('staff:donor_list')

@login_required
def donor_toggle_availability(request, pk):
    if request.method != 'POST':
        return redirect('staff:donor_detail', pk=pk)
    
    try:
        donor = Donor.objects.get(pk=pk)
        donor.is_available = not donor.is_available
        donor.save()
        
        status = "available" if donor.is_available else "unavailable"
        messages.success(request, f"Donor {donor.full_name} is now {status}.")
        return redirect('staff:donor_detail', pk=pk)
    except Donor.DoesNotExist:
        messages.error(request, f"Donor #{pk} not found. The donor may have been deleted or never existed.")
        return redirect('staff:donor_list')

@login_required
def donor_delete(request, pk):
    if request.method != 'POST':
        return redirect('staff:donor_detail', pk=pk)
    
    try:
        donor = Donor.objects.get(pk=pk)
        donor_name = donor.full_name
        
        # Delete the donor without any limitations
        donor.delete()
        messages.success(request, f"Donor {donor_name} has been deleted successfully.")
        return redirect('staff:donor_list')
    except Donor.DoesNotExist:
        messages.error(request, f"Donor #{pk} not found. The donor may have been deleted or never existed.")
        return redirect('staff:donor_list')

@login_required
def request_list(request):
    from notifications.models import SMSNotification
    from django.db.models import Count, Q
    
    requests = EmergencyRequest.objects.select_related('created_by').all()
    
    # Annotate each request with confirmed donor count
    requests_with_counts = requests.annotate(
        confirmed_donors=Count(
            'sms_notifications',
            filter=Q(sms_notifications__donor_response='confirmed')
        )
    )
    
    return render(request, 'staff_portal/request_list.html', {
        'requests': requests_with_counts,
        'open_requests': requests.filter(status='open'),
        'fulfilled_requests': requests.filter(status='fulfilled'),
    })

@login_required
def request_create(request):
    if request.method == 'POST':
        form = EmergencyRequestForm(request.POST)
        if form.is_valid():
            emergency_request = form.save(commit=False)
            emergency_request.created_by = request.user
            emergency_request.save()
            
            sms_result = send_emergency_sms(emergency_request)
            
            # Send push notifications alongside SMS
            from notifications.push_utils import send_emergency_push_alerts
            push_result = send_emergency_push_alerts(emergency_request)
            
            messages.success(request, f"Emergency request created. SMS alerts sent to {sms_result['sent_count']} donors (failed: {sms_result['failed_count']}). Push notifications sent to {push_result['sent']} devices (failed: {push_result['failed']}).")
            
            # Add notification data to session for immediate display
            request.session['emergency_notification'] = {
                'type': 'danger',
                'title': '🚨 Emergency Blood Request Created',
                'message': f'{emergency_request.units_needed} units of {emergency_request.blood_type_needed} blood needed urgently in {emergency_request.ward}',
                'url': f'/staff/requests/{emergency_request.pk}/',
                'sound': 'urgent',
                'urgent': True
            }
            
            return redirect('staff:request_detail', pk=emergency_request.pk)
    else:
        form = EmergencyRequestForm()
    
    # Add blood type choices for the interactive selector
    blood_type_choices = EmergencyRequestForm.base_fields['blood_type_needed'].choices
    
    return render(request, 'staff_portal/request_form.html', {
        'form': form,
        'blood_type_choices': blood_type_choices
    })

@login_required
def request_detail(request, pk):
    try:
        emergency_request = EmergencyRequest.objects.get(pk=pk)
        sms_list = emergency_request.sms_notifications.select_related('donor').all()
        
        context = {
            'emergency_request': emergency_request,
            'sms_list': sms_list,
        }
        return render(request, 'staff_portal/request_detail.html', context)
    except EmergencyRequest.DoesNotExist:
        messages.error(request, f"Emergency Request #{pk} not found. It may have been deleted or never existed.")
        return redirect('staff:request_list')

@login_required
def request_close(request, pk):
    if request.method != 'POST':
        return redirect('staff:request_detail', pk=pk)
    
    try:
        emergency_request = EmergencyRequest.objects.get(pk=pk)
        emergency_request.status = 'closed'
        emergency_request.save()
        
        messages.success(request, f"Request #{emergency_request.pk} has been closed.")
        return redirect('staff:request_detail', pk=pk)
    except EmergencyRequest.DoesNotExist:
        messages.error(request, f"Emergency Request #{pk} not found. It may have been deleted or never existed.")
        return redirect('staff:request_list')

@login_required
def request_delete(request, pk):
    if request.method != 'POST':
        return redirect('staff:request_detail', pk=pk)
    
    try:
        emergency_request = EmergencyRequest.objects.get(pk=pk)
        request_id = emergency_request.pk
        
        # Delete all related SMS notifications first
        sms_count = emergency_request.sms_notifications.count()
        emergency_request.sms_notifications.all().delete()
        
        # Delete the emergency request
        emergency_request.delete()
        
        messages.success(request, f"Request #{request_id} and {sms_count} related SMS notifications have been deleted.")
        return redirect('staff:request_list')
    except EmergencyRequest.DoesNotExist:
        messages.error(request, f"Emergency Request #{pk} not found. It may have been already deleted.")
        return redirect('staff:request_list')

@login_required
def reports(request):
    blood_type_breakdown = Donor.objects.values('blood_type').annotate(
        total=Count('id'),
        available=Count('id', filter=Q(is_available=True))
    ).order_by('blood_type')
    
    # Calculate availability rate for each blood type
    for stat in blood_type_breakdown:
        if stat['total'] > 0:
            stat['availability_rate'] = round((stat['available'] / stat['total']) * 100, 1)
        else:
            stat['availability_rate'] = 0
    
    total_requests_by_blood = EmergencyRequest.objects.values('blood_type_needed').annotate(count=Count('id'))
    recent_donations = DonationRecord.objects.select_related('donor', 'recorded_by').order_by('-donation_date')[:20]
    
    # Calculate totals for the template
    total_available_donors = sum(item['available'] for item in blood_type_breakdown)
    total_requests_count = sum(item['count'] for item in total_requests_by_blood)
    
    # Calculate additional statistics for the enhanced template
    total_donors = sum(item['total'] for item in blood_type_breakdown)
    total_unavailable_donors = total_donors - total_available_donors
    
    # Find most and least common blood types
    if blood_type_breakdown:
        most_common = max(blood_type_breakdown, key=lambda x: x['total'])
        least_common = min(blood_type_breakdown, key=lambda x: x['total'])
    else:
        most_common = None
        least_common = None
    
    # Calculate average availability
    if total_donors > 0:
        average_availability = round((total_available_donors / total_donors) * 100, 1)
    else:
        average_availability = 0
    
    context = {
        'blood_type_breakdown': blood_type_breakdown,
        'total_requests_by_blood': total_requests_by_blood,
        'recent_donations': recent_donations,
        'total_available_donors': total_available_donors,
        'total_requests_count': total_requests_count,
        'total_donors': total_donors,
        'total_unavailable_donors': total_unavailable_donors,
        'most_common': most_common,
        'least_common': least_common,
        'average_availability': average_availability,
    }
    return render(request, 'staff_portal/reports.html', context)

@csrf_exempt
@login_required
def check_shortage_api(request):
    """API endpoint to trigger blood shortage check"""
    if request.method == 'POST':
        try:
            # Import the management command
            from staff_portal.management.commands.check_blood_shortage import Command
            from io import StringIO
            from django.core.management import call_command
            
            # Capture command output
            out = StringIO()
            call_command('check_blood_shortage', stdout=out)
            
            return JsonResponse({
                'success': True,
                'message': 'Blood shortage check completed',
                'output': out.getvalue()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error running shortage check: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST method allowed'
    })

# Donation Recording Views
@login_required
def donation_list(request):
    """Display all recorded donations."""
    donations = DonationRecord.objects.select_related('donor', 'emergency_request', 'recorded_by').order_by('-donation_date')
    
    # Filter options
    date_filter = request.GET.get('date', '')
    blood_type_filter = request.GET.get('blood_type', '')
    
    if date_filter:
        donations = donations.filter(donation_date=date_filter)
    if blood_type_filter:
        donations = donations.filter(donor__blood_type=blood_type_filter)
    
    context = {
        'donations': donations,
        'date_filter': date_filter,
        'blood_type_filter': blood_type_filter,
        'blood_types': BLOOD_TYPE_CHOICES,
    }
    return render(request, 'staff_portal/donation_list.html', context)

@login_required
def donation_create(request):
    """Record a new blood donation."""
    if request.method == 'POST':
        form = DonationRecordForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.recorded_by = request.user
            donation.save()
            
            # Check if this donation fulfills an emergency request
            if donation.emergency_request:
                check_request_fulfillment(donation.emergency_request)
            
            messages.success(request, f"Donation recorded successfully! {donation.donor.full_name} donated {donation.units_donated} unit(s).")
            return redirect('staff:donation_list')
    else:
        form = DonationRecordForm()
        # Set today's date as default
        form.fields['donation_date'].initial = timezone.now().date()
    
    context = {
        'form': form,
        'title': 'Record Blood Donation'
    }
    return render(request, 'staff_portal/donation_form.html', context)

def check_request_fulfillment(emergency_request):
    """Check if an emergency request has been fulfilled and update status."""
    # Count total units donated for this request
    total_donated = DonationRecord.objects.filter(
        emergency_request=emergency_request
    ).aggregate(total=Sum('units_donated'))['total'] or 0
    
    # If donated units meet or exceed needed units, mark as fulfilled
    if total_donated >= emergency_request.units_needed:
        emergency_request.status = 'fulfilled'
        emergency_request.fulfilled_at = timezone.now()
        emergency_request.save()
        
        # You could send a notification here that request is fulfilled
        print(f"Emergency Request #{emergency_request.pk} has been fulfilled with {total_donated} units donated.")

@login_required
def blood_stock(request):
    """View and manage blood stock levels."""
    stocks = BloodStock.objects.all().order_by('blood_type')
    
    # Auto-create missing stock records
    existing_types = stocks.values_list('blood_type', flat=True)
    blood_types = ['A+','A-','B+','B-','AB+','AB-','O+','O-']
    for bt in blood_types:
        if bt not in existing_types:
            BloodStock.objects.create(
                blood_type=bt,
                units_available=0,
                minimum_threshold=3
            )
    stocks = BloodStock.objects.all().order_by('blood_type')
    
    critical_stocks = stocks.filter(
        units_available__lte=F('minimum_threshold')
    )
    
    context = {
        'stocks': stocks,
        'critical_count': critical_stocks.count(),
        'total_units': sum(s.units_available for s in stocks),
        'empty_types': stocks.filter(units_available=0).count(),
    }
    return render(request, 'staff_portal/blood_stock.html', context)


@login_required
def update_blood_stock(request, pk):
    """Update units for a specific blood type."""
    if request.method == 'POST':
        stock = get_object_or_404(BloodStock, pk=pk)
        try:
            new_units = int(request.POST.get('units_available', 0))
            new_threshold = int(request.POST.get('minimum_threshold', 3))
            notes = request.POST.get('notes', '')
            
            stock.units_available = max(0, new_units)
            stock.minimum_threshold = max(1, new_threshold)
            stock.notes = notes
            stock.updated_by = request.user
            stock.save()
            
            # Auto-create emergency request if stock is critical
            if stock.is_critical and stock.units_available > 0:
                messages.warning(
                    request,
                    f'⚠️ {stock.blood_type} stock is critically low '
                    f'({stock.units_available} units). '
                    f'Consider sending an emergency alert.'
                )
            elif stock.units_available == 0:
                messages.error(
                    request,
                    f'🚨 {stock.blood_type} stock is EMPTY! '
                    f'Please create an emergency request immediately.'
                )
            else:
                messages.success(
                    request,
                    f'✅ {stock.blood_type} stock updated to '
                    f'{stock.units_available} units.'
                )
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value entered.')
    
    return redirect('staff:blood_stock')


@login_required
def dashboard_stats_api(request):
    """
    Returns live dashboard stats as JSON.
    Called every 60 seconds by JavaScript to update stats
    without page reload.
    """
    from notifications.models import SMSNotification
    
    stats = {
        'total_donors': Donor.objects.count(),
        'available_donors': Donor.objects.filter(
            is_available=True, is_active=True
        ).count(),
        'total_requests': EmergencyRequest.objects.count(),
        'open_requests': EmergencyRequest.objects.filter(
            status='open'
        ).count(),
        'total_sms': SMSNotification.objects.count(),
        'confirmed_responses': SMSNotification.objects.filter(
            donor_response='confirmed'
        ).count(),
        'critical_stocks': BloodStock.objects.filter(
            units_available__lte=F('minimum_threshold')
        ).count(),
    }
    return JsonResponse(stats)


@login_required
def request_resend_alerts(request, pk):
    """
    Re-send SMS alerts for an existing open emergency request.
    Used when no donors have responded after initial alert.
    """
    if request.method == 'POST':
        emergency_request = get_object_or_404(
            EmergencyRequest, pk=pk, status='open'
        )
        
        from notifications.utils import send_emergency_sms
        from django.utils import timezone
        
        result = send_emergency_sms(emergency_request)
        
        emergency_request.alert_count += 1
        emergency_request.last_alert_sent = timezone.now()
        emergency_request.save(update_fields=[
            'alert_count', 'last_alert_sent'
        ])
        
        messages.success(
            request,
            f'🔔 Re-alert #{emergency_request.alert_count} sent to '
            f'{result.get("sent_count", 0)} donors for '
            f'{emergency_request.blood_type_needed} blood.'
        )
    
    return redirect('staff:request_detail', pk=pk)


@login_required
def request_fulfill(request, pk):
    """Mark a request as fulfilled and update units count."""
    if request.method == 'POST':
        emergency_request = get_object_or_404(EmergencyRequest, pk=pk)
        units_received = int(request.POST.get('units_received', 0))
        
        emergency_request.units_fulfilled = units_received
        emergency_request.status = 'fulfilled'
        
        from django.utils import timezone
        emergency_request.fulfilled_at = timezone.now()
        emergency_request.save()
        
        # Update blood stock if BloodStock record exists
        try:
            stock = BloodStock.objects.get(
                blood_type=emergency_request.blood_type_needed
            )
            stock.units_available += units_received
            stock.updated_by = request.user
            stock.save()
            messages.success(
                request,
                f'✅ Request fulfilled! {units_received} units of '
                f'{emergency_request.blood_type_needed} received. '
                f'Blood stock updated automatically.'
            )
        except BloodStock.DoesNotExist:
            messages.success(
                request,
                f'✅ Request marked as fulfilled with '
                f'{units_received} units received.'
            )
    
    return redirect('staff:request_detail', pk=pk)


@login_required
def export_reports_pdf(request):
    """
    Generate PDF report of all system data.
    Includes donors, requests, SMS stats, and blood stock.
    """
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from io import BytesIO
    from datetime import datetime
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=colors.HexColor('#2C3E50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#34495E')
    )
    
    # Title
    story.append(Paragraph("BloodLink System Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Donor Statistics
    story.append(Paragraph("Donor Statistics", heading_style))
    donor_data = [
        ['Metric', 'Count'],
        ['Total Donors', str(Donor.objects.count())],
        ['Available Donors', str(Donor.objects.filter(is_available=True, is_active=True).count())],
        ['Active Donors', str(Donor.objects.filter(is_active=True).count())],
    ]
    donor_table = Table(donor_data, hAlign='LEFT')
    donor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
    ]))
    story.append(donor_table)
    story.append(Spacer(1, 20))
    
    # Emergency Request Statistics
    story.append(Paragraph("Emergency Request Statistics", heading_style))
    request_data = [
        ['Metric', 'Count'],
        ['Total Requests', str(EmergencyRequest.objects.count())],
        ['Open Requests', str(EmergencyRequest.objects.filter(status='open').count())],
        ['Fulfilled Requests', str(EmergencyRequest.objects.filter(status='fulfilled').count())],
        ['Critical Requests', str(EmergencyRequest.objects.filter(status='open', urgency_level='critical').count())],
    ]
    request_table = Table(request_data, hAlign='LEFT')
    request_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FADBD8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5B9B7'))
    ]))
    story.append(request_table)
    story.append(Spacer(1, 20))
    
    # SMS Statistics
    story.append(Paragraph("SMS Notification Statistics", heading_style))
    from notifications.models import SMSNotification
    sms_data = [
        ['Metric', 'Count'],
        ['Total SMS Sent', str(SMSNotification.objects.count())],
        ['Delivered SMS', str(SMSNotification.objects.filter(delivery_status='delivered').count())],
        ['Failed SMS', str(SMSNotification.objects.filter(delivery_status='failed').count())],
        ['Confirmed Responses', str(SMSNotification.objects.filter(donor_response='confirmed').count())],
        ['Declined Responses', str(SMSNotification.objects.filter(donor_response='declined').count())],
    ]
    sms_table = Table(sms_data, hAlign='LEFT')
    sms_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D5F5E3')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#A9DFBF'))
    ]))
    story.append(sms_table)
    story.append(Spacer(1, 20))
    
    # Blood Stock Statistics
    story.append(Paragraph("Blood Stock Levels", heading_style))
    stock_data = [['Blood Type', 'Units Available', 'Status', 'Critical Threshold']]
    for stock in BloodStock.objects.all().order_by('blood_type'):
        stock_data.append([
            stock.blood_type,
            str(stock.units_available),
            stock.stock_status.title(),
            f"{stock.minimum_threshold} units"
        ])
    stock_table = Table(stock_data, hAlign='LEFT')
    stock_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8E44AD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EBDEF0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D7BDE2'))
    ]))
    story.append(stock_table)
    
    # Build PDF
    doc.build(story)
    
    # Get PDF value
    pdf_value = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(pdf_value, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bloodlink_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


@login_required
def public_requests_list(request):
    """Staff view of all public blood requests."""
    requests_list = PublicBloodRequest.objects.all()
    pending_count = requests_list.filter(status='pending').count()
    
    context = {
        'public_requests': requests_list,
        'pending_count': pending_count,
    }
    return render(request, 'staff_portal/public_requests.html', context)


@login_required
def approve_public_request(request, pk):
    """
    Approve a public blood request and automatically
    create an EmergencyRequest + send SMS alerts.
    """
    if request.method == 'POST':
        from django.utils import timezone
        public_req = get_object_or_404(PublicBloodRequest, pk=pk)
        
        # Create emergency request
        emergency = EmergencyRequest.objects.create(
            blood_type_needed=public_req.blood_type_needed,
            units_needed=public_req.units_needed,
            patient_name=public_req.patient_name,
            ward=public_req.hospital_ward,
            urgency_level=public_req.urgency_level,
            notes=(f"Public request by {public_req.requester_name} "
                   f"({public_req.requester_relationship}). "
                   f"{public_req.additional_notes}"),
            created_by=request.user,
            status='open',
        )
        
        # Send SMS alerts
        from notifications.utils import send_emergency_sms
        result = send_emergency_sms(emergency)
        
        # Update public request status
        public_req.status = 'approved'
        public_req.reviewed_by = request.user
        public_req.reviewed_at = timezone.now()
        public_req.linked_emergency_request = emergency
        public_req.save()
        
        # Log activities
        log_activity(
            request, 'public_approved',
            f'Approved public blood request from {public_req.requester_name} '
            f'for {public_req.blood_type_needed} blood',
            request_id=emergency.pk
        )
        log_activity(
            request, 'request_created',
            f'Created emergency request for {emergency.blood_type_needed} '
            f'blood — {emergency.units_needed} units — '
            f'{emergency.urgency_level}',
            request_id=emergency.pk
        )
        
        messages.success(
            request,
            f'✅ Request approved! Emergency Request #{emergency.pk} created. '
            f'SMS alerts sent to {result.get("sent_count", 0)} donors.'
        )
        return redirect('staff:request_detail', pk=emergency.pk)
    
    return redirect('staff:public_requests_list')


@login_required
def reject_public_request(request, pk):
    """Reject a public blood request with reason."""
    if request.method == 'POST':
        from django.utils import timezone
        public_req = get_object_or_404(PublicBloodRequest, pk=pk)
        reason = request.POST.get('rejection_reason', 'No reason provided')
        
        public_req.status = 'rejected'
        public_req.reviewed_by = request.user
        public_req.reviewed_at = timezone.now()
        public_req.rejection_reason = reason
        public_req.save()
        
        # Log activity
        log_activity(
            request, 'public_rejected',
            f'Rejected public blood request from {public_req.requester_name} '
            f'for {public_req.blood_type_needed} blood',
            request_id=public_req.pk
        )
        
        messages.warning(
            request,
            f'Request from {public_req.requester_name} has been rejected.'
        )
    return redirect('staff:public_requests_list')


@login_required
def activity_log(request):
    """View staff activity log — superuser only."""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('staff:dashboard')
    
    logs = ActivityLog.objects.select_related('staff_user').all()[:200]
    return render(request, 'staff_portal/activity_log.html', {
        'logs': logs
    })


@login_required
def donation_detail(request, pk):
    """View details of a specific donation."""
    donation = get_object_or_404(DonationRecord.objects.select_related('donor', 'emergency_request', 'recorded_by'), pk=pk)
    
    context = {
        'donation': donation,
    }
    return render(request, 'staff_portal/donation_detail.html', context)


@login_required
def request_escalate(request, pk):
    """Escalate an emergency request to higher authorities."""
    emergency_request = get_object_or_404(EmergencyRequest, pk=pk)
    
    if request.method == 'POST':
        # Log the escalation
        log_activity(
            request.user,
            'request_escalated',
            f'Emergency request for {emergency_request.blood_type_needed} blood escalated to higher authorities',
            related_request_id=emergency_request.pk
        )
        
        # Update the request to mark as escalated
        emergency_request.urgency_level = 'critical'  # Upgrade to critical
        emergency_request.save()
        
        messages.success(
            request,
            f'✅ Request escalated to higher authorities. Urgency level upgraded to critical.'
        )
        
        return redirect('staff:request_detail', pk=emergency_request.pk)
    
    return redirect('staff:request_detail', pk=emergency_request.pk)
