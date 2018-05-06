from jetty.admin.model_description import JettyAdminModelDescription
from rest_framework import views
from rest_framework.response import Response


class JettyAdmin(object):
    models = []

    def models_view(self):
        Admin = self

        class View(views.APIView):
            def get(self, request, *args, **kwargs):
                return Response(map(lambda x: x.serialize(), Admin.models))

        return View

    def register(self, Model, fields=None, actions=list(), ordering_field=None):
        self.models.append(JettyAdminModelDescription(Model, fields, actions, ordering_field))

jetty = JettyAdmin()
