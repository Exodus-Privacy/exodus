from django.core.management.base import BaseCommand
from exodus.core.dns import refresh_dns


class Command(BaseCommand):
    help = 'Refresh DNS tracking flag'

    def handle(self, *args, **options):
        refresh_dns()
        self.stdout.write(self.style.SUCCESS('Successfully refresh of DNS flag'))
