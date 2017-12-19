import os
import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from exodus.core.static_analysis import *
from minio import Minio
from minio.error import (ResponseError)

from exodus.core.storage import RemoteStorageHelper
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

                storage_helper = RemoteStorageHelper(report.bucket)
                try:
                    storage_helper.get_file(apk_name, apk_tmp)
                except ResponseError:
                    raise CommandError('Unable to get APK')

                # Refresh trackers
                if options['trackers']:
                    # Download class list file
                    static_analysis = StaticAnalysis(None)
                    clist_tmp = os.path.join(tmpdir, report.class_list_file)
                    try:
                        storage_helper.get_file(report.class_list_file, clist_tmp)
                    except ResponseError as err:
                        print(err)
                        raise CommandError('Unable to clist file')
                    trackers = static_analysis.detect_trackers(clist_tmp)
                    print(trackers)
                    report.found_trackers = trackers
                    report.save()
                    self.stdout.write(
                        self.style.SUCCESS('Successfully update trackers list of "%s"' % report.application.handle))

                # Refresh icon
                if options['icons']:
                    icon_path = get_application_icon(storage_helper, icon_name, report.application.handle)
                    if icon_path != '':
                        report.application.icon_path = icon_path
                        report.application.save()
                        self.stdout.write(
                            self.style.SUCCESS('Successfully update icon of "%s"' % report.application.handle))
