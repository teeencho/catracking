import arrow

from catracking.ga.core import GoogleAnalyticsTracker

COOKIE_NAME = '_ga2017'


class GoogleAnalyticsCookieMiddleware(object):
    """
    Generates the `_ga2017` cookie in case it does not exist yet.

    This middleware should not be used by all our applications,
    only the ones that really need to generate a cookie before hitting a view.

    IMPORTANT: Using this middleware in applications with varnish might
    invalidate the cache, cause it will set a cookie in the response.
    """

    def process_request(self, request):
        """
        Generates a client id and adds to the session in case `_ga2017` cookie
        does not exist.
        """
        if COOKIE_NAME not in request.COOKIES:
            request.session['ga_cookie'] = \
                GoogleAnalyticsTracker.generate_ga_cookie()

    def process_response(self, request, response):
        """
        If a session value was added by `process_request`, pops that out
        and adds it as a cookie. This cookie will be used by Google Analytics.
        """
        if 'ga_cookie' in request.session:
            response.set_cookie(
                COOKIE_NAME,
                request.session.pop('ga_cookie'),
                domain=GoogleAnalyticsTracker.settings('COOKIE_DOMAIN'),
                expires=arrow.utcnow().shift(years=+2).datetime)
