from catracking.core import Trackers
from catracking.ga.core import GoogleAnalyticsTracker


class TrackingMiddleware(object):
    """
    Any request that resolves to a view containing `trackers` should have
    its trackers available for usage.

    This only support Class Based Views.
    """

    TRACKERS_MAP = {
        Trackers.GOOGLE_ANALYTICS: GoogleAnalyticsTracker
    }

    def get_valid_trackers(self, trackers):
        return (
            tracker for tracker in trackers if tracker in self.TRACKERS_MAP)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not hasattr(view_func, 'view_class'):
            return

        setattr(request, 'trackers', {})
        for tracker in self.get_valid_trackers(
                getattr(view_func.view_class, 'trackers', [])):
            request.trackers[tracker] = self.TRACKERS_MAP[tracker](request)
