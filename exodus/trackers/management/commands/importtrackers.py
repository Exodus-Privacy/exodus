from django.core.management.base import BaseCommand, CommandError
from trackers.models import Tracker
import json

class Command(BaseCommand):
    help = 'Import trackers from exodus'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            nargs='?',
            default='https://reports.exodus-privacy.eu.org/api/trackers'
        )

    def handle(self, *args, **options):
        if (Tracker.objects.all()[:1].count() > 0):
            raise CommandError('Your trakers table in not empty, please truncate its before the import')

        json_str = self.read_file(options['filename']).decode('utf-8')
        trackers = json.loads(json_str)

        for id, tracker in trackers['trackers'].items():
            model = Tracker(
                id=tracker['id'],
                name=tracker['name'],
                description=tracker['description'],
                creation_date=tracker['creation_date'],
                code_signature=tracker['code_signature'],
                network_signature=tracker['network_signature'],
                website=tracker['website'],
            )

            model.save()

            print('%s saved' % model.name)

    def read_file(self, filename):
        if (filename.find('://') > 0):
            import urllib.request

            file = urllib.request.urlopen(filename)
        else:
            file = open(filename, 'r')

        return file.read()
