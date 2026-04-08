from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from .choices import BLOOD_TYPE_CHOICES, LOCATION_CHOICES, GENDER_CHOICES

class Donor(models.Model):
    """Blood donor model — has its own login system separate from StaffUser."""
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)  # Hashed password for donor portal login
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Other')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, default='Other')
    physical_address = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    profile_notes = models.TextField(blank=True)
    
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    
    @property
    def is_eligible(self):
        """Donor is eligible if available and active."""
        return self.is_available and self.is_active
    
    def __str__(self):
        return f"{self.full_name} ({self.blood_type}) — {self.phone_number}"
    
    class Meta:
        ordering = ['-date_registered']
        verbose_name = 'Donor'
        verbose_name_plural = 'Donors'
