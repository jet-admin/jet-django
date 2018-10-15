import logging
import traceback

from jet_django.deps.rest_framework import status
from jet_django.deps.rest_framework.views import exception_handler, set_rollback
from jet_django.deps.rest_framework.response import Response

logger = logging.getLogger(__name__)


def jet_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if not response:
        data = {'detail': 'Server Error'}

        set_rollback()
        response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.exception('Jet view exception', exc_info=exc)
        traceback.print_exc()

    if context and 'request' in context and context['request'].method == 'OPTIONS':
        response.status_code = 204

        response['Access-Control-Max-Age'] = '1728000'
        response['Content-Type'] = 'text/plain; charset=utf-8'
        response['Content-Length'] = 0

    return response
