from rest_framework import viewsets, permissions, mixins
from django.db.models import Avg
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import RestaurantListSerializer
from .models import Restaurant
from .filters import RestaurantFilter


class RestaurantListView(viewsets.GenericViewSet, mixins.ListModelMixin):
    """3. Endpoint with list of all restaurants with
    Fields: name, description, location, image, had order
    filtering by cuisines, average price

    ordering by distance, average price
    searching by title(restaurants) and description(restaurants))
    available for all users (even unauthorized)"""

    serializer_class = RestaurantListSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = RestaurantFilter
    search_fields = ["title", "description"]
    ordering = ["-average_price", "-distance"]

    def get_queryset(self):
        queryset = Restaurant.objects.annotate(
            average_price=Avg("dishes_restaurant__price")
        ).order_by("average_price")

        return queryset
