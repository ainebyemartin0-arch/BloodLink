from django.core.management.base import BaseCommand
from staff_portal.models import BloodStock

class Command(BaseCommand):
    help = 'Initialize blood stock records for all blood types'

    def handle(self, *args, **options):
        """Create BloodStock records for all blood types if they don't exist"""
        self.stdout.write('Initializing blood stock records...')
        
        blood_types = [
            ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ]
        
        created_count = 0
        updated_count = 0
        
        for blood_type_code, blood_type_display in blood_types:
            stock, created = BloodStock.objects.get_or_create(
                blood_type=blood_type_code,
                defaults={
                    'current_units': 25,  # Starting stock level
                    'optimal_level': 50,
                    'minimum_level': 10,
                    'critical_level': 5,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created stock record for {blood_type_code}')
                )
            else:
                updated_count += 1
                self.stdout.write(f'Stock record for {blood_type_code} already exists')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Blood stock initialization complete: '
                f'{created_count} created, {updated_count} already existed'
            )
        )
