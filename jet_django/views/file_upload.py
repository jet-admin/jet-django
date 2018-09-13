from rest_framework import views
from rest_framework.response import Response

from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.file_upload import FileUploadSerializer


class FileUploadView(views.APIView):
    pagination_class = None
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
