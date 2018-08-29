from django.http import HttpResponseBadRequest
from django.views import generic

from jet_django import settings
from jet_django.utils.backend import register_token


class RegisterView(generic.RedirectView):
    def get(self, request, *args, **kwargs):
        token, created = register_token()

        if not token:
            return HttpResponseBadRequest

        self.url = '{}/projects/register/{}'.format(settings.JET_BACKEND_WEB_BASE_URL, token.token)
        return super().get(request, *args, **kwargs)
