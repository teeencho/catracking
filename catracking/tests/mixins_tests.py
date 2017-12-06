import mock

from django.test import TestCase

from catracking.mixins import MiddlewareMixin


class MiddlewareMixinTest(TestCase):

    def setUp(self):
        self.middleware_class = MiddlewareMixin
        self.middleware = self.middleware_class()

    def test_init_no_get_response(self):
        self.assertIsNone(self.middleware.get_response)

    def test_init_get_response(self):
        get_response = mock.MagicMock()
        self.middleware = self.middleware_class(get_response)
        self.assertEquals(self.middleware.get_response, get_response)

    def test_call_with_process_request(self):
        process_request = mock.MagicMock()
        request = mock.MagicMock()
        expected_response = mock.MagicMock()

        setattr(self.middleware, 'process_request', process_request)
        process_request.return_value = expected_response
        response = self.middleware(request)
        self.assertEquals(expected_response, response)

    def test_call_without_process_request(self):
        get_response = mock.MagicMock()
        request = mock.MagicMock()
        expected_response = mock.MagicMock()
        get_response.return_value = expected_response

        self.middleware = self.middleware_class(get_response)
        response = self.middleware(request)
        self.assertEquals(expected_response, response)

    def test_call_with_process_response(self):
        request = mock.MagicMock()
        expected_response = mock.MagicMock()
        get_response = mock.MagicMock()
        get_response.return_value = expected_response
        process_response = mock.MagicMock()
        process_response.return_value = expected_response
        setattr(self.middleware, 'process_response', process_response)

        self.middleware = self.middleware_class(get_response)
        response = self.middleware(request)
        self.assertEquals(expected_response, response)

    def test_call_with_process_request_and_process_response(self):
        request = mock.MagicMock()
        expected_response = mock.MagicMock()
        process_request = mock.MagicMock()
        process_request.return_value = expected_response
        process_response = mock.MagicMock()
        process_response.return_value = expected_response
        setattr(self.middleware, 'process_request', process_request)
        setattr(self.middleware, 'process_response', process_response)

        response = self.middleware(request)
        self.assertEquals(expected_response, response)
