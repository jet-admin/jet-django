from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from jetty.admin.jetty import jetty
from jetty.views.dashboard import DashboardViewSet
from jetty.views.menu_settings import MenuSettingsViewSet
from jetty.views.model_description import ModelDescriptionViewSet
from jetty.views.register import RegisterView
from jetty.views.sql import SqlView
from jetty.views.view_settings import ViewSettingsViewSet
from jetty.views.widget import WidgetViewSet


def init_urls():
    class Router(DefaultRouter):
        include_root_view = False

    router = Router()

    jetty.register_related_models()

    for model in jetty.models:
        router.register(model.viewset_url, model.viewset)

    router.register('model_descriptions', ModelDescriptionViewSet)
    router.register('dashboards', DashboardViewSet)
    router.register('widgets', WidgetViewSet)
    router.register('view_settings', ViewSettingsViewSet)
    router.register('menu_settings', MenuSettingsViewSet)

    extra_urls = [
        url(r'^model_descriptions_base/', jetty.models_view().as_view(), name='model-descriptions'),
        url(r'^register/', RegisterView.as_view(), name='register'),
        url(r'^sql/', SqlView.as_view(), name='sql')
    ]

    api_urls = router.urls + extra_urls

    return api_urls


jetty_urls = init_urls()
