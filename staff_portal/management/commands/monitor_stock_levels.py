from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from staff_portal.models import BloodStock, StockAlert
from accounts.models import StaffUser

class Command(BaseCommand):
    help = 'Monitor blood stock levels and send alerts to staff when stocks are low'

    def handle(self, *args, **options):
        """Check all blood stock levels and send alerts if needed"""
        self.stdout.write('Starting blood stock monitoring...')
        
        alerts_created = 0
        critical_alerts = 0
        low_stock_alerts = 0
        
        # Check each blood type
        for blood_stock in BloodStock.objects.all():
            if blood_stock.should_send_alert():
                alert_type = 'critical' if blood_stock.get_stock_status() == 'critical' else 'low'
                
                # Create alert record
                alert = StockAlert.objects.create(
                    blood_stock=blood_stock,
                    alert_type=alert_type,
                    current_units=blood_stock.current_units,
                    message=self.generate_alert_message(blood_stock, alert_type)
                )
                
                # Update last alert sent time
                blood_stock.last_alert_sent = timezone.now()
                blood_stock.save()
                
                alerts_created += 1
                if alert_type == 'critical':
                    critical_alerts += 1
                else:
                    low_stock_alerts += 1
                
                self.stdout.write(
                    self.style.WARNING(
                        f'ALERT SENT: {blood_stock.blood_type} - {alert_type.upper()} '
                        f'({blood_stock.current_units} units)'
                    )
                )
        
        # Summary
        if alerts_created > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Stock monitoring complete: {alerts_created} alerts sent '
                    f'({critical_alerts} critical, {low_stock_alerts} low stock)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Stock monitoring complete: All stock levels adequate')
            )
    
    def generate_alert_message(self, blood_stock, alert_type):
        """Generate professional alert message"""
        status = blood_stock.get_stock_status_display()
        
        if alert_type == 'critical':
            return (
                f'CRITICAL BLOOD SHORTAGE ALERT\n\n'
                f'Blood Type: {blood_stock.blood_type}\n'
                f'Current Stock: {blood_stock.current_units} units\n'
                f'Critical Level: {blood_stock.critical_level} units\n'
                f'Optimal Level: {blood_stock.optimal_level} units\n\n'
                f'IMMEDIATE ACTION REQUIRED: This critical shortage may affect '
                f'patient care. Please contact eligible donors urgently.'
            )
        else:
            return (
                f'LOW BLOOD STOCK ALERT\n\n'
                f'Blood Type: {blood_stock.blood_type}\n'
                f'Current Stock: {blood_stock.current_units} units\n'
                f'Minimum Level: {blood_stock.minimum_level} units\n'
                f'Optimal Level: {blood_stock.optimal_level} units\n\n'
                f'Action Recommended: Stock levels are below minimum. '
                f'Consider organizing blood drive or contacting regular donors.'
            )
