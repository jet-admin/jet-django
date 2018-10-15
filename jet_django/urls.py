from django.conf.urls import url
from jet_django.deps.rest_framework.routers import DefaultRouter

from jet_django.admin.jet import jet
from jet_django.views.file_upload import FileUploadView
from jet_django.views.model_description import ModelDescriptionView
from jet_django.views.register import RegisterView
from jet_django.views.root import RootView
from jet_django.views.sql import SqlView

app_name = 'jet_django'


def init_urls():
    class Router(DefaultRouter):
        include_root_view = False

    router = Router()

    jet.register_related_models()

    for model in jet.models:
        router.register(model.viewset_url, model.viewset)

    extra_urls = [
        url(r'^model_descriptions/', ModelDescriptionView.as_view(), name='model-descriptions'),
        url(r'^register/', RegisterView.as_view(), name='register'),
        url(r'^sql/', SqlView.as_view(), name='sql'),
        url(r'^file_upload/', FileUploadView.as_view(), name='file-upload'),
        url(r'^$', RootView.as_view(), name='root')
    ]

    api_urls = router.urls + extra_urls

    return api_urls


jet_urls = init_urls()
