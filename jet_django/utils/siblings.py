from django.db import connection
from django.db.models.sql import Query
from django.db.models.sql.datastructures import BaseTable


def get_row_number(Model, instance, join_sql, join_args, where_sql, where_args, order_by_sql):
    pk = Model._meta.pk.name
    table = Model._meta.db_table

    with connection.cursor() as cursor:
        query = '''
            SELECT 
              __inner.__inner__row 
            FROM 
              (
                SELECT 
                  {}.{} as __inner__pk, 
                  ROW_NUMBER() OVER({}) AS __inner__row
                FROM 
                  {}
                {}
                {}
              ) AS __inner 
            WHERE 
              __inner.__inner__pk = %s
        '''.format(
            table,
            pk,
            order_by_sql,
            table,
            join_sql,
            where_sql
        )
        args = join_args + where_args + [instance.pk]
        cursor.execute(query, args)
        row = cursor.fetchone()

    if not row:
        return

    return row[0]


def get_row_siblings(Model, row_number, join_sql, join_args, where_sql, where_args, order_by_sql):
    pk = Model._meta.pk.name
    table = Model._meta.db_table

    has_prev = row_number > 1
    offset = row_number - 2 if has_prev else row_number - 1
    limit = 3 if has_prev else 4

    with connection.cursor() as cursor:
        query = '''
                    SELECT {}.{} 
                    FROM {} 
                    {}
                    {}
                    {} 
                    LIMIT %s 
                    OFFSET %s
                '''.format(
            table,
            pk,
            table,
            join_sql,
            where_sql,
            order_by_sql
        )
        args = join_args + where_args + [limit, offset]
        cursor.execute(query, args)
        rows = cursor.fetchall()

    if has_prev:
        next_index = 2
    else:
        next_index = 1

    if next_index >= len(rows):
        next_index = None

    if has_prev:
        prev_index = 0
    else:
        prev_index = None

    def map_row(row):
        columns = (x.name for x in cursor.description)
        return dict(zip(columns, row))

    return {
        'prev': map_row(rows[prev_index]) if prev_index is not None else None,
        'next': map_row(rows[next_index]) if next_index is not None else None
    }


def get_model_siblings(Model, instance, queryset):
    def map_ordering(x):
        asc = x[0:1] != '-'
        name = x if asc else x[1:]
        operator = 'ASC' if asc else 'DESC'
        return '{}{} {}'.format(alias, name, operator)

    pk = Model._meta.pk.name
    ordering = queryset.query.order_by
    alias = ''

    if len(ordering) == 0 and len(Model._meta.ordering):
        ordering = Model._meta.ordering

    if not any(map(lambda x: x == pk or x == '-{}'.format(pk), ordering)):
        ordering = list(ordering) + ['-{}'.format(pk)]

    compiler = Query(Model).get_compiler(connection=connection)

    join_queries = []
    join_args = []

    for key, value in queryset.query.alias_map.items():
        if isinstance(value, BaseTable):
            alias = '{}.'.format(key)
        else:
            query, args = value.as_sql(compiler, connection)
            join_queries.append(query)
            join_args.extend(args)

    join_sql = ' '.join(join_queries)

    where_query, where_args = queryset.query.where.as_sql(compiler, connection)
    where_sql = 'WHERE {}'.format(where_query) if where_query != '' else ''
    order_by = list(map(map_ordering, ordering))
    order_by_sql = 'ORDER BY {}'.format(', '.join(order_by)) if len(order_by) else ''

    row_number = get_row_number(Model, instance, join_sql, join_args, where_sql, where_args, order_by_sql)

    if not row_number:
        return {}

    return get_row_siblings(Model, row_number, join_sql, join_args, where_sql, where_args, order_by_sql)
