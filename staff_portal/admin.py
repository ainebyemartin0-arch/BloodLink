from django.contrib import admin
from .models import EmergencyRequest, DonationRecord

@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'blood_type_needed', 'units_needed', 'urgency_level', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'blood_type_needed', 'urgency_level']

@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'units_donated', 'emergency_request', 'recorded_by']
