
class MethodOverrideViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        METHOD_OVERRIDE_HEADER = 'HTTP_X_HTTP_METHOD_OVERRIDE'

        if METHOD_OVERRIDE_HEADER in request.META:
            request.method = request.META[METHOD_OVERRIDE_HEADER]

        return super().dispatch(request, *args, **kwargs)
