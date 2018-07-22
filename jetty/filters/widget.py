import django_filters

from jetty.models.widget import Widget


class WidgetFilterSet(django_filters.FilterSet):
    class Meta:
        model = Widget
        fields = (
            'dashboard',
        )
