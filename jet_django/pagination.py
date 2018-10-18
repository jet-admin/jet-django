from collections import OrderedDict

from django.core.paginator import Paginator
from django.db import connection
from django.utils.functional import cached_property

from jet_django.deps.rest_framework.pagination import PageNumberPagination
from jet_django.deps.rest_framework.response import Response


class CustomPaginator(Paginator):
    def count_for_postgresql(self, db_table):
        cursor = connection.cursor()
        cursor.execute('SELECT reltuples FROM pg_class WHERE relname = %s', [db_table])
        return int(cursor.fetchone()[0])

    def count_for_mysql(self, db_table):
        cursor = connection.cursor()
        cursor.execute('EXPLAIN SELECT COUNT(*) FROM `{}`'.format(db_table))
        return int(cursor.fetchone()[8])

    @cached_property
    def count(self):
        query = self.object_list.query
        result = None

        if not query.where:
            try:
                if connection.vendor == 'postgresql':
                    result = self.count_for_postgresql(query.model._meta.db_table)
                elif connection.vendor == 'mysql':
                    result = self.count_for_mysql(query.model._meta.db_table)
            except:
                pass

        if result is not None and result >= 10000:
            return result

        return super(CustomPaginator, self).count


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = '_per_page'
    django_paginator_class = CustomPaginator

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('num_pages', self.page.paginator.num_pages),
            ('per_page', self.page.paginator.per_page),
        ]))
