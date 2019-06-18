from django.core.management.base import BaseCommand, CommandError

from exodus_core.analysis.static_analysis import get_details_from_gplaycli
from reports.models import Report


class Command(BaseCommand):
    help = 'Refresh application informations'

    def handle(self, *args, **options):
        try:
            reports = Report.objects.order_by('-creation_date')
        except Report.DoesNotExist:
            raise CommandError('No reports found')

        for report in reports:
            handle = report.application.handle
            infos = get_details_from_gplaycli(handle)
            if infos is not None:
                report.application.name = infos.get('title')
                report.application.creator = infos.get('author')
                report.application.downloads = infos.get('numDownloads')
                report.application.save()
                self.stdout.write(self.style.SUCCESS('Successfully update for "%s"' % handle))
