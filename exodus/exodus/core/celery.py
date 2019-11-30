# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from celery import Celery
from django.conf import settings

app = Celery(
    'exodus',
    backend='rpc://',
    include=['exodus.core.apk', 'trackers.tasks'],
    broker=settings.CELERY_BROKER_URL
)

app.conf.beat_schedule = {}

if settings.TRACKERS_AUTO_UPDATE:
    app.conf.beat_schedule['auto_update_trackers'] = {
        'task': 'trackers.tasks.auto_update_trackers',
        'schedule': settings.TRACKERS_AUTO_UPDATE_TIME
    }


app.config_from_object('django.conf:settings')
if __name__ == '__main__':
    app.start()
