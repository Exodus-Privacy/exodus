import os
import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from exodus.core.static_analysis import *
from minio import Minio
from minio.error import (ResponseError)
from reports.models import *


class Command(BaseCommand):
    help = 'Refresh all reports'

    def add_arguments(self, parser):
        parser.add_argument('report_id', nargs = '*', type = int)

        parser.add_argument(
            '--all',
            action = 'store_true',
            dest = 'all',
            help = 'Update all reports',
        )

        parser.add_argument(
            '--icons',
            action = 'store_true',
            dest = 'icons',
            help = 'Update icons',
        )

        parser.add_argument(
            '--trackers',
            action = 'store_true',
            dest = 'trackers',
            help = 'Update found trackers',
        )

        parser.add_argument(
            '--versions',
            action = 'store_true',
            dest = 'versions',
            help = 'Update application version code',
        )

    def handle(self, *args, **options):
        if options['all']:
            try:
                reports = Report.objects.order_by('-creation_date')
            except Report.DoesNotExist:
                raise CommandError('No reports found')
        else:
            try:
                reports = Report.objects.filter(pk__in = options['report_id'])
            except Report.DoesNotExist:
                raise CommandError('No reports found')

        for report in reports:
            self.stdout.write(self.style.SUCCESS('Start updating report "%s"' % report.id))
            with tempfile.TemporaryDirectory() as tmpdir:
                decoded_dir = os.path.join(tmpdir, 'decoded')
                icon_name = '%s_%s.png' % (report.bucket, report.application.handle)
                apk_name = report.apk_file
                apk_tmp = os.path.join(tmpdir, apk_name)

                # Download APK from storage
                minio_client = Minio(settings.MINIO_URL,
                                     access_key = settings.MINIO_ACCESS_KEY,
                                     secret_key = settings.MINIO_SECRET_KEY,
                                     secure = settings.MINIO_SECURE)
                try:
                    data = minio_client.get_object(settings.MINIO_BUCKET, apk_name)
                    with open(apk_tmp, 'wb') as file_data:
                        for d in data.stream(32 * 1024):
                            file_data.write(d)
                except ResponseError:
                    raise CommandError('Unable to get APK')

                # Refresh trackers
                if options['trackers']:
                    # Check if classes list has already been generated
                    if len(report.class_list_file) == 0:
                        # Decode APK
                        if decode_apk_file(apk_tmp, decoded_dir):
                            class_list_file = '%s_%s.clist' % (report.bucket, report.application.handle)
                            if list_embedded_classes(decoded_dir, class_list_file) != '':
                                report.class_list_file = class_list_file
                                report.save()

                    # Download class list file
                    minio_client = Minio(settings.MINIO_URL,
                                         access_key = settings.MINIO_ACCESS_KEY,
                                         secret_key = settings.MINIO_SECRET_KEY,
                                         secure = settings.MINIO_SECURE)
                    clist_tmp = os.path.join(tmpdir, report.class_list_file)
                    try:
                        data = minio_client.get_object(settings.MINIO_BUCKET, report.class_list_file)
                        with open(clist_tmp, 'wb') as file_data:
                            for d in data.stream(32 * 1024):
                                file_data.write(d)
                    except ResponseError as err:
                        print(err)
                        raise CommandError('Unable to clist file')
                    trackers = find_embedded_trackers(clist_tmp)
                    print(trackers)
                    report.found_trackers = trackers
                    report.save()
                    self.stdout.write(
                        self.style.SUCCESS('Successfully update trackers list of "%s"' % report.application.handle))

                # Get version code if missing
                if len(report.application.version_code) == 0 or options['versions']:
                    # Decode APK
                    if decode_apk_file(apk_tmp, decoded_dir):
                        report.application.version_code = get_application_version_code(decoded_dir)
                        report.application.save()
                        self.stdout.write(
                            self.style.SUCCESS('Successfully update version of "%s"' % report.application.handle))

                # Refresh icon
                if options['icons']:
                    icon_path = get_application_icon(icon_name, report.application.handle)
                    if icon_path != '':
                        report.application.icon_path = icon_path
                        report.application.save()
                        self.stdout.write(
                            self.style.SUCCESS('Successfully update icon of "%s"' % report.application.handle))
