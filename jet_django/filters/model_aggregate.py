from jet_django.deps import django_filters
from django.db.models import Count, Sum, Min, Max, Avg
from jet_django.deps.django_filters.constants import EMPTY_VALUES


class AggregateFilter(django_filters.CharFilter):

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        if value['y_func'] == 'count':
            y_func = Count(value['y_column'])
        elif value['y_func'] == 'sum':
            y_func = Sum(value['y_column'])
        elif value['y_func'] == 'min':
            y_func = Min(value['y_column'])
        elif value['y_func'] == 'max':
            y_func = Max(value['y_column'])
        elif value['y_func'] == 'avg':
            y_func = Avg(value['y_column'])
        else:
            return qs.none()

        qs = qs \
            .aggregate(y_func=y_func)

        return qs
