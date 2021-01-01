from django.core.management.base import BaseCommand

from trackers.models import TrackerCategory


class Command(BaseCommand):
    help = 'Import tracker categories'

    def handle(self, *args, **options):

        category_names = [
            'Crash reporting',
            'Analytics',
            'Profiling',
            'Identification',
            'Advertisement',
            'Location',
        ]

        existing_categories = TrackerCategory.objects.all()
        for name in category_names:
            if not existing_categories.filter(name=name):
                cat = TrackerCategory(name=name)
                cat.save()
                self.stdout.write('Category {} created'.format(name))
        self.stdout.write('Tracker categories imported')
