from rest_framework import viewsets, permissions, mixins
from django.db.models import Avg
from .serializers import RestaurantListSerializer, RestaurantDetailSerializer
from .models import Restaurant
from .filters import RestaurantFilter


class RestaurantListView(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    """3. Endpoint with list of all restaurants with
    Fields: name, description, location, image, had order
    filtering by cuisines, average price

    ordering by distance, average price
    searching by title(restaurants) and description(restaurants))
    available for all users (even unauthorized)"""

    serializer_class = RestaurantListSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"
    filterset_class = RestaurantFilter
    ordering_fields = ["cuisines__dishes__price"]

    def get_queryset(self):
        qs = Restaurant.objects.annotate(
            average_price=Avg("cuisines__dishes__price")
        ).order_by("average_price")

        return qs

    def get_serializer_class(self):
        """on assignment. in the detailed information
        about the restaurant,
        you need to show an additional field"""
        if self.action == "retrieve":
            return RestaurantDetailSerializer
        return RestaurantListSerializer
