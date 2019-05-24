import tempfile
import os
from django.core.management.base import BaseCommand, CommandError

from exodus.core.static_analysis import *
from exodus.core.storage import RemoteStorageHelper
from reports.models import *


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

        parser.add_argument(
            '--icons',
            action='store_true',
            dest='icons',
            help='Update icons',
        )

        parser.add_argument(
            '--trackers',
            action='store_true',
            dest='trackers',
            help='Update found trackers',
        )

        parser.add_argument(
            '--clist',
            action='store_true',
            dest='clist',
            help='Update clist file',
        )

    def handle(self, *args, **options):
        if options['all']:
            try:
                reports = Report.objects.order_by('-creation_date')
            except Report.DoesNotExist:
                raise CommandError('No reports found')
        elif options['report_id']:
            try:
                reports = Report.objects.filter(pk__in=options['report_id'])
            except Report.DoesNotExist:
                raise CommandError('No reports found')
        else:
            raise CommandError('Please specify a report id or --all option')

        count = 1
        for report in reports:
            self.stdout.write('Start updating report "%s" - %s/%s' % (report.id, count, len(reports)))

            # report.application could fail with malformed reports
            try:
                handle = report.application.handle
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                continue

            count += 1
            with tempfile.TemporaryDirectory() as tmpdir:
                icon_name = '%s_%s.png' % (report.bucket, handle)
                apk_name = report.apk_file
                apk_tmp = os.path.join(tmpdir, apk_name)

                storage_helper = RemoteStorageHelper(report.bucket)

                # Refresh clist
                if options['clist']:
                    try:
                        storage_helper.get_file(apk_name, apk_tmp)
                    except ResponseError:
                        raise CommandError('Unable to get APK')
                    static_analysis = StaticAnalysis(apk_path=apk_tmp)
                    with tempfile.NamedTemporaryFile(delete=True) as fp:
                        static_analysis.save_embedded_classes_in_file(fp.name)
                        storage_helper.put_file(fp.name, report.class_list_file)
                    self.stdout.write(
                        self.style.SUCCESS('Successfully updated classes list of "%s"' % handle))

                # Refresh trackers
                if options['trackers']:
                    # Download class list file
                    static_analysis = StaticAnalysis(None)
                    clist_tmp = os.path.join(tmpdir, report.class_list_file)
                    try:
                        storage_helper.get_file(report.class_list_file, clist_tmp)
                    except ResponseError as err:
                        raise CommandError('Unable to clist file')
                    trackers = static_analysis.detect_trackers(clist_tmp)
                    self.stdout.write(
                        self.style.WARNING(
                            'previous: %s - new: %s trackers' % (report.found_trackers.count(), len(trackers))))
                    report.found_trackers = trackers
                    report.save()
                    self.stdout.write(
                        self.style.SUCCESS('Successfully updated trackers list of "%s"' % handle))

                # Refresh icon
                if options['icons']:
                    try:
                        storage_helper.get_file(apk_name, apk_tmp)
                    except ResponseError:
                        raise CommandError('Unable to get APK')
                    static_analysis = StaticAnalysis(apk_path=apk_tmp)
                    icon_path = static_analysis.get_application_icon(storage_helper, icon_name)
                    if icon_path != '':
                        report.application.icon_path = icon_path
                        report.application.save()
                        self.stdout.write(
                            self.style.SUCCESS('Successfully updated icon of "%s"' % report.application.handle))
