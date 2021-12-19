import logging
import os
import tempfile
import zipfile

import requests
from celery import shared_task
from django.conf import settings
from eventlog.events import EventGroup

from exodus.core.static_analysis import StaticAnalysis
from exodus.core.storage import RemoteStorageHelper
from reports.models import Report

logger = logging.getLogger(__name__)


@shared_task
def recompute_all_reports():
    ev = EventGroup()
    ev.info('Starting the update of all reports', initiator=__name__)

    try:
        reports = Report.objects.order_by('-creation_date')
    except Report.DoesNotExist:
        ev.error('No reports found', initiator=__name__)
        return

    count = 1
    for report in reports:
        ev.info('Start updating report "%s" - %s/%s' % (report.id, count, len(reports)), initiator=__name__)
        try:
            handle = report.application.handle
        except Exception as e:
            ev.error(e, initiator=__name__)
            continue

        count += 1
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_helper = RemoteStorageHelper(report.bucket)

            # Refresh trackers
            # Download class list file
            static_analysis = StaticAnalysis(None)
            clist_tmp = os.path.join(tmpdir, report.class_list_file)
            try:
                storage_helper.get_file(report.class_list_file, clist_tmp)
            except Exception:
                ev.error('Unable to get clist file', initiator=__name__)
                continue

            trackers = static_analysis.detect_trackers(clist_tmp)
            if report.found_trackers.count() != len(trackers):
                ev.warning('previous: %s - new: %s trackers' % (report.found_trackers.count(), len(trackers)),
                           initiator=__name__)
            report.found_trackers.set(trackers)
            report.save()
            ev.info('Successfully updated trackers list of "{}"'.format(handle), initiator=__name__)


@shared_task
def update_fdroid_data():
    ev = EventGroup()
    ev.info('Downloading F-Droid index', initiator=__name__)

    with tempfile.NamedTemporaryFile() as f:
        try:
            r = requests.get('{}/index.xml'.format(settings.FDROID_MIRROR))
            open(f.name, 'wb').write(r.content)

            storage_helper = RemoteStorageHelper()
            storage_helper.put_file(f.name, 'fdroid_index.xml')

            ev.info('Update of F-Droid index complete', initiator=__name__)
        except Exception as e:
            ev.error('Error while downloading Fdroid index', initiator=__name__)
            ev.error(str(e), initiator=__name__)

    ev.info('Downloading F-Droid localized metadata', initiator=__name__)

    with tempfile.NamedTemporaryFile() as f:
        try:
            r = requests.get('{}/index-v1.jar'.format(settings.FDROID_MIRROR))
            open(f.name, 'wb').write(r.content)

            zip_file = zipfile.ZipFile(f.name)
            zip_file.extract('index-v1.json', '/tmp')

            storage_helper = RemoteStorageHelper()
            storage_helper.put_file('/tmp/index-v1.json', 'fdroid_index_v1.json')

            ev.info('Update of F-Droid localized metadata complete', initiator=__name__)
        except Exception as e:
            ev.error('Error while downloading Fdroid localized metadata', initiator=__name__)
            ev.error(str(e), initiator=__name__)
