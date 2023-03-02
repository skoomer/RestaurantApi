from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance


class RestaurantFilter(filters.FilterSet):
    """restaurant filters: cuisines,description, avg price,title, distance"""
    cuisines = filters.CharFilter(field_name="cuisines__name", label="Cuisines name")
    description = filters.CharFilter(
        field_name="description", label="Description restaurants"
    )
    title = filters.CharFilter(field_name="title", label="Title restaurant")

    cuisines__dishes__price__gt = filters.NumberFilter(
        field_name="cuisines__dishes__price", lookup_expr="gt"
    )
    cuisines__dishes__price__lt = filters.NumberFilter(
        field_name="cuisines__dishes__price", lookup_expr="lt"
    )

    coordinates = filters.CharFilter(method="filter_by_distance", label="coordinates")

    def filter_by_distance(self, queryset, name, value):
        try:
            longitude, latitude = map(float, value.split(","))
        except ValueError:
            return queryset.none()
        user_location = Point(longitude, latitude, srid=4326)
        return queryset.annotate(distance=Distance("location", user_location)).order_by(
            "distance"
        )
