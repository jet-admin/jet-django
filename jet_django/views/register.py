from urllib.parse import quote

from django.views import generic

from jet_django import settings
from jet_django.utils.backend import register_token


class RegisterView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token, created = register_token()

        if not token:
            return

        url = '{}/projects/register/{}'.format(settings.JET_BACKEND_WEB_BASE_URL, token.token)
        query_string = 'referrer={}'.format(quote(self.request.build_absolute_uri().encode('utf8')))

        return '%s?%s' % (url, query_string)
