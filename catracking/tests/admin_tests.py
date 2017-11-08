from model_mommy import mommy

from django.test import TestCase

from catracking import admin
from catracking import models


class TrackingRequestAdminTest(TestCase):

    def setUp(self):
        self.admin = admin.TrackingRequestAdmin(models.TrackingRequest, None)
        self.tracking_request = mommy.make(
            'catracking.TrackingRequest', tracker='ga',
            payload='t=event&ec=c&ea=a&el=l')

    def test_payloadify_ga_event(self):
        self.assertEquals(
            'event (c, a, l)',
            self.admin.payloadify(self.tracking_request))

    def test_payloadify_ga_no_event(self):
        self.tracking_request.payload = 't=pageview'
        self.assertEquals('', self.admin.payloadify(self.tracking_request))

    def test_payloadify_non_ga(self):
        self.tracking_request.tracker = 'somethingelse'
        self.assertEquals('', self.admin.payloadify(self.tracking_request))
