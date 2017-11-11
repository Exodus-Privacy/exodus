from django.core.management.base import BaseCommand, CommandError
from exodus.core.static_analysis import *
from exodus.core.dns import *


class Command(BaseCommand):
    help = 'Refresh DNS tracking flag'

    def handle(self, *args, **options):
        refresh_dns()
        self.stdout.write(self.style.SUCCESS('Successfully refresh of DNS flag'))