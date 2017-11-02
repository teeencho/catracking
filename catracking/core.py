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


class Tracker(object):
    """
    Defines a tracker behavior.

    """
    __metaclass__ = ABCMeta

    @classmethod
    def is_active(cls):
        return hasattr(
            django_settings, 'TRACKERS'
        ) and cls.ident in django_settings.TRACKERS

    @classmethod
    def base_settings(cls):
        """
        Returns the settings object of a specific tracker.

        An error will be raised if this property is ever called without
        a configuration for the tracker.
        """
        try:
            return django_settings.TRACKERS[cls.ident]
        except (AttributeError, KeyError):
            raise TrackerNotConfiguredError(
                '{} tracker configuration does not exist.'.format(cls.ident))

    @classmethod
    def settings(cls, key):
        try:
            return cls.base_settings()[key]
        except KeyError:
            raise MissingTrackerConfigurationError(
                'Missing {0} in {1} tracker configuration'.format(
                    key, cls.ident))

    @abstractmethod
    def send(self, endpoint, data):
        pass
