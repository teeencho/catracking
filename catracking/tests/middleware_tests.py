import mock

from django.conf import settings
from django.test import (
    TestCase,
    override_settings)

from catracking import middleware
from catracking.ga.core import GoogleAnalyticsTracker
from catracking.mixins import MiddlewareMixin


class CustomTracker(GoogleAnalyticsTracker):
    pass


@override_settings(TRACKERS={'ga': {}})
class TrackingMiddlewareTest(TestCase):

    CUSTOM_TRACKER_IMPORT_ERROR = {
        'CUSTOM_TRACKER': 'catracking.tests.middleware_tests.InvalidTracker'
    }

    CUSTOM_TRACKER_VALID = {
        'CUSTOM_TRACKER': 'catracking.tests.middleware_tests.CustomTracker'
    }

    def setUp(self):
        self.middleware = middleware.TrackingMiddleware()

    def test_attrs(self):
        self.assertIsInstance(self.middleware, MiddlewareMixin)

    def test_trackers_no_trackers_object(self):
        with self.settings():
            del settings.TRACKERS
            self.assertEquals(self.middleware.trackers, [])

    @override_settings(TRACKERS={})
    def test_trackers_no_trackers(self):
        self.assertEquals(self.middleware.trackers, [])

    def test_trackers_with_trackers(self):
        self.assertEquals(self.middleware.trackers, ['ga'])

    def test_resolve_tracker_no_custom_tracker(self):
        self.assertEquals(
            GoogleAnalyticsTracker,
            self.middleware.resolve_tracker(GoogleAnalyticsTracker))

    @override_settings(TRACKERS={'ga': CUSTOM_TRACKER_IMPORT_ERROR})
    def test_resolve_tracker_with_custom_tracker_import_error(self):
        self.assertEquals(
            GoogleAnalyticsTracker,
            self.middleware.resolve_tracker(GoogleAnalyticsTracker))

    @override_settings(TRACKERS={'ga': CUSTOM_TRACKER_VALID})
    def test_resolve_tracker_with_custom_tracker(self):
        self.assertEquals(
            CustomTracker,
            self.middleware.resolve_tracker(GoogleAnalyticsTracker))

    def test_process_view(self):
        request = mock.MagicMock()
        request.trackers = None

        self.middleware.process_view(request, None, None, None)
        self.assertTrue(hasattr(request, 'trackers'))
        self.assertTrue(hasattr(request.trackers, 'ga'))

    @mock.patch('catracking.middleware.GoogleAnalyticsTracker.send')
    def test_process_response(self, p_send):
        request = mock.MagicMock()
        response = mock.MagicMock()
        self.middleware.process_view(request, None, None, None)
        self.assertEquals(
            response,
            self.middleware.process_response(request, response))
        p_send.assert_called_once()

    @mock.patch('catracking.middleware.GoogleAnalyticsTracker.send')
    def test_process_response_request_no_trackers(self, p_send):
        request = None
        response = mock.MagicMock()
        self.assertEquals(
            response,
            self.middleware.process_response(request, response))
        p_send.assert_not_called()
