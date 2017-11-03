import requests

from celery.task import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class SendTrackingDataTask(Task):

    def run(self, endpoint, payload):
        pass
