from django.db import models
from django.conf import settings
from django.utils import timezone
from donors.models import Donor
from donors.choices import URGENCY_CHOICES

REQUEST_STATUS_CHOICES = [
    ('open', 'Open'),
    ('fulfilled', 'Fulfilled'),
    ('closed', 'Closed'),
]

ALERT_LEVELS = [
    ('low', 'Low Stock'),
    ('critical', 'Critical Shortage'),
    ('emergency', 'Emergency Shortage'),
]

class BloodShortageAlert(models.Model):
    blood_type = models.CharField(max_length=3, choices=[
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ])
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVELS)
    available_donors = models.PositiveIntegerField(default=0)
    total_requests = models.PositiveIntegerField(default=0)
    shortage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')

    def __str__(self):
        return f"{self.blood_type} - {self.alert_level.title()} Alert"

    class Meta:
        ordering = ['-created_at']

class EmergencyRequest(models.Model):
    blood_type_needed = models.CharField(max_length=3, choices=[
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ])
    units_needed = models.PositiveIntegerField(default=1)
    patient_name = models.CharField(max_length=150, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='urgent')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='emergency_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    alert_count = models.PositiveIntegerField(
        default=1,
        help_text="How many times SMS alerts have been sent for this request"
    )
    last_alert_sent = models.DateTimeField(null=True, blank=True)
    units_fulfilled = models.PositiveIntegerField(
        default=0,
        help_text="How many units have been received so far"
    )
    
    def __str__(self):
        return f"[{self.blood_type_needed}] {self.urgency_level.upper()} — {self.status} (#{self.pk})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Emergency Request'
        verbose_name_plural = 'Emergency Requests'

class DonationRecord(models.Model):
    """Records actual donations made by donors."""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donation_records')
    emergency_request = models.ForeignKey(EmergencyRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donation_date = models.DateField()
    units_donated = models.PositiveIntegerField(default=1)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_donations')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.donor.full_name} donated {self.units_donated} unit(s) on {self.donation_date}"
    
    class Meta:
        ordering = ['-donation_date']


class BloodStock(models.Model):
    """
    Tracks current blood stock levels at the hospital.
    One record per blood type — updated manually by staff.
    """
    BLOOD_TYPE_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]

    blood_type = models.CharField(
        max_length=3,
        choices=BLOOD_TYPE_CHOICES,
        unique=True
    )
    units_available = models.PositiveIntegerField(default=0)
    minimum_threshold = models.PositiveIntegerField(
        default=3,
        help_text="Send auto-alert when stock falls below this level"
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_updates'
    )
    notes = models.TextField(blank=True)

    @property
    def is_critical(self):
        return self.units_available <= self.minimum_threshold

    @property
    def stock_status(self):
        if self.units_available == 0:
            return 'empty'
        elif self.units_available <= self.minimum_threshold:
            return 'critical'
        elif self.units_available <= self.minimum_threshold * 2:
            return 'low'
        return 'adequate'

    @property
    def stock_percentage(self):
        max_units = max(self.units_available, self.minimum_threshold * 3)
        return min(100, int((self.units_available / max_units) * 100))

    def __str__(self):
        return f"{self.blood_type}: {self.units_available} units ({self.stock_status})"

    class Meta:
        ordering = ['blood_type']
        verbose_name = 'Blood Stock'
        verbose_name_plural = 'Blood Stock'


class PublicBloodRequest(models.Model):
    """
    Allows patients or families to request blood
    directly from the donor portal.
    Staff must approve before SMS alerts are sent.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved - Alerts Sent'),
        ('rejected', 'Rejected'),
    ]

    requester_name = models.CharField(max_length=150)
    requester_phone = models.CharField(max_length=20)
    requester_relationship = models.CharField(
        max_length=100,
        help_text="e.g. Patient, Mother, Brother"
    )
    patient_name = models.CharField(max_length=150)
    blood_type_needed = models.CharField(max_length=3, choices=[
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ])
    units_needed = models.PositiveIntegerField(default=1)
    urgency_level = models.CharField(max_length=20, choices=[
        ('critical', 'Critical - Life Threatening'),
        ('urgent', 'Urgent - Within 2 Hours'),
        ('normal', 'Normal - Within 24 Hours'),
    ], default='urgent')
    hospital_ward = models.CharField(max_length=100, blank=True)
    additional_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        'accounts.StaffUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_public_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    linked_emergency_request = models.ForeignKey(
        EmergencyRequest,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='public_requests'
    )

    def __str__(self):
        return (f"Public Request: {self.blood_type_needed} by "
                f"{self.requester_name} ({self.status})")

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Public Blood Request'
        verbose_name_plural = 'Public Blood Requests'


class ActivityLog(models.Model):
    """
    Records every important action performed by staff.
    Provides audit trail for hospital management.
    """
    ACTION_CHOICES = [
        ('donor_added', 'Donor Added'),
        ('donor_edited', 'Donor Edited'),
        ('donor_deleted', 'Donor Deleted'),
        ('donor_toggled', 'Donor Availability Toggled'),
        ('request_created', 'Emergency Request Created'),
        ('request_closed', 'Request Closed'),
        ('request_fulfilled', 'Request Fulfilled'),
        ('request_resent', 'Alerts Re-Sent'),
        ('stock_updated', 'Blood Stock Updated'),
        ('public_approved', 'Public Request Approved'),
        ('public_rejected', 'Public Request Rejected'),
        ('staff_registered', 'Staff Registered'),
        ('login', 'Staff Login'),
        ('logout', 'Staff Logout'),
    ]

    staff_user = models.ForeignKey(
        'accounts.StaffUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional references
    related_donor_id = models.IntegerField(null=True, blank=True)
    related_request_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (f"{self.staff_user} — {self.get_action_display()} "
                f"at {self.timestamp.strftime('%Y-%m-%d %H:%M')}")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
