import logging

from celery import shared_task
from django.conf import settings
from eventlog.events import EventGroup

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

    ev.info('{} code signatures updated.'.format(updated_code_signatures), initiator=__name__)

    ev.info('Tracker list has been updated', initiator=__name__)
