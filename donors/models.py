from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from datetime import date, datetime
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Fallback if dateutil is not available
    def relativedelta(start_date, end_date):
        delta = end_date - start_date
        return type('Delta', (), {'years': delta.days // 365, 'months': delta.days // 30, 'days': delta.days % 30})()
from .choices import BLOOD_TYPE_CHOICES, LOCATION_CHOICES, GENDER_CHOICES

class Donor(models.Model):
    """Blood donor model — has its own login system separate from StaffUser."""
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255, blank=True, null=True)  # Hashed password for donor portal login
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)  # Google OAuth ID
    phone_verified = models.BooleanField(default=False)  # Phone verification status
    auth_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('google', 'Google'),
            ('phone', 'Phone'),
        ],
        default='email'
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Other')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, default='Other')
    physical_address = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    google_profile_picture = models.URLField(blank=True, null=True)  # Google profile picture URL
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    next_eligible_date = models.DateField(null=True, blank=True, help_text="Date when donor can donate again")
    total_donations = models.PositiveIntegerField(default=0, help_text="Total number of donations made")
    donation_count_12_months = models.PositiveIntegerField(default=0, help_text="Donations in last 12 months")
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
        elif self.google_profile_picture:
            return self.google_profile_picture
        return 'https://ui-avatars.com/api/?name=' + self.full_name.replace(' ', '+') + '&background=dc2626&color=fff&size=200'
    
    @classmethod
    def get_by_google_id(cls, google_id):
        """Get donor by Google OAuth ID."""
        try:
            return cls.objects.get(google_id=google_id, is_active=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_by_phone_number(cls, phone_number):
        """Get donor by phone number."""
        try:
            return cls.objects.get(phone_number=phone_number, is_active=True)
        except cls.DoesNotExist:
            return None
    
    def authenticate_with_google(self, google_id, email=None, name=None, picture_url=None):
        """Authenticate or create donor using Google OAuth."""
        if self.google_id == google_id:
            return True
        
        # Update existing donor with Google info
        self.google_id = google_id
        if email and not self.email:
            self.email = email
        if name and not self.full_name:
            self.full_name = name
        if picture_url and not self.profile_picture:
            self.google_profile_picture = picture_url
        self.auth_method = 'google'
        self.save()
        return True
    
    def authenticate_with_phone(self, phone_number):
        """Authenticate donor using phone number."""
        if self.phone_number == phone_number and self.phone_verified:
            return True
        return False
    
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
        Professional eligibility calculation following medical guidelines:
        - Must be between 18 and 65 years old
        - Must be marked as available and active
        - Must have completed waiting period since last donation
        - Must not exceed donation frequency limits
        """
        from datetime import date, timedelta
        
        if not self.is_active or not self.is_available:
            return False
        
        # Age eligibility
        if self.age is not None:
            if self.age < 18 or self.age > 65:
                return False
        
        # Check if within eligible period
        if self.next_eligible_date:
            if date.today() < self.next_eligible_date:
                return False
        
        # Check donation frequency (max 6 donations per year)
        if self.donation_count_12_months >= 6:
            return False
        
        return True

    @property
    def days_until_eligible(self):
        """
        Returns how many days until donor can donate again.
        Returns 0 if already eligible.
        """
        from datetime import date
        
        if self.next_eligible_date:
            if date.today() >= self.next_eligible_date:
                return 0
            else:
                return (self.next_eligible_date - date.today()).days
        return 0

    @property
    def eligibility_status_display(self):
        """Human-readable eligibility status"""
        if not self.is_active:
            return "Inactive Account"
        elif not self.is_available:
            return "Unavailable"
        elif not self.is_eligible_to_donate:
            days = self.days_until_eligible
            if days > 0:
                return f"Eligible in {days} days"
            else:
                return "Not Eligible"
        else:
            return "Eligible to Donate"

    def record_donation(self, units_donated=1):
        """
        Professional donation recording with automatic eligibility calculation.
        Updates donation history and calculates next eligible date.
        """
        from datetime import date, timedelta
        from django.utils import timezone
        
        # Update donation counts
        self.total_donations += 1
        self.last_donation_date = date.today()
        
        # Calculate next eligible date (90 days for whole blood, 56 for plasma)
        # Using 90 days as standard for whole blood donation
        self.next_eligible_date = date.today() + timedelta(days=90)
        
        # Update 12-month donation count
        one_year_ago = date.today() - timedelta(days=365)
        # Defer import to avoid circular dependency
        from staff_portal.models import DonationRecord
        recent_donations = DonationRecord.objects.filter(
            donor=self,
            donation_date__gte=one_year_ago
        ).count()
        self.donation_count_12_months = recent_donations + 1  # Include current donation
        
        self.save()
        
        # Create donation record - defer import to avoid circular dependency
        from staff_portal.models import DonationRecord
        return DonationRecord.objects.create(
            donor=self,
            donation_date=date.today(),
            units_donated=units_donated,
            notes=f"Donation #{self.total_donations} recorded automatically"
        )

    def update_eligibility_status(self):
        """
        Update eligibility status based on current date and donation history.
        This method should be called periodically to ensure eligibility is up-to-date.
        """
        from datetime import date, timedelta
        from django.db.models import Count
        
        # Update 12-month donation count
        one_year_ago = date.today() - timedelta(days=365)
        # Defer import to avoid circular dependency
        from staff_portal.models import DonationRecord
        recent_count = DonationRecord.objects.filter(
            donor=self,
            donation_date__gte=one_year_ago
        ).count()
        self.donation_count_12_months = recent_count
        
        # Update next eligible date if needed
        if self.last_donation_date:
            expected_next_date = self.last_donation_date + timedelta(days=90)
            if self.next_eligible_date != expected_next_date:
                self.next_eligible_date = expected_next_date
        
        self.save()

    @classmethod
    def get_eligible_donors_for_blood_type(cls, blood_type):
        """
        Get all eligible donors for a specific blood type.
        Excludes donors who are not eligible due to waiting period or other restrictions.
        """
        return cls.objects.filter(
            blood_type=blood_type,
            is_active=True,
            is_available=True
        ).filter(
            models.Q(next_eligible_date__lte=date.today()) | 
            models.Q(next_eligible_date__isnull=True)
        ).filter(
            donation_count_12_months__lt=6
        )

    @property
    def eligibility_reason(self):
        """Returns human-readable reason if donor is NOT eligible."""
        from datetime import date
        
        if not self.is_active:
            return "Account is inactive"
        if not self.is_available:
            return "Marked as unavailable"
        if self.age is not None:
            if self.age < 18:
                return f"Too young (age {self.age}, minimum 18)"
            if self.age > 65:
                return f"Exceeds age limit (age {self.age}, maximum 65)"
        
        # Check waiting period
        if self.next_eligible_date and date.today() < self.next_eligible_date:
            days = self.days_until_eligible
            return f"Waiting period: {days} days remaining"
        
        # Check donation frequency
        if self.donation_count_12_months >= 6:
            return "Annual donation limit reached (6 donations per year)"
        
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
