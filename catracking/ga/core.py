import catracking.ga.parameters as parameters
import random
import time
import uuid

from collections import OrderedDict
from urllib import urlencode

from django.conf import settings as django_settings
from django.utils.functional import cached_property

from catracking.ga.dimensions import CD25_US_GA_CLIENT_ID


class TrackerNotConfiguredError(Exception):
    """
    Raised when the tracker has not been configured in settings.
    Each tracker should have its configuration specific in TRACKERS.
    """
    pass


class MissingTrackerConfigurationError(Exception):
    """
    Raised when a required parameters is not speficied in the tracker config.
    """
    pass


def generate_ga_client_id():
    """
    Generates a new random id to be used as client id if one is not provided
    by Google Analytics.
    """
    random_string = str(uuid.uuid4().int % 2147483647)
    timestamp = str(int(time()))
    return 'GA1.1.{0}'.format('.'.join([random_string, timestamp]))


class MeasurementProtocol(OrderedDict):
    """
    Builds the skeleton of a Measurement Protocol hit.

    All information added to the hit by this class is required and
    should be the same for all type of hits.
    """

    def __init__(self, request):
        super(MeasurementProtocol, self).__init__()
        self.request = request

        self[parameters.VERSION] = 1
        self[parameters.TRACKING_ID] = self.ga_property
        self[parameters.CLIENT_ID] = self.client_id
        if self.user_id:
            self[parameters.USER_ID] = self.user_id
        self[parameters.USER_AGENT] = self.request.META.get(
            'HTTP_USER_AGENT', '')
        self[parameters.DOCUMENT_HOSTNAME] = self.document_hostname
        self[CD25_US_GA_CLIENT_ID] = self.client_id

    @property
    def settings(self):
        """
        Returns the Google Analytics tracker configuration.

        An error will be raised if this property is ever called without
        a configuration for the tracker.
        """
        try:
            return django_settings.TRACKERS['GA']
        except AttributeError:
            raise TrackerNotConfiguredError(
                'GA tracker configuration does not exist.')

    @property
    def ga_property(self):
        """
        Google Analytics property should be equal to the specific property
        in our account that we are going to send the hits.
        Production and test/local environments currently have different ones.
        """
        try:
            return self.settings['PROPERTY']
        except KeyError:
            raise MissingTrackerConfigurationError(
                'Missing PROPERTY in GA tracker configuration')

    @property
    def document_hostname(self):
        """
        Document Hostname is used to identify from which host an event
        is coming from. In some cases GA does not bind an event to a session
        and if we don't specify the document hostname, we can't identify
        what application sent it.
        """
        try:
            return self.settings['DOCUMENT_HOSTNAME']
        except KeyError:
            raise MissingTrackerConfigurationError(
                'Missing DOCUMENT_HOSTNAME in GA tracker configuration')

    @cached_property
    def client_id(self):
        """
        ID generated in Google Analytics for each client.
        A middleware should handle the creation of it in case Google Analytics
        was not loaded beforehand.

        Every hit should contain a client id, so it can be identified and
        included to a specific session.

        A `_ga2017` cookie real example: `GA1.1.809004643.1509480820` and
        in Measurement Protocol, we need to get rid of `GA1.1.`.
        """
        return '.'.join(
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


class EventHit(MeasurementProtocol):
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
