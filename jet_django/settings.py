from django.conf import settings

JET_BACKEND_API_BASE_URL = getattr(settings, 'JET_BACKEND_API_BASE_URL', 'https://api.jetadmin.io/api')
JET_BACKEND_WEB_BASE_URL = getattr(settings, 'JET_BACKEND_WEB_BASE_URL', 'https://app.jetadmin.io')
JET_DEMO = getattr(settings, 'JET_DEMO', False)

JET_REST_FRAMEWORK = getattr(settings, 'JET_REST_FRAMEWORK', {
    'PAGE_SIZE': 25,
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    'DEFAULT_FILTER_BACKENDS': (
        'jet_django.deps.rest_framework.filters.DjangoFilterBackend',
        'jet_django.deps.rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'jet_django.deps.rest_framework.throttling.AnonRateThrottle',
        'jet_django.deps.rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '120/minute',
        'user': '480/minute'
    },
    'DEFAULT_RENDERER_CLASSES': (
        'jet_django.deps.rest_framework.renderers.JSONRenderer',
    )
})
