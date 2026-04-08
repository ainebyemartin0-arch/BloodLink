from django.contrib.auth.models import AbstractUser
from django.db import models

DESIGNATION_CHOICES = [
    ('lab_technician', 'Laboratory Technician'),
    ('blood_bank_admin', 'Blood Bank Administrator'),
    ('emergency_clinician', 'Emergency Unit Clinician'),
    ('it_staff', 'IT Staff'),
    ('admin', 'System Administrator'),
]

class StaffUser(AbstractUser):
    """Custom user model for hospital staff only."""
    designation = models.CharField(max_length=100, choices=DESIGNATION_CHOICES, default='lab_technician')
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Hospital Staff'
        verbose_name_plural = 'Hospital Staff'
    
    def __str__(self):
        return f"{self.get_full_name()} — {self.get_designation_display()}"
