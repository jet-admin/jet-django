from django.conf import settings

JETTY_BACKEND_API_BASE_URL = getattr(settings, 'JETTY_BACKEND_API_BASE_URL', 'http://api.jetty.geex-arts.com/api')
JETTY_BACKEND_WEB_BASE_URL = getattr(settings, 'JETTY_BACKEND_WEB_BASE_URL', 'http://jetty.geex-arts.com')
JETTY_DEMO = getattr(settings, 'JETTY_DEMO', False)
