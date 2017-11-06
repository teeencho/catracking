import arrow

from django.test import TestCase

from catracking.models import TrackingRequest


class TrackingRequestTest(TestCase):

    def setUp(self):
        self.tracking_request = TrackingRequest.objects.create(
            tracker='ga', endpoint='/endpoint', payload='?v=1',
            response_code=200, created=arrow.get(2017, 1, 1))

    def test_str(self):
        self.assertEquals('ga - 200', str(self.tracking_request))
