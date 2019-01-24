from django.core.files.storage import default_storage

from jet_django.deps.rest_framework import views
from jet_django.deps.rest_framework.response import Response

from jet_django import VERSION
from jet_django.mixins.cors_api_view import CORSAPIViewMixin


class RootView(CORSAPIViewMixin, views.APIView):
    def get(self, request, *args, **kwargs):
        unique_placeholder = '__FILE_PATH___'
        return Response({
            'version': VERSION,
            'type': 'jet_django',
            'media_url_template': request.build_absolute_uri(default_storage.url(unique_placeholder)).replace(unique_placeholder, '{}')
        })
