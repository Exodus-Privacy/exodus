import logging
from datetime import date, timedelta

from celery import shared_task
from django.conf import settings
from eventlog.events import EventGroup

from analysis_query.models import AnalysisRequest

logger = logging.getLogger(__name__)


@shared_task
def auto_cleanup_analysis_requests():
    ev = EventGroup()
    ev.info('Starting the the cleanup of analysis requests', initiator=__name__)

    end_date = date.today() - timedelta(days=settings.ANALYSIS_REQUESTS_KEEP_DURATION)
    ev.info('Delete analysis requests issued before {}'.format(end_date), initiator=__name__)
    requests = AnalysisRequest.objects.filter(uploaded_at__lte=end_date)
    count = requests.count()
    requests.delete()
    ev.info('{} analysis requests deleted'.format(count), initiator=__name__)
