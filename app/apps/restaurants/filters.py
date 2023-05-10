from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Cuisines, Restaurant


class RestaurantFilter(filters.FilterSet):
    """restaurant filters: cuisines,description, avg price,title, distance"""

    cuisines = filters.ModelMultipleChoiceFilter(
        queryset=Cuisines.objects.all(),
        field_name="cuisines__name",
        to_field_name="name",
    )

    min_price = filters.NumberFilter(
        field_name="dishes_restaurant__price", lookup_expr="gt", label="Min price"
    )
    max_price = filters.NumberFilter(
        field_name="dishes_restaurant__price", lookup_expr="lt", label="Max price"
    )

    coordinates = filters.CharFilter(method="filter_by_distance", label="coordinates")

    ordering = filters.OrderingFilter(
        fields=(
            ("average_price", "average_price"),
            ("distance", "distance"),
        ),
    )

    class Meta:
        """main meta filter class restaurants"""

        model = Restaurant
        fields = ["cuisines", "coordinates", "min_price", "max_price"]

    def filter_by_distance(self, queryset, name, value):
        try:
            longitude, latitude = map(float, value.split(","))
        except ValueError:
            return queryset.none()
        user_location = Point(longitude, latitude, srid=4326)
        return (
            queryset.annotate(distance=Distance("location", user_location))
            .order_by("distance")
            .distinct()
        )
