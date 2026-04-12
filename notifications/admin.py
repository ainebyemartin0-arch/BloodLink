from django.contrib import admin
from .models import SMSNotification, PushSubscription

@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'emergency_request', 'delivery_status', 'donor_response', 'sent_at']
    list_filter = ['delivery_status', 'donor_response']

@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_active', 'subscribed_at']
