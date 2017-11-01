from abc import (
    ABCMeta,
    abstractmethod)

from django.conf import settings as django_settings


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


class Trackers:
    GOOGLE_ANALYTICS = 1


class Tracker(object):
    """
    Defines a tracker behavior.

    """
    __metaclass__ = ABCMeta

    @classmethod
    def settings(cls, tracker):
        """
        Returns the settings object of a specific tracker.

        An error will be raised if this property is ever called without
        a configuration for the tracker.
        """
        try:
            return django_settings.TRACKERS[tracker]
        except (AttributeError, KeyError):
            raise TrackerNotConfiguredError(
                'GA tracker configuration does not exist.')

    @abstractmethod
    def send(self, endpoint, data):
        pass
