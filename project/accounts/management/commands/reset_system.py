from django.core.management.base import BaseCommand
from django.db import transaction
from assets.models import Asset
from assignments.models import Assignment
from requests.models import AssetRequest

class Command(BaseCommand):
    help = 'Reset system: Clear all assignments and make all assets available'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', 
                          help='Confirm the reset operation')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING('This will reset ALL assignments and asset statuses!')
            )
            self.stdout.write('Run with --confirm to proceed')
            return

        with transaction.atomic():
            # Mark all assignments as returned
            active_assignments = Assignment.objects.filter(active=True)
            assignment_count = active_assignments.count()
            
            for assignment in active_assignments:
                assignment.mark_returned()
            
            # Reset all assets to available
            Asset.objects.all().update(status=Asset.STATUS_AVAILABLE)
            asset_count = Asset.objects.count()
            
            # Clear ALL request history
            all_requests = AssetRequest.objects.all()
            request_count = all_requests.count()
            all_requests.delete()

        self.stdout.write(
            self.style.SUCCESS(f'System reset completed:')
        )
        self.stdout.write(f'- {assignment_count} assignments returned')
        self.stdout.write(f'- {asset_count} assets set to available')
        self.stdout.write(f'- {request_count} requests cleared')