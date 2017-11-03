import requests

from celery.task import Task
from celery.utils.log import get_task_logger

from catracking.models import TrackingRequest

logger = get_task_logger(__name__)


class SendTrackingDataTask(Task):

    def run(self, tracker, endpoint, payload):
        TrackingRequest.objects.create(
            tracker=tracker, endpoint=endpoint, payload=payload,
            response_code=200)
