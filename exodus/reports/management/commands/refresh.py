from django.core.management.base import BaseCommand, CommandError
from .models import Reports

class Command(BaseCommand):
    help = 'Refresh all reports'

    def handle(self, *args, **options):
        pass