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
