import tempfile
import os
from django.core.management.base import BaseCommand, CommandError

from exodus.core.static_analysis import *
from exodus.core.storage import RemoteStorageHelper
from reports.models import *


class Command(BaseCommand):
    help = 'Refresh all APK signatures'

    def add_arguments(self, parser):
        parser.add_argument('report_id', nargs = '*', type = int)

        parser.add_argument(
            '--all',
            action = 'store_true',
            dest = 'all',
            help = 'Update all reports',
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

        count = 1
        for report in reports:
            self.stdout.write(
                self.style.SUCCESS('Start updating report "%s" - %s/%s' % (report.id, count, len(reports))))
            count += 1
            with tempfile.TemporaryDirectory() as tmp_dir:
                icon_name = '%s_%s.png' % (report.bucket, report.application.handle)
                apk_name = report.apk_file
                apk_tmp = os.path.join(tmp_dir, apk_name)

                storage_helper = RemoteStorageHelper(report.bucket)

                # Refresh signature
                try:
                    storage_helper.get_file(apk_name, apk_tmp)
                except ResponseError:
                    raise CommandError('Unable to get APK')
                static_analysis = StaticAnalysis(apk_path = apk_tmp)
                icon_path = static_analysis.get_application_icon(storage_helper, icon_name)
                if icon_path != '':
                    report.application.icon_path = icon_path
                    report.application.save()
                    self.stdout.write(self.style.SUCCESS('Successfully updated icon'))
                report.application.app_uid = static_analysis.get_application_universal_id()
                report.application.icon_phash = static_analysis.get_icon_phash()
                report.application.save()
                if report.application.apk.certificate_set.count() == 0:
                    certificates = static_analysis.get_certificates()
                    for certificate in certificates:
                        c = Certificate(apk = report.application.apk)
                        c.issuer = certificate.issuer
                        c.fingerprint = certificate.fingerprint
                        c.subject = certificate.subject
                        c.serial_number = certificate.serial
                        c.save(force_insert = True)

