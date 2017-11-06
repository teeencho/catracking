import requests

from celery.task import Task
from celery.utils.log import get_task_logger

from catracking.models import TrackingRequest

logger = get_task_logger(__name__)


class SendTrackingDataTask(Task):
    """
    Sends the tracking data to the tracker endpoint.

    Sentry errors will be thrown in case any exception is raised or if
    the response status code is bad.

    A log object will be created containing information about the tracker, its
    endpoint and the payload. Those should be checked to verify if the
    tracking data is being sent correctly.
    """

    @property
    def extra(self):
        return {
            'tracker': self.tracker_ident,
            'endpoint': self.endpoint,
            'payload': self.payload
        }

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error('General failure sending tracking data', extra=self.extra)

    def create_tracking_request_log(self):
        TrackingRequest.objects.create(
            tracker=self.tracker_ident, endpoint=self.endpoint,
            payload=self.payload, response_code=self.response.status_code)

    def check_response(self):
        if not (200 <= self.response.status_code < 300):
            logger.error('Bad response status from tracker', extra=self.extra)

    def run(self, tracker_ident, endpoint, payload):
        self.tracker_ident = tracker_ident
        self.endpoint = endpoint
        self.payload = payload

        self.response = requests.post(endpoint, data=payload)
        self.create_tracking_request_log()
        self.check_response()
