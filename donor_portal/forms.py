from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from donors.models import Donor
from donors.choices import BLOOD_TYPE_CHOICES, LOCATION_CHOICES, GENDER_CHOICES

class DonorRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'})
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07xxxxxxxx or +2567xxxxxxxx'})
    )
    password1 = forms.CharField(
        label="Create Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a strong password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    blood_type = forms.ChoiceField(
        choices=BLOOD_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    physical_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your physical address (optional)'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Donor.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different email or login.")
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if Donor.objects.filter(phone_number=phone).exists():
            raise ValidationError("This phone number is already registered. Please use a different number.")
        return phone
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        today = timezone.now().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise ValidationError("You must be at least 18 years old to register as a blood donor.")
        return dob

class DonorLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

class DonorProfileEditForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['phone_number', 'location', 'physical_address', 'is_available', 'profile_notes']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'physical_address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DonorChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your current password'})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your new password'})
    )
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("New passwords do not match.")
        return password2
