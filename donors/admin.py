from django.contrib import admin
from .models import Donor

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'blood_type', 'phone_number', 'email', 'location', 'is_available', 'is_active', 'date_registered']
    list_filter = ['blood_type', 'location', 'is_available', 'gender']
    search_fields = ['full_name', 'phone_number', 'email']
