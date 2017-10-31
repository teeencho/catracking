import random

from collections import OrderedDict
from urllib import urlencode

from django.conf import settings as django_settings

import catracking.ga.parameters as parameters
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


class MeasurementProtocol(OrderedDict):
    """
    Builds the skeleton of a Measurement Protocol hit.

    All information added to the hit by this class is required and
    should be the same for all type of hits.
    """

    def __init__(self, request):
        super(MeasurementProtocol, self).__init__()
        self.request = request
        client_id = self.client_id

        self[parameters.VERSION] = 1
        self[parameters.TRACKING_ID] = self.ga_property
        self[parameters.CLIENT_ID] = client_id
        self[parameters.USER_ID] = None
        self[parameters.USER_AGENT] = self.request.META.get(
            'HTTP_USER_AGENT', '')
        self[parameters.DOCUMENT_HOSTNAME] = self.document_hostname
        self[CD25_US_GA_CLIENT_ID] = client_id

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

    @property
    def client_id(self):
        return None

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
