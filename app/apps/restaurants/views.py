from rest_framework import viewsets, permissions, mixins
from django.shortcuts import redirect
from django.db.models import Avg
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    DishesSerializer,
)
from .models import Restaurant, Dishes
from .filters import RestaurantFilter, DishesFilterSet


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
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = RestaurantFilter
    search_fields = ["title", "description"]
    ordering = ["-average_price", "-distance"]

    def get_queryset(self):
        queryset = Restaurant.objects.annotate(
            average_price=Avg("dishes_restaurant__price")
        ).order_by("average_price")

        return queryset

    def get_serializer_class(self):
        """on assignment. in the detailed information
        about the restaurant,
        you need to show an additional field"""
        if self.action == "retrieve":
            return RestaurantDetailSerializer
        return RestaurantListSerializer


class MenuEndpointViews(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    """5. Endpoint with menu of a certain restaurant
    list of all available dishes in menu
    add filters by cuisine
    search by title and description
    ordering by price
    available only for logged in users
    Leave a like to a dish"""

    serializer_class = DishesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]

    filterset_class = DishesFilterSet
    ordering_fields = ["price"]
    search_fields = ["title", "description"]
    lookup_field = "pk"

    def get_queryset(self):
        restaurant_id = self.kwargs["restaurant_pk"]
        queryset = Dishes.objects.filter(restaurants_id=restaurant_id)
        return queryset

    @action(detail=True, methods=["post"])
    def like_dish(self, request, restaurant_pk=None, pk=None):
        """action  set user like and return  quantity likes"""
        if not self.request.user.is_authenticated:
            # Redirect to login
            return redirect("rest_login")

        dish = self.get_object()
        user = self.request.user.id

        if user in dish.like_user:
            dish.like_user.remove(user)
            dish.save()
            return Response({"detail": "you canceled your like"})

        dish.like_user.append(user)
        dish.save()
        serializer = DishesSerializer(dish)
        return Response(serializer.data)
