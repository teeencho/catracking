
class MiddlewareMixin(object):
    """
    Adds compatibility from django 1.9 and django 1.11+.
    Unfortunately, django 1.9 does not have
    `django.utils.deprecation.MiddlewareMixin`, as it is available on 1.10
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
