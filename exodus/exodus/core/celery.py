# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from celery import Celery
from django.conf import settings

app = Celery(
    'exodus',
    backend='rpc://',
    include=['exodus.core.apk', 'trackers.tasks', 'analysis_query.tasks', 'reports.tasks'],
    broker=settings.CELERY_BROKER_URL
)

app.conf.beat_schedule = {
    'auto_cleanup_analysis_requests': {
        'task': 'analysis_query.tasks.auto_cleanup_analysis_requests',
        'schedule': settings.ANALYSIS_REQUESTS_AUTO_CLEANUP_TIME
    },
    'calculate_trackers_statistics': {
        'task': 'trackers.tasks.calculate_trackers_statistics',
        'schedule': settings.TRACKERS_STATISTICS_AUTO_UPDATE_TIME
    }
}

if settings.TRACKERS_AUTO_UPDATE:
    app.conf.beat_schedule['auto_update_trackers'] = {
        'task': 'trackers.tasks.auto_update_trackers',
        'schedule': settings.TRACKERS_AUTO_UPDATE_TIME
    }


app.config_from_object('django.conf:settings')
if __name__ == '__main__':
    app.start()
