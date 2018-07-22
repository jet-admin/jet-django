import django_filters

from jetty.models.view_settings import ViewSettings


class ViewSettingsFilterSet(django_filters.FilterSet):
    class Meta:
        model = ViewSettings
        fields = (
            'app_label',
            'model',
        )
