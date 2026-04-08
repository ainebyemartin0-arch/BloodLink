from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import StaffUser

class StaffUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    designation = forms.CharField(max_length=100, required=False)
    department = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = StaffUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                  'designation', 'department', 'phone_number')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.designation = self.cleaned_data['designation']
        user.department = self.cleaned_data['department']
        user.phone_number = self.cleaned_data['phone_number']
        user.is_staff = True
        if commit:
            user.save()
        return user

class StaffUserChangeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Leave blank to keep current password")
    
    class Meta:
        model = StaffUser
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].help_text = "Leave blank to keep current password"
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
