import mock

from django.test import TestCase

from catracking.core import Tracker
from catracking.models import TrackingRequest
from catracking.tasks import SendTrackingDataTask


class SendTrackingDataTaskTest(TestCase):

    class MyTracker(Tracker):
        IDENT = 'mytracker'
        ENDPOINT = '/endpoint'

        def __init__(self):
            pass

        def send(self):
            pass

    def setUp(self):
        self.task = SendTrackingDataTask()
        self.task.tracker_ident = self.MyTracker.IDENT
        self.task.endpoint = self.MyTracker.ENDPOINT
        self.task.payload = 'p'
        self.task.response = mock.MagicMock()
        self.task.response.status_code = 200

    def test_extra(self):
        self.assertEquals(
            {'tracker': 'mytracker', 'endpoint': '/endpoint', 'payload': 'p'},
            self.task.extra)

    @mock.patch('catracking.tasks.logger.error')
    def test_on_failure(self, p_error):
        self.task.on_failure(None, None, (), {}, None)
        p_error.assert_called_once_with(
            'General failure sending tracking data',
            extra=self.task.extra)

    def test_create_tracking_request_log(self):
        self.task.create_tracking_request_log()
        tracking_request = TrackingRequest.objects.last()
        self.assertEquals(self.MyTracker.IDENT, tracking_request.tracker)
        self.assertEquals(self.MyTracker.ENDPOINT, tracking_request.endpoint)
        self.assertEquals('p', tracking_request.payload)
        self.assertEquals(200, tracking_request.response_code)

    @mock.patch('catracking.tasks.logger.error')
    def test_check_response_more_than_299(self, p_error):
        self.task.response.status_code = 300
        self.task.check_response()
        p_error.assert_called_once_with(
            'Bad response status from tracker',
            extra=self.task.extra)

    @mock.patch('catracking.tasks.logger.error')
    def test_check_response_less_than_200(self, p_error):
        self.task.response.status_code = 199
        self.task.check_response()
        p_error.assert_called_once_with(
            'Bad response status from tracker',
            extra=self.task.extra)

    @mock.patch('catracking.tasks.logger.error')
    def test_check_response_between_200_and_199(self, p_error):
        self.task.response.status_code = 250
        self.task.check_response()
        p_error.assert_not_called()

    @mock.patch('requests.post')
    def test_run(self, p_post):
        response = mock.MagicMock()
        response.status_code = 200
        p_post.return_value = response
        self.task.run(self.MyTracker.IDENT, self.MyTracker.ENDPOINT, 'p')
        p_post.assert_called_once_with(
            self.MyTracker.ENDPOINT, data='p')

    @mock.patch('requests.post')
    @mock.patch('catracking.tasks.logger.error')
    def test_run_bad_response(self, p_error, p_post):
        response = mock.MagicMock()
        response.status_code = 300
        p_post.return_value = response
        self.task.run(self.MyTracker.IDENT, self.MyTracker.ENDPOINT, 'p')
        p_post.assert_called_once_with(
            self.MyTracker.ENDPOINT, data='p')
        p_error.assert_called_once_with(
            'Bad response status from tracker',
            extra=self.task.extra)
