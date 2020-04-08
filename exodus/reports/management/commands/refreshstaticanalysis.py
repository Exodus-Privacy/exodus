import tempfile
import os
from django.core.management.base import BaseCommand, CommandError
from minio.error import ResponseError, NoSuchKey

from exodus.core.static_analysis import StaticAnalysis
from exodus.core.storage import RemoteStorageHelper
from reports.models import Report


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

        trackers_changed = 0
        count = 1
        for report in reports:
            self.stdout.write('Start updating report "{}" - {}/{}'.format(report.id, count, len(reports)))

            # report.application could fail with malformed reports
            try:
                handle = report.application.handle
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                continue

            count += 1
            with tempfile.TemporaryDirectory() as tmpdir:
                storage_helper = RemoteStorageHelper(report.bucket)

                if options['clist'] or options['icons']:
                    apk_name = report.apk_file
                    apk_tmp = os.path.join(tmpdir, apk_name)
                    try:
                        storage_helper.get_file(apk_name, apk_tmp)
                    except ResponseError:
                        raise CommandError('Unable to get APK')
                    static_analysis = StaticAnalysis(apk_path=apk_tmp)

                    if options['clist']:
                        with tempfile.NamedTemporaryFile(delete=True) as fp:
                            static_analysis.save_embedded_classes_in_file(fp.name)
                            storage_helper.put_file(fp.name, report.class_list_file)
                        self.stdout.write(
                            self.style.SUCCESS('Successfully updated classes list of "{}"'.format(handle)))

                    if options['icons']:
                        icon_name = '{}_{}.png'.format(report.bucket, handle)
                        icon_path, _ = static_analysis.get_icon_and_phash(storage_helper, icon_name)
                        if icon_path != '':
                            report.application.icon_path = icon_path
                            report.application.save()
                            self.stdout.write(
                                self.style.SUCCESS('Successfully updated icon of "{}"'.format(handle)))

                if options['trackers']:
                    # Download class list file
                    static_analysis = StaticAnalysis(None)
                    clist_tmp = os.path.join(tmpdir, report.class_list_file)
                    try:
                        storage_helper.get_file(report.class_list_file, clist_tmp)
                    except (ResponseError, NoSuchKey):
                        raise CommandError('Unable to get clist file')

                    trackers = static_analysis.detect_trackers(clist_tmp)
                    if report.found_trackers.count() != len(trackers):
                        trackers_changed += 1
                        self.stdout.write(
                            self.style.WARNING(
                                'Previous: {} - New: {} trackers'.format(report.found_trackers.count(), len(trackers))))
                    report.found_trackers.set(trackers)
                    report.save()
                    self.stdout.write(
                        self.style.SUCCESS('Successfully updated trackers list of "{}"'.format(handle)))

            self.stdout.write('=====')

        self.stdout.write(self.style.SUCCESS('Update complete !'))
        if options['trackers']:
            self.stdout.write('Reports updated (trackers): {}'.format(trackers_changed))
