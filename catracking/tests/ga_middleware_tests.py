import arrow
import mock

from django.test import (
    TestCase,
    override_settings)

from catracking.ga.middleware import GoogleAnalyticsCookieMiddleware
from catracking.mixins import MiddlewareMixin


class GoogleAnalyticsCookieMiddlewareTest(TestCase):

    def setUp(self):
        self.middleware = GoogleAnalyticsCookieMiddleware()
        self.request = mock.MagicMock()
        self.request.COOKIES = {}
        self.request.session = {}

    def test_attrs(self):
        self.assertIsInstance(self.middleware, MiddlewareMixin)

    @mock.patch(
        'catracking.ga.core.GoogleAnalyticsTracker.generate_ga_cookie')
    def test_process_request_cookie_not_in_request(self, p_generate_ga_cookie):
        self.middleware.process_request(self.request)
        p_generate_ga_cookie.assert_called_once()
        self.assertIn('ga_cookie', self.request.session)

    @mock.patch(
        'catracking.ga.core.GoogleAnalyticsTracker.generate_ga_cookie')
    def test_process_request_cookie_in_request(self, p_generate_ga_cookie):
        self.request.COOKIES['_ga2017'] = 'GA1.2.12345.12345'
        self.middleware.process_request(self.request)
        p_generate_ga_cookie.assert_not_called()
        self.assertNotIn('ga_cookie', self.request.session)

    @override_settings(TRACKERS={'ga': {'COOKIE_DOMAIN': '.ca.com'}})
    @mock.patch('arrow.utcnow')
    def test_process_response_cookie_in_session(self, p_utcnow):
        date_2017_1_1 = arrow.get(2017, 1, 1)
        date_2019_1_1 = arrow.get(2019, 1, 1)
        p_utcnow.return_value = date_2017_1_1
        self.request.session['ga_cookie'] = 'GA1.2.12345.12345'
        response = mock.MagicMock()
        with mock.patch.object(response, 'set_cookie') as p_set_cookie:
            self.middleware.process_response(self.request, response)
            p_set_cookie.assert_called_once_with(
                '_ga2017', 'GA1.2.12345.12345', domain='.ca.com',
                expires=date_2019_1_1.datetime)

    def test_process_response_cookie_not_in_session(self):
        self.request.session = {}
        response = mock.MagicMock()
        with mock.patch.object(response, 'set_cookie') as p_set_cookie:
            self.middleware.process_response(self.request, response)
            p_set_cookie.assert_not_called()
