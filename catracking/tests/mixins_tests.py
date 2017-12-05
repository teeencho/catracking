import mock

from django.test import TestCase

from catracking.mixins import MiddlewareMixin


class MiddlewareMixinTest(TestCase):

    def setUp(self):
        self.middleware_class = MiddlewareMixin

    def test_init_no_get_response(self):
        middleware = self.middleware_class()
        self.assertIsNone(middleware.get_response)

    def test_init_get_response(self):
        get_response = mock.MagicMock()
        middleware = self.middleware_class(get_response)
        self.assertEquals(middleware.get_response, get_response)
