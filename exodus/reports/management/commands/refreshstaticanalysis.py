from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from exodus.core.static_analysis import *
from reports.models import *
import shutil, os
import tempfile
from minio import Minio
from minio.error import (ResponseError)


class Command(BaseCommand):
    help = 'Refresh all reports'

    def add_arguments(self, parser):
        parser.add_argument('report_id', nargs='*', type=int)

        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='Update all reports',
        )

    def handle(self, *args, **options):
        if options['all']:
            try:
                reports = Report.objects.order_by('-creation_date')
            except Report.DoesNotExist:
                raise CommandError('No reports found')
        else:
            try:
                reports = Report.objects.filter(pk__in=options['report_id'])
            except Report.DoesNotExist:
                raise CommandError('No reports found')

        for report in reports:
            self.stdout.write(
                self.style.SUCCESS('Start updating report "%s"' % report.id))
            tmpdir = tempfile.mkdtemp()
            decoded_dir = os.path.join(tmpdir, 'decoded')
            icon_name = '%s_%s.png' % (report.bucket, report.application.handle)
            apk_name = report.apk_file
            apk_tmp = os.path.join(tmpdir, apk_name)

            # Download APK from storage
            minio_client = Minio(settings.MINIO_URL,
                         access_key=settings.MINIO_ACCESS_KEY,
                         secret_key=settings.MINIO_SECRET_KEY,
                         secure=settings.MINIO_SECURE)
            try:
                data = minio_client.get_object(settings.MINIO_BUCKET, apk_name)
                with open(apk_tmp, 'wb') as file_data:
                    for d in data.stream(32 * 1024):
                        file_data.write(d)
            except ResponseError as err:
                print(err)
            # Decode APK
            if decodeAPK(apk_tmp, decoded_dir):
                # Refresh trackers
                trackers = findTrackers(decoded_dir)
                if len(trackers) > len(report.found_trackers.all()):
                    report.found_trackers = trackers
                    report.save()
                    self.stdout.write(self.style.SUCCESS('Successfully update trackers list of "%s"' % report.application.handle))
                # Refresh icon
                icon_path = getIcon(icon_name, report.application.handle)
                if icon_path != '':
                    report.application.icon_path = icon_path
                    report.application.save()
                    self.stdout.write(self.style.SUCCESS('Successfully update icon of "%s"' % report.application.handle))

            shutil.rmtree(tmpdir, ignore_errors=True)

