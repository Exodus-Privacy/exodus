from django.core.management.base import BaseCommand, CommandError

from reports.tasks import update_fdroid_data


class Command(BaseCommand):
    help = 'Refresh F-Droid data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to download F-Droid index...')
        try:
            update_fdroid_data.apply()
        except Exception:
            raise CommandError('Impossible to update F-Droid data')

        self.stdout.write(self.style.SUCCESS('Command completed, check Event Logs'))
