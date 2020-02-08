import logging

from celery import shared_task
from django.conf import settings
from django.db.models import Max
from eventlog.events import EventGroup

from reports.tasks import recompute_all_reports
from reports.models import Report
from trackers.models import Tracker


logger = logging.getLogger(__name__)


@shared_task
def auto_update_trackers():
    import urllib.request
    import json

    ev = EventGroup()
    ev.info('Starting the update of the tracker list', initiator=__name__)

    if Tracker.objects.all().count() > 0:
        ev.warning('Your trackers table is not empty, changes will be reverted.', initiator=__name__)

    try:
        with urllib.request.urlopen(settings.TRACKERS_AUTO_UPDATE_FROM) as rq:
            content = rq.read()
            trackers = json.loads(content.decode())
    except Exception as e:
        ev.error(e, initiator=__name__)
        return

    updated_code_signatures = 0

    for _, tracker in trackers['trackers'].items():
        obj, created = Tracker.objects.update_or_create(
            id=tracker['id'],
            name=tracker['name'],
            website=tracker['website'],
            defaults={
                'description': tracker['description'],
                'creation_date': tracker['creation_date'],
                'network_signature': tracker['network_signature']
            }
        )
        if obj.code_signature != tracker['code_signature']:
            obj.code_signature = tracker['code_signature']
            obj.save()
            updated_code_signatures += 1

        if created:
            logger.info('Tracker {} has been added.'.format(tracker['name']))
        else:
            logger.info('Tracker {} has been updated.'.format(tracker['name']))

    if updated_code_signatures > 0:
        recompute_all_reports.delay()

    ev.info('{} code signatures updated.'.format(updated_code_signatures), initiator=__name__)

    ev.info('Tracker list has been updated', initiator=__name__)


@shared_task
def calculate_trackers_statistics():
    ev = EventGroup()

    trackers = Tracker.objects.order_by('name')
    application_report_id_map = Report.objects.values('application__handle').annotate(recent_id=Max('id'))
    report_ids = [k['recent_id'] for k in application_report_id_map]

    reports_number = Report.objects.filter(id__in=report_ids).count()

    if trackers.count() == 0 or reports_number == 0:
        ev.info('No tracker to update', initiator=__name__)
        return

    ev.info('Starting update of trackers statistics', initiator=__name__)

    for t in trackers:
        t.apps_number = Report.objects.filter(found_trackers=t.id, id__in=report_ids).count()
        t.apps_percent = int(100. * t.apps_number / reports_number)
        t.save()

    ev.info('Trackers statistics have been updated', initiator=__name__)
