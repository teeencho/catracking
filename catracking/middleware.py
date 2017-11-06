from collections import namedtuple

from django.conf import settings
from django.utils.module_loading import import_string

from catracking.core import MissingTrackerConfigurationError
from catracking.ga.core import GoogleAnalyticsTracker


class TrackingMiddleware(object):
    """
    Any request that resolves to a view  should have the trackers available
    for usage. So they are accessible from `request.trackers`.

    As an example, we could use the `ga` tracker with `request.trackers.ga`
    in any view.
    """

    TRACKERS_MAP = {
        GoogleAnalyticsTracker.IDENT: GoogleAnalyticsTracker
    }

    @property
    def trackers(self):
        return [tracker for tracker in getattr(
            settings, 'TRACKERS', {}) if tracker in self.TRACKERS_MAP]

    def resolve_tracker(self, tracker_class):
        """
        Resolves the correct tracker to be instantiated.
        If there is a custom tracker, uses it instead of the base one.
        """
        try:
            return import_string(tracker_class.settings('CUSTOM_TRACKER'))
        except (ImportError, MissingTrackerConfigurationError):
            return tracker_class

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Creates a `trackers` object in the request and loops through the
        configured trackers in django settings.

        Available trackers from the package but not yet configured should
        not be added to the trackers object.
        """
        setattr(request, 'trackers', namedtuple(
            'Trackers', ' '.join(self.trackers)))

        for tracker in self.trackers:
            tracker_class = self.resolve_tracker(self.TRACKERS_MAP[tracker])
            setattr(request.trackers, tracker, tracker_class(request))

    def process_response(self, request, response):
        """
        After hitting the view and before delivering the response to the
        client, every event prepared from each tracker needs to be sent.
        """
        if hasattr(request, 'trackers'):
            for tracker in request.trackers._fields:
                getattr(request.trackers, tracker).send()
        return response
