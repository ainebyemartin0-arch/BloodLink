from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
from dateutil.relativedelta import relativedelta
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
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
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
    def profile_picture_url(self):
        """Get profile picture URL or return default avatar."""
        if self.profile_picture:
            return self.profile_picture.url
        return 'https://ui-avatars.com/api/?name=' + self.full_name.replace(' ', '+') + '&background=dc2626&color=fff&size=200'
    
    @property
    def is_eligible(self):
        """Donor is eligible if available and active."""
        return self.is_available and self.is_active

    @property
    def age(self):
        """Calculate donor age from date_of_birth."""
        if self.date_of_birth:
            today = date.today()
            return relativedelta(today, self.date_of_birth).years
        return None

    @property
    def is_eligible_to_donate(self):
        """
        Auto-calculate eligibility:
        - Must be between 18 and 65 years old
        - Must be marked as available
        - Must be active
        - Last donation must be at least 90 days ago (3 months)
        """
        if not self.is_active or not self.is_available:
            return False
        if self.age is not None:
            if self.age < 18 or self.age > 65:
                return False
        if self.last_donation_date:
            days_since = (date.today() - self.last_donation_date).days
            if days_since < 90:
                return False
        return True

    @property
    def days_until_eligible(self):
        """
        Returns how many days until donor can donate again.
        Returns 0 if already eligible.
        """
        if self.last_donation_date:
            days_since = (date.today() - self.last_donation_date).days
            remaining = 90 - days_since
            return max(0, remaining)
        return 0

    @property
    def eligibility_reason(self):
        """Returns human-readable reason if donor is NOT eligible."""
        if not self.is_active:
            return "Account is inactive"
        if not self.is_available:
            return "Marked as unavailable"
        if self.age is not None:
            if self.age < 18:
                return f"Too young (age {self.age}, minimum 18)"
            if self.age > 65:
                return f"Exceeds age limit (age {self.age}, maximum 65)"
        if self.last_donation_date:
            days_since = (date.today() - self.last_donation_date).days
            if days_since < 90:
                remaining = 90 - days_since
                return f"Must wait {remaining} more days before donating again"
        return "Eligible to donate"

    @property
    def donation_count(self):
        """Total number of confirmed donations."""
        return self.donation_records.count()

    @property
    def badges(self):
        """Returns list of earned badges based on donation history."""
        count = self.donation_count
        earned = []
        
        if count >= 1:
            earned.append({
                'name': 'First Drop',
                'description': 'Made your first donation',
                'icon': '🩸',
                'color': '#F1948A',
                'level': 'bronze'
            })
        if count >= 3:
            earned.append({
                'name': 'Life Giver',
                'description': '3 donations completed',
                'icon': '💪',
                'color': '#D68910',
                'level': 'silver'
            })
        if count >= 5:
            earned.append({
                'name': 'Hero Donor',
                'description': '5 donations — you are a hero!',
                'icon': '🦸',
                'color': '#1A5276',
                'level': 'gold'
            })
        if count >= 10:
            earned.append({
                'name': 'Legend',
                'description': '10 donations — BloodLink Legend!',
                'icon': '🏆',
                'color': '#C0392B',
                'level': 'platinum'
            })
        if self.sms_notifications.filter(
            donor_response='confirmed'
        ).count() >= 3:
            earned.append({
                'name': 'First Responder',
                'description': 'Confirmed 3+ emergency alerts',
                'icon': '⚡',
                'color': '#1E8449',
                'level': 'special'
            })
        
        return earned

    @property
    def next_badge(self):
        """Returns info about next badge to earn."""
        count = self.donation_count
        if count < 1:
            return {'name': 'First Drop', 'needed': 1, 'current': count}
        elif count < 3:
            return {'name': 'Life Giver', 'needed': 3, 'current': count}
        elif count < 5:
            return {'name': 'Hero Donor', 'needed': 5, 'current': count}
        elif count < 10:
            return {'name': 'Legend', 'needed': 10, 'current': count}
        return None
    
    def __str__(self):
        return f"{self.full_name} ({self.blood_type}) — {self.phone_number}"
    
    class Meta:
        ordering = ['-date_registered']
        verbose_name = 'Donor'
        verbose_name_plural = 'Donors'
