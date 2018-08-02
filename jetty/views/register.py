from django.http import HttpResponseBadRequest
from django.views import generic

from jetty import settings
from jetty.utils.backend import register_token


class RegisterView(generic.RedirectView):
    def get(self, request, *args, **kwargs):
        token, created = register_token()

        if not token:
            return HttpResponseBadRequest

        self.url = '{}/projects/register/{}'.format(settings.JETTY_BACKEND_WEB_BASE_URL, token.token)
        return super().get(request, *args, **kwargs)
