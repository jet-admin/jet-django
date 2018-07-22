from collections import OrderedDict

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from jetty.admin.jetty import jetty
from jetty.views.dashboard import DashboardViewSet
from jetty.views.view_settings import ViewSettingsViewSet
from jetty.views.widget import WidgetViewSet


def init_urls():
    class Router(DefaultRouter):
        def get_api_root_view(self, api_urls=None):
            api_root_dict = OrderedDict()
            list_name = self.routes[0].name
            for prefix, viewset, basename in self.registry:
                api_root_dict[prefix] = list_name.format(basename=basename)
            api_root_dict['model_descriptions'] = 'model-descriptions'
            return self.APIRootView.as_view(api_root_dict=api_root_dict)

    router = Router()

    jetty.register_related_models()

    for model in jetty.models:
        router.register(model.viewset_url, model.viewset)

    router.register('dashboards', DashboardViewSet)
    router.register('widgets', WidgetViewSet)
    router.register('view_settings', ViewSettingsViewSet)

    extra_urls = [
        url(r'^model_descriptions/', jetty.models_view().as_view(), name='model-descriptions')
    ]

    api_urls = router.urls + extra_urls

    return api_urls


jetty_urls = init_urls()
