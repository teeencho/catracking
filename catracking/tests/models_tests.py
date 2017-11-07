import arrow

from django.test import TestCase

from catracking.models import TrackingRequest


class TrackingRequestTest(TestCase):

    def setUp(self):
        self.tracking_request = TrackingRequest.objects.create(
            tracker='ga', endpoint='/endpoint', payload='?v=1',
            response_code=200)
        self.tracking_request.created = arrow.get(2017, 1, 1).datetime

    def test_init(self):
        self.assertEquals('ga', self.tracking_request.tracker)
        self.assertEquals('/endpoint', self.tracking_request.endpoint)
        self.assertEquals('?v=1', self.tracking_request.payload)
        self.assertEquals(200, self.tracking_request.response_code)
        self.assertEquals(
            '2017 01 01',
            arrow.get(self.tracking_request.created).format('YYYY MM DD'))

    def test_str(self):
        self.assertEquals('ga - 200', self.tracking_request.__str__())
