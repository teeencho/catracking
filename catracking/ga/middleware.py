import arrow
import logging

from catracking.ca.core import generate_ga_client_id

logger = logging.getLogger(__name__)


COOKIE_NAME = '_ga2017'


class GoogleAnalyticsCookieMiddleware(object):
    """
    Generates the `_ga2017` cookie in case it does not exist yet.

    This middleware should not be used by all our applications,
    only the ones that really need to generate a cookie before hitting a view.

    IMPORTANT: Using this middleware in applications with varnish might
    invalidate the cache, cause it will set a cookie in the response.
    """

    def process_request(request):
        """
        Generates a client id and adds to the session in case `_ga2017` cookie
        does not exist.
        """
        if COOKIE_NAME not in request.COOKIES:
            request.session['ga_client_id'] = generate_ga_client_id()

    def process_response(request, response):
        """
        If a session value was added by `process_request`, pops that out
        and adds it as a cookie. This cookie will be used by Google Analytics.
        """
        if 'ga_client_id' in request.session:
            response.set_cookie(
                COOKIE_NAME,
                request.session.pop('ga_client_id'),
                domain=GoogleAnalyticsTracker.settings('COOKIE_DOMAIN'),
                expires=arrow.utcnow().shift(years=+2).datetime)
