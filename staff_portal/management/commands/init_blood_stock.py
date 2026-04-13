from django.core.management.base import BaseCommand
from staff_portal.models import BloodStock

class Command(BaseCommand):
    help = 'Initialize blood stock records for all blood types'

    def handle(self, *args, **kwargs):
        blood_types = ['A+','A-','B+','B-','AB+','AB-','O+','O-']
        created = 0
        for bt in blood_types:
            stock, was_created = BloodStock.objects.get_or_create(
                blood_type=bt,
                defaults={'units_available': 0, 'minimum_threshold': 3}
            )
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(f'Created {created} blood stock records')
        )
