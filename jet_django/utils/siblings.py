from collections import OrderedDict


def get_model_sibling(Model, instance, next, ordering=None):
    if len(Model._meta.ordering):
        ordering = list(Model._meta.ordering) + ['-id']
    elif ordering is None:
        ordering = ['-id']
    elif ordering != ['-id']:
        ordering = list(ordering) + ['-id']

    def inverse_ordering(x):
        if x[0:1] == '-':
            return x[1:]
        else:
            return '-{}'.format(x)

    if not next:
        ordering = list(map(inverse_ordering, ordering))

    def map_ordering(x):
        asc = x[0:1] != '-'
        name = x if asc else x[1:]
        operator = 'gte' if asc else 'lte'
        return '{}__{}'.format(name, operator), getattr(instance, name)

    try:
        params = OrderedDict(map(map_ordering, ordering[0:1]))
    except AttributeError:
        params = {}

    found_instance = False
    sibling = None

    for item in Model.objects.filter(**params).order_by(*ordering).all():
        if item.pk == instance.pk:
            found_instance = True
        elif found_instance:
            sibling = item
            break

    return sibling
