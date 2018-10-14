from jet_django.deps.rest_framework import views
from jet_django.deps.rest_framework.response import Response
from jet_django.mixins.cors_api_view import CORSAPIViewMixin
from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.file_upload import FileUploadSerializer


class FileUploadView(CORSAPIViewMixin, views.APIView):
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
