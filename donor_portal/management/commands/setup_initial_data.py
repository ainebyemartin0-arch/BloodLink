from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from donors.models import Donor
from accounts.models import StaffUser

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial data for BloodLink deployment'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create staff user if not exists
        if not StaffUser.objects.exists():
            staff_user = StaffUser.objects.create_user(
                username='admin',
                email='admin@bloodlink.com',
                password='admin123',
                full_name='System Administrator',
                role='admin',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created staff user: {staff_user.username}'))
        else:
            self.stdout.write('Staff user already exists')
        
        # Create sample donor if not exists
        if not Donor.objects.exists():
            donor = Donor.objects.create(
                full_name='John Doe',
                email='john.doe@example.com',
                phone_number='+256700000000',
                blood_type='O+',
                location='Kampala',
                physical_address='123 Kampala Road',
                is_available=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created sample donor: {donor.full_name}'))
        else:
            self.stdout.write('Donor records already exist')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup complete!'))
