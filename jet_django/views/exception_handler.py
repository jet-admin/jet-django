from jet_django.deps.rest_framework import status
from jet_django.deps.rest_framework.compat import set_rollback
from jet_django.deps.rest_framework.views import exception_handler
from jet_django.deps.rest_framework.response import Response


def jet_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if not response:
        data = {'detail': 'Server Error'}
        set_rollback()
        response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if context and 'request' in context and context['request'].method == 'OPTIONS':
        response.status_code = 204

        response['Access-Control-Max-Age'] = '1728000'
        response['Content-Type'] = 'text/plain; charset=utf-8'
        response['Content-Length'] = 0

    return response
