from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from exodus.core.static_analysis import *
from reports.models import *
import shutil
import tempfile


class Command(BaseCommand):
    help = 'Refresh all reports'

    def handle(self, *args, **options):
        try:
            reports = Report.objects.order_by('-creation_date')
        except Report.DoesNotExist:
            raise CommandError('No reports found')

        for report in reports:
            tmpdir = tempfile.mkdtemp()
            decoded_dir = os.path.join(tmpdir, 'decoded')
            apk_path = report.application.apk.name
            storage_path = report.storage_path
            # Decode APK
            if decodeAPK(apk_path, decoded_dir):
                # Refresh trackers
                trackers = findTrackers(decoded_dir)
                if len(trackers) > len(report.found_trackers.all()):
                    report.found_trackers = trackers
                    report.save()
                    self.stdout.write(self.style.SUCCESS('Successfully update trackers list of "%s"' % report.application.handle))
                # Refresh icon
                icon_path = getIcon(decoded_dir, storage_path, apk_path)
                if icon_path != '':
                    report.application.icon_path = os.path.relpath(icon_path, settings.EX_FS_ROOT)
                    report.application.save()
                    self.stdout.write(self.style.SUCCESS('Successfully update icon of "%s"' % report.application.handle))

            shutil.rmtree(tmpdir, ignore_errors=True)

            
