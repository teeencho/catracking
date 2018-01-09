
class MiddlewareMixin(object):
    """
    Adds compatibility from django 1.9 and django 1.11+.
    Unfortunately, django 1.9 does not have
    `django.utils.deprecation.MiddlewareMixin`, as it is available on 1.10
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response