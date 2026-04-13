from django.core.management.base import BaseCommand
from donors.models import Donor
from datetime import date

class Command(BaseCommand):
    help = 'Auto-update donor eligibility based on last donation date'

    def handle(self, *args, **kwargs):
        donors = Donor.objects.filter(is_active=True)
        updated_eligible = 0
        updated_ineligible = 0

        for donor in donors:
            should_be_available = donor.is_eligible_to_donate
            if should_be_available != donor.is_available:
                donor.is_available = should_be_available
                donor.save(update_fields=['is_available'])
                if should_be_available:
                    updated_eligible += 1
                else:
                    updated_ineligible += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Eligibility check complete: '
                f'{updated_eligible} marked eligible, '
                f'{updated_ineligible} marked ineligible'
            )
        )
