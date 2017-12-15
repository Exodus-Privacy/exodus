from django.core.management.base import BaseCommand
from exodus.core.dns import *
from exodus.core.static_analysis import *


class Command(BaseCommand):
    help = 'Refresh DNS tracking flag'

    def handle(self, *args, **options):
        refresh_dns()
        self.stdout.write(self.style.SUCCESS('Successfully refresh of DNS flag'))
