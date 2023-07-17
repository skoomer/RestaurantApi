from rest_framework import viewsets, permissions, mixins
from .serializers import OrderListSerializer, OrderDetailSerializer

from .models import Order


class OrderListView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """List of orders with fields: customer name,
    date, total price, number of dishes, status.Orders API for a logged in user"""

    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
    serializer_class = OrderListSerializer

    def get_queryset(self):
        qs = Order.objects.filter(costumer=self.request.user)
        return qs

    def get_serializer_class(self):
        """on assignment. in the detailed information
        about the restaurant"""
        if self.action == "retrieve":
            return OrderDetailSerializer

        return self.serializer_class
