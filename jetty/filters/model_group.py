import django_filters
from django.db.models import Count, Sum, Min, Max, Avg, Value, F
from django.db.models.functions import TruncDate
from django_filters.constants import EMPTY_VALUES


class GroupFilter(django_filters.CharFilter):

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        if value['y_func'] == 'Count':
            y_func = Count(value['y_column'])
        elif value['y_func'] == 'Sum':
            y_func = Sum(value['y_column'])
        elif value['y_func'] == 'Min':
            y_func = Min(value['y_column'])
        elif value['y_func'] == 'Max':
            y_func = Max(value['y_column'])
        elif value['y_func'] == 'Avg':
            y_func = Avg(value['y_column'])
        else:
            return qs.none()

        x_lookup = value['x_lookup'] if value['x_lookup'] else F

        qs = qs \
            .annotate(group=x_lookup(value['x_column']))\
            .values('group')\
            .annotate(y_func=y_func)\
            .order_by('group')

        return qs
