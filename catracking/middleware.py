from collections import namedtuple

from django.conf import settings

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
            setattr(request.trackers, tracker,
                    self.TRACKERS_MAP[tracker](request))

    def process_response(self, request, response):
        """
        After hitting the view and before delivering the response to the
        client, every event prepared from each tracker needs to be sent.
        """
        if hasattr(request, 'trackers'):
            for tracker in request.trackers._fields:
                getattr(request.trackers, tracker).send()
        return response
