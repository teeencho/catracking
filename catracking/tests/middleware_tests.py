import mock

from django.test import (
    TestCase,
    override_settings)

from catracking import middleware


@override_settings(TRACKERS={'ga': {}})
class TrackingMiddlewareTest(TestCase):

    def setUp(self):
        self.middleware = middleware.TrackingMiddleware()

    @override_settings(TRACKERS={})
    def test_trackers_no_trackers(self):
        self.assertEquals(self.middleware.trackers, [])

    def test_trackers_with_trackers(self):
        self.assertEquals(self.middleware.trackers, ['ga'])

    def test_process_view(self):
        request = mock.MagicMock()
        request.trackers = None

        self.middleware.process_view(request, None, None, None)
        self.assertTrue(hasattr(request, 'trackers'))
        self.assertTrue(hasattr(request.trackers, 'ga'))

    @mock.patch('catracking.middleware.GoogleAnalyticsTracker.send')
    def test_process_response(self, p_send):
        request = mock.MagicMock()
        request.trackers = None

        self.middleware.process_view(request, None, None, None)
        self.middleware.process_response(request, None)
        p_send.assert_called_once()
