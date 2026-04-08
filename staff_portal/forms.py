from django import forms
import random
import string
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import StaffUser
from donors.models import Donor
from donors.choices import BLOOD_TYPE_CHOICES, LOCATION_CHOICES, GENDER_CHOICES, URGENCY_CHOICES
from staff_portal.models import EmergencyRequest, DonationRecord

class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class StaffRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = StaffUser
        fields = ['first_name', 'last_name', 'username', 'email', 'designation', 'department', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class DonorForm(forms.ModelForm):
    password_option = forms.ChoiceField(
        choices=[
            ('auto', 'Generate Random Password'),
            ('phone', 'Use Phone Number as Password'),
            ('custom', 'Set Custom Password')
        ],
        initial='auto',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    custom_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom password'}),
        help_text="Only required if 'Set Custom Password' is selected"
    )
    
    class Meta:
        model = Donor
        fields = ['full_name', 'email', 'phone_number', 'gender', 'date_of_birth', 
                  'blood_type', 'location', 'physical_address', 'is_available', 'profile_notes',
                  'password_option', 'custom_password']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'physical_address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make custom_password required only when custom option is selected
        self.fields['custom_password'].required = False
    
    def clean_custom_password(self):
        password_option = self.cleaned_data.get('password_option')
        custom_password = self.cleaned_data.get('custom_password')
        
        if password_option == 'custom' and not custom_password:
            raise forms.ValidationError("Custom password is required when 'Set Custom Password' is selected.")
        
        return custom_password
    
    def generate_random_password(self, length=8):
        """Generate a random password with letters and numbers"""
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    def get_password_for_donor(self):
        """Get the password based on the selected option"""
        password_option = self.cleaned_data.get('password_option')
        
        if password_option == 'auto':
            return self.generate_random_password()
        elif password_option == 'phone':
            return self.cleaned_data.get('phone_number', '').replace(' ', '').replace('-', '')
        elif password_option == 'custom':
            return self.cleaned_data.get('custom_password')
        
        return self.generate_random_password()  # fallback

class DonationRecordForm(forms.ModelForm):
    """Form for recording blood donations from donors."""
    class Meta:
        model = DonationRecord
        fields = ['donor', 'emergency_request', 'donation_date', 'units_donated', 'notes']
        widgets = {
            'donor': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'emergency_request': forms.Select(attrs={'class': 'form-control', 'required': False}),
            'donation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'units_donated': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10, 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any medical notes or observations...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter donors to only show available ones
        self.fields['donor'].queryset = Donor.objects.filter(is_available=True).order_by('full_name')
        
        # Filter emergency requests to only show open ones
        self.fields['emergency_request'].queryset = EmergencyRequest.objects.filter(status='open').order_by('-created_at')
        self.fields['emergency_request'].empty_label = "No specific emergency request (general donation)"

class EmergencyRequestForm(forms.ModelForm):
    class Meta:
        model = EmergencyRequest
        fields = ['blood_type_needed', 'units_needed', 'patient_name', 'ward', 
                  'urgency_level', 'notes']
        widgets = {
            'blood_type_needed': forms.Select(attrs={'class': 'form-control'}),
            'units_needed': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.TextInput(attrs={'class': 'form-control'}),
            'urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
