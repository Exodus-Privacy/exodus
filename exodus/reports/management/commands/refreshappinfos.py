from django.core.management.base import BaseCommand, CommandError
from exodus.core.static_analysis import *
from reports.models import *

class Command(BaseCommand):
    help = 'Refresh application informations'

    def handle(self, *args, **options):
        try:
            reports = Report.objects.order_by('-creation_date')
        except Report.DoesNotExist:
            raise CommandError('No reports found')

        for report in reports:
            handle = report.application.handle
            infos = getApplicationInfos(handle)
            if infos is not None:
                report.application.name = infos['title']
                report.application.creator = infos['creator']
                report.application.downloads = infos['downloads']
                report.application.save()
                self.stdout.write(self.style.SUCCESS('Successfully update for "%s"' % handle))