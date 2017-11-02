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
        GoogleAnalyticsTracker.ident: GoogleAnalyticsTracker
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Creates a `trackers` object in the request and loops through the
        configured trackers in django settings.

        Available trackers from the package but not yet configured should
        not be added to the trackers object.
        """
        setattr(request, 'trackers', namedtuple(
            'Trackers', ' '.join([tracker for tracker in self.TRACKERS_MAP])))

        for tracker in getattr(settings, 'TRACKERS', {}):
            if tracker in self.TRACKERS_MAP:
                setattr(request.trackers, tracker,
                        self.TRACKERS_MAP[tracker](request))
