from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from notifications.utils import check_sms_delivery_status
from notifications.models import SMSNotification

class Command(BaseCommand):
    help = 'Check SMS delivery status and update notifications accordingly'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Check SMS sent in the last N hours (default: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
    
    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('📱 Checking SMS Delivery Status'))
        self.stdout.write(f"Checking SMS sent in the last {hours} hours...")
        
        if dry_run:
            self.stdout.write("DRY RUN - No changes will be made")
        
        try:
            # Call the delivery status checking function
            check_sms_delivery_status()
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS('✅ SMS delivery status check completed')
                )
                self.stdout.write(
                    self.style.WARNING('Run this command periodically to update delivery statuses')
                )
            else:
                self.stdout.write("Dry run completed - no changes made")
                
        except Exception as e:
            raise CommandError(f'Error checking SMS delivery status: {str(e)}')
