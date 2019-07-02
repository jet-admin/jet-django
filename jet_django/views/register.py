from urllib.parse import quote

from django.http import HttpResponseRedirect, JsonResponse
from django.views import generic

from jet_django import settings
from jet_django.mixins.cors_api_view import CORSAPIViewMixin
from jet_django.utils.backend import register_token, is_token_activated


class RegisterView(CORSAPIViewMixin, generic.RedirectView):

    def get(self, request, *args, **kwargs):
        token, created = register_token()

        if not token:
            return

        if is_token_activated(token):
            return JsonResponse({
                'message': 'Project token is already activated'
            })

        if settings.JET_BACKEND_WEB_BASE_URL.startswith('https') and not self.request.is_secure():
            web_base_url = 'http{}'.format(settings.JET_BACKEND_WEB_BASE_URL[5:])
        else:
            web_base_url = settings.JET_BACKEND_WEB_BASE_URL

        url = '{}/projects/register/'.format(web_base_url)
        query_string = 'referrer={}'.format(quote(self.request.build_absolute_uri().encode('utf8')))

        return HttpResponseRedirect('%s?%s' % (url, query_string))
