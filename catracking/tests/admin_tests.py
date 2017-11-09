import arrow

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

    def test_get_queryset(self):
        mommy.make('catracking.TrackingRequest')
        mommy.make('catracking.TrackingRequest')
        mommy.make('catracking.TrackingRequest')
        past_5_hours_tr = mommy.make('catracking.TrackingRequest')
        past_5_hours_tr2 = mommy.make('catracking.TrackingRequest')
        past_5_hours_tr.created = arrow.utcnow().shift(
            hours=-5, minutes=-1).datetime
        past_5_hours_tr2.created = arrow.utcnow().shift(hours=-6).datetime
        past_5_hours_tr.save()
        past_5_hours_tr2.save()

        self.assertEquals(4, len(self.admin.get_queryset(None)))

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
