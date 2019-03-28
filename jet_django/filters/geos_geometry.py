from jet_django.deps import django_filters


class GEOSGeometryFilter(django_filters.CharFilter):

    def filter(self, qs, value):
        try:
            from django.contrib.gis.geos import GEOSGeometry
            value = GEOSGeometry(value)
            return super().filter(qs, value)
        except (ValueError, TypeError, ImportError):
            return qs
