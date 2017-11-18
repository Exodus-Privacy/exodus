from django.core.management.base import BaseCommand, CommandError
from exodus.core.static_analysis import *
from reports.models import *


class Command(BaseCommand):
    help = 'Refresh application icon'

    def add_arguments(self, parser):
        parser.add_argument('report_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for report_id in options['report_id']:
            try:
                report = Report.objects.get(pk=report_id)
            except Report.DoesNotExist:
                raise CommandError('Report %s not found' % report_id)

            icon_name = '%s_%s.png' % (report.bucket, report.application.handle)
            result = getIcon(icon_name, report.application.handle)
            if result != '':
                report.application.icon_path = result
                report.application.save()
                self.stdout.write(self.style.SUCCESS('Successfully update icon for report %s - %s' % (report_id, report.application.handle)))

