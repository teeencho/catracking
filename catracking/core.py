from abc import (
    ABCMeta,
    abstractmethod)

from django.conf import settings as django_settings

from catracking.tasks import SendTrackingDataTask


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


class Tracker(object):
    """
    Defines a tracker behavior.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @classmethod
    def is_active(cls):
        return hasattr(
            django_settings, 'TRACKERS'
        ) and cls.IDENT in django_settings.TRACKERS

    @classmethod
    def base_settings(cls):
        """
        Returns the settings object of a specific tracker.
        An error will be raised if the settings is ever called without
        a configuration for the tracker
        """
        try:
            return django_settings.TRACKERS[cls.IDENT]
        except (AttributeError, KeyError):
            raise TrackerNotConfiguredError(
                '{} tracker configuration does not exist.'.format(cls.IDENT))

    @classmethod
    def settings(cls, key):
        """
        Returns a specific setting property of the tracker.
        An error will be raised if the property is not defined.
        """
        try:
            return cls.base_settings()[key]
        except KeyError:
            raise MissingTrackerConfigurationError(
                'Missing {0} in {1} tracker configuration'.format(
                    key, cls.IDENT))

    @abstractmethod
    def send(self, payload_bucket):
        """
        Instantiates a celery task for each payload in the bucket.
        """
        for payload in payload_bucket:
            SendTrackingDataTask().delay(self.IDENT, self.ENDPOINT, payload)
