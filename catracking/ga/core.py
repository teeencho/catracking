import catracking.ga.parameters as parameters
import random
import time
import uuid

from collections import OrderedDict
from urllib import urlencode

from django.utils.functional import cached_property

from catracking.core import (
    Tracker,
    MissingTrackerConfigurationError)
from catracking.ga.dimensions import CD25_US_GA_CLIENT_ID


def generate_ga_client_id():
    """
    Generates a new random id to be used as client id if one is not provided
    by Google Analytics.
    """
    random_string = str(uuid.uuid4().int % 2147483647)
    timestamp = str(int(time()))
    return 'GA1.1.{0}'.format('.'.join([random_string, timestamp]))


class GoogleAnalyticsTracker(Tracker):
    """
    Builds the skeleton of a Measurement Protocol hit.

    All information added to the hit by this class is required and
    should be the same for all type of hits.
    """

    def __init__(self, request):
        super(GoogleAnalyticsTracker, self).__init__()
        self.request = request

    @classmethod
    def settings(cls, key):
        """
        Returns the value Google Analytics tracker settings.
        """
        try:
            return super(GoogleAnalyticsTracker, cls).settings('GA')[key]
        except KeyError:
            raise MissingTrackerConfigurationError(
                'Missing {} in GA tracker configuration'.format(key))

    @property
    def ga_property(self):
        """
        Google Analytics property should be equal to the specific property
        in our account that we are going to send the hits.
        Production and test/local environments currently have different ones.
        """
        return GoogleAnalyticsTracker.settings('PROPERTY')

    @property
    def document_hostname(self):
        """
        Document Hostname is used to identify from which host an event
        is coming from. In some cases GA does not bind an event to a session
        and if we don't specify the document hostname, we can't identify
        what application sent it.
        """
        return GoogleAnalyticsTracker.settings('DOCUMENT_HOSTNAME')

    @cached_property
    def client_id(self):
        """
        ID generated in Google Analytics for each client.
        A middleware should handle the creation of it in case Google Analytics
        was not loaded beforehand.
        If the middleware created the value, it will be available in the
        session as `ga_client_id`.

        Every hit should contain a client id, so it can be identified and
        included to a specific session.

        A `_ga2017` cookie real example: `GA1.1.809004643.1509480820` and
        in Measurement Protocol, we need to get rid of `GA1.1.`.
        """
        return self.request.session.get('ga_client_id', None) or '.'.join(
            self.request.COOKIES.get('_ga2017', '').split('.')[-2:])

    @cached_property
    def user_id(self):
        """
        Identifies the user in our database inside GA.
        If there's an user attached to the request, returns its pk.
        Non authenticated users will return either 0 or `None`.
        """
        try:
            return self.request.user.pk
        except AttributeError:
            return 0

    @property
    def encoded_url(self):
        """
        Returns the full encoded url for the hit.
        Cache buster parameter should be the last in the querystring.
        """
        self[parameters.CACHE_BUSTER] = random.randint(1, 100000)
        return urlencode(self)

    def send(self):
        pass


class MeasurementProtocolHit(OrderedDict):

    def __init__(self):
        self[parameters.VERSION] = 1
        self[parameters.TRACKING_ID] = self.ga_property
        self[parameters.CLIENT_ID] = self.client_id
        if self.user_id:
            self[parameters.USER_ID] = self.user_id
        self[parameters.USER_AGENT] = self.request.META.get(
            'HTTP_USER_AGENT', '')
        self[parameters.DOCUMENT_HOSTNAME] = self.document_hostname
        self[CD25_US_GA_CLIENT_ID] = self.client_id


class EventHit(MeasurementProtocolHit):
    """
    Builds an event hit for Measurement Protocol.

    Adds the base information required for an `event` hit type, any
    additional data can be appended to the object (custom dimensions, metrics)
    """

    def __init__(self, request, category, action, label, value,
                 non_interactive='1'):
        """
        Events are non interactive by default, using `non_interactive=0`
        makes it interactive and will affect the bounce rate metric
        """
        super(EventHit, self).__init__(request)
        self[parameters.HIT_TYPE] = parameters.HIT_TYPE_EVENT
        self[parameters.EVENT_CATEGORY] = category
        self[parameters.EVENT_ACTION] = action
        self[parameters.EVENT_LABEL] = label
        self[parameters.EVENT_VALUE] = value
        self[parameters.EVENT_NON_INTERACTIVE] = non_interactive
