import tempfile
import os
from django.core.management.base import BaseCommand, CommandError

from exodus.core.static_analysis import StaticAnalysis
from exodus.core.storage import RemoteStorageHelper
from reports.models import Certificate, Report


class Command(BaseCommand):
    help = 'Refresh all APK certificate infos'

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
                raise CommandError('Report not found')

        count = 1
        for report in reports:
            self.stdout.write('%s/%s - Start updating report "%s"' % (count, len(reports), report.id))
            count += 1

            with tempfile.TemporaryDirectory() as tmp_dir:
                apk_name = report.apk_file
                apk_tmp = os.path.join(tmp_dir, apk_name)

                storage_helper = RemoteStorageHelper(report.bucket)

                try:
                    storage_helper.get_file(apk_name, apk_tmp)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING('Unable to get APK: '+str(e)))
                    continue

                static_analysis = StaticAnalysis(apk_path=apk_tmp)

                if report.application.apk.certificate_set.count() == 0:
                    certificates = static_analysis.get_certificates()
                    for certificate in certificates:
                        c = Certificate(apk=report.application.apk)
                        c.issuer = certificate.issuer
                        c.fingerprint = certificate.fingerprint
                        c.subject = certificate.subject
                        c.serial_number = certificate.serial
                        c.save(force_insert=True)
                    self.stdout.write(self.style.SUCCESS('Certificates added'))
                else:
                    self.stdout.write('Certificates already in the DB')
