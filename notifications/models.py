from django.db import models
from donors.models import Donor
from staff_portal.models import EmergencyRequest

DELIVERY_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('failed', 'Failed'),
]

DONOR_RESPONSE_CHOICES = [
    ('no_response', 'No Response'),
    ('confirmed', 'Confirmed — Will Donate'),
    ('declined', 'Declined'),
]

class SMSNotification(models.Model):
    emergency_request = models.ForeignKey(EmergencyRequest, on_delete=models.CASCADE, related_name='sms_notifications')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='sms_notifications')
    message_content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending')
    donor_response = models.CharField(max_length=20, choices=DONOR_RESPONSE_CHOICES, default='no_response')
    
    # Enhanced message tracking fields
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    message_status = models.CharField(max_length=50, default='pending')  # Africa's Talking message status
    is_fulfilled = models.BooleanField(default=False)  # Mark as fulfilled when donor responds
    fulfilled_at = models.DateTimeField(null=True, blank=True)  # When donor responded
    
    # Africa's Talking fields
    at_message_id = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000)
    
    def __str__(self):
        status_icon = {
            'pending': 'PENDING',
            'sent': 'SENT',
            'delivered': 'DELIVERED',
            'failed': 'FAILED'
        }.get(self.delivery_status, 'UNKNOWN')
        
        return f"{status_icon} SMS → {self.donor.full_name} | Request #{self.emergency_request.pk} | {self.get_delivery_status_display()}"
    
    @property
    def is_opened(self):
        return self.opened_at is not None
    
    @property
    def is_delivered(self):
        return self.delivery_status == 'delivered'
    
    @property
    def status_badge_class(self):
        if self.delivery_status == 'failed':
            return 'danger'
        elif self.delivery_status == 'delivered' and self.is_opened:
            return 'success'  # Delivered AND opened = complete success
        elif self.delivery_status == 'delivered':
            return 'warning'  # Delivered but not opened yet
        elif self.delivery_status == 'sent':
            return 'info'
        else:
            return 'secondary'
    
    @property
    def status_display(self):
        if self.delivery_status == 'failed':
            return 'FAILED'
        elif self.delivery_status == 'delivered' and self.is_opened:
            return 'OPENED'
        elif self.delivery_status == 'delivered':
            return 'DELIVERED'
        elif self.delivery_status == 'sent':
            return 'SENT'
        else:
            return 'PENDING'
    
    def get_delivery_status_display(self):
        """Get enhanced delivery status display"""
        if self.delivery_status == 'delivered':
            if self.is_opened:
                return 'DELIVERED & OPENED'  # Green when delivered AND opened
            else:
                return 'DELIVERED'  # Yellow when delivered but not opened
        elif self.delivery_status == 'sent':
            return 'SENT TO PHONE'
        elif self.delivery_status == 'failed':
            return 'FAILED'
        else:
            return f'PENDING {self.delivery_status.title()}'
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'SMS Notification'
        verbose_name_plural = 'SMS Notifications'


class PushSubscription(models.Model):
    """Stores browser push notification subscriptions."""
    
    # Can belong to a donor or staff — both optional
    donor = models.ForeignKey(
        'donors.Donor',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='push_subscriptions'
    )
    staff_user = models.ForeignKey(
        'accounts.StaffUser',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='push_subscriptions'
    )
    
    # The subscription data from browser
    endpoint = models.TextField(unique=True)
    p256dh_key = models.TextField()
    auth_key = models.TextField()
    
    user_agent = models.CharField(max_length=300, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.donor:
            return f"Push: {self.donor.full_name}"
        if self.staff_user:
            return f"Push: {self.staff_user.get_full_name()}"
        return f"Push: Anonymous ({self.endpoint[:40]}...)"
    
    class Meta:
        ordering = ['-subscribed_at']
