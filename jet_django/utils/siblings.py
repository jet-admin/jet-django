from django.db import connection
from django.db.models.sql import Query


def get_row_number(Model, instance, where_sql, where_args, order_by_sql):
    pk = Model._meta.pk.name
    table = Model._meta.db_table

    with connection.cursor() as cursor:
        query = '''
            SELECT 
              rows.row 
            FROM 
              (
                SELECT 
                  {} as pk, 
                  ROW_NUMBER() OVER({}) AS row 
                FROM 
                  {}
                {}
              ) AS rows 
            WHERE 
              rows.pk = %s
        '''.format(
            pk,
            order_by_sql,
            table,
            where_sql
        )

        cursor.execute(query, where_args + [instance.pk])
        row = cursor.fetchone()

    if not row:
        return

    return row[0]


def get_row_siblings(Model, row_number, where_sql, where_args, order_by_sql):
    pk = Model._meta.pk.name
    table = Model._meta.db_table

    has_previous = row_number > 1
    offset = row_number - 2 if has_previous else row_number - 1
    limit = 3 if has_previous else 2

    with connection.cursor() as cursor:
        query = '''
                    SELECT {} 
                    FROM {} 
                    {}
                    {} 
                    LIMIT %s 
                    OFFSET %s
                '''.format(
            pk,
            table,
            where_sql,
            order_by_sql
        )
        cursor.execute(query, where_args + [limit, offset])
        rows = cursor.fetchall()

    if has_previous:
        next_index = 2
    else:
        next_index = 1

    if next_index >= len(rows):
        next_index = None

    if has_previous:
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
        return '{} {}'.format(name, operator)

    ordering = queryset.query.order_by
    compiler = Query(Model).get_compiler(connection=connection)
    where_query, where_args = queryset.query.where.as_sql(compiler, connection)
    where_sql = 'WHERE {}'.format(where_query) if where_query != '' else ''
    order_by = list(map(map_ordering, ordering))
    order_by_sql = 'ORDER BY {}'.format(', '.join(order_by)) if len(order_by) else ''

    row_number = get_row_number(Model, instance, where_sql, where_args, order_by_sql)

    if not row_number:
        return {}

    return get_row_siblings(Model, row_number, where_sql, where_args, order_by_sql)
