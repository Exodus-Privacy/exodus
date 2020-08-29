from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests

from trackers.models import Tracker, TrackerCategory

ETIP_API_DEFAULT_HOSTNAME = settings.ETIP_HOSTNAME
ETIP_API_PATH = '/api/trackers'


class Command(BaseCommand):
    help = 'Import data from ETIP DB'

    def add_arguments(self, parser):
        parser.add_argument(
            '-e',
            '--etip-hostname',
            type=str,
            nargs='?',
            default=ETIP_API_DEFAULT_HOSTNAME,
            help='Hostname of the ETIP instance to query'
        )
        parser.add_argument(
            '-t',
            '--token',
            type=str,
            nargs='?',
            help='Authorization token for ETIP'
        )
        parser.add_argument(
            '-a',
            '--apply',
            action='store_true',
            default=False,
            help='Wether to apply changes'
        )

    def get_trackers_from_etip(self, etip_base_url, auth_token):
        headers = {'Authorization': 'Token {}'.format(auth_token)}
        response = requests.get(etip_base_url + ETIP_API_PATH, headers=headers)
        if response.status_code != 200:
            raise CommandError(
                'Unexpected status from API: {}'.format(response.status_code))

        etip_trackers = response.json()
        if etip_trackers is None or etip_trackers == []:
            raise CommandError('Empty response')

        exodus_trackers = []
        for tracker in etip_trackers:
            if tracker.get('is_in_exodus'):
                exodus_trackers.append(tracker)
        return exodus_trackers

    def compare_trackers(self, etip_trackers, apply):
        exodus_trackers = Tracker.objects.all()
        for etip_tracker in etip_trackers:
            self.stdout.write('* Checking {}'.format(etip_tracker['name']))
            changes = False
            new_tracker = False

            try:
                existing_tracker = exodus_trackers.get(name=etip_tracker['name'])
            except Tracker.DoesNotExist:
                new_tracker = True

            if new_tracker:
                if apply:
                    Tracker.objects.create(
                        name=etip_tracker['name'],
                        code_signature=etip_tracker['code_signature'],
                        network_signature=etip_tracker['network_signature'],
                        website=etip_tracker['website'],
                        description=etip_tracker['description'],
                    )
                    self.stdout.write(self.style.SUCCESS('Tracker created'))
                else:
                    self.stdout.write(self.style.WARNING('Will create new tracker'))
            else:
                if existing_tracker.code_signature != etip_tracker['code_signature']:
                    self.stdout.write(self.style.WARNING("Updating code signature from '{}' to '{}'".format(existing_tracker.code_signature, etip_tracker['code_signature'])))
                    existing_tracker.code_signature = etip_tracker['code_signature']
                    changes = True

                if existing_tracker.network_signature != etip_tracker['network_signature']:
                    self.stdout.write(self.style.WARNING("Updating network signature from '{}' to '{}'".format(existing_tracker.network_signature, etip_tracker['network_signature'])))
                    existing_tracker.network_signature = etip_tracker['network_signature']
                    changes = True

                if existing_tracker.website != etip_tracker['website']:
                    self.stdout.write(self.style.WARNING("Updating website from '{}' to '{}'".format(existing_tracker.website, etip_tracker['website'])))
                    existing_tracker.website = etip_tracker['website']
                    changes = True

                if existing_tracker.description != etip_tracker['description']:
                    self.stdout.write(self.style.WARNING("Updating description from '{}' to '{}'".format(existing_tracker.description, etip_tracker['description'])))
                    existing_tracker.description = etip_tracker['description']
                    changes = True

                existing_categories = [c.name for c in existing_tracker.category.order_by('name')]
                etip_categories = [c.get('name') for c in etip_tracker['category']]
                if existing_categories != etip_categories:
                    self.stdout.write(self.style.WARNING("Updating category from '{}' to '{}'".format(', '.join(existing_categories), ', '.join(etip_categories))))
                    if apply:
                        categories = [TrackerCategory.objects.get(name=c) for c in etip_categories]
                        existing_tracker.category.set(categories)
                    changes = True

                if apply and changes:
                    existing_tracker.save()
                    self.stdout.write(self.style.SUCCESS('Saved changes'))

    def handle(self, *args, **options):
        etip_trackers = self.get_trackers_from_etip(
            options['etip_hostname'], options['token'])
        self.stdout.write(
            'Retrieved {} trackers from ETIP'.format(len(etip_trackers)))

        if not options['apply']:
            self.stdout.write(self.style.WARNING('Running in check mode, will not apply changes'))

        self.compare_trackers(etip_trackers, options['apply'])
