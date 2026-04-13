from django.contrib import admin
from .models import EmergencyRequest, DonationRecord, BloodStock, PublicBloodRequest

@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'blood_type_needed', 'units_needed', 'urgency_level', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'blood_type_needed', 'urgency_level']

@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'units_donated', 'emergency_request', 'recorded_by']

@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ['blood_type', 'units_available', 
                    'minimum_threshold', 'stock_status', 'last_updated']

@admin.register(PublicBloodRequest)
class PublicBloodRequestAdmin(admin.ModelAdmin):
    list_display = ['requester_name', 'blood_type_needed', 
                    'urgency_level', 'status', 'submitted_at']
    list_filter = ['status', 'urgency_level', 'blood_type_needed']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['staff_user', 'action', 'description', 'timestamp']
    list_filter = ['action']
    readonly_fields = ['staff_user', 'action', 'description', 
                       'timestamp', 'ip_address']
