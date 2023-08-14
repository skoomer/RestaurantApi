from rest_framework import viewsets, permissions, mixins
from .serializers import OrderListSerializer, OrderDetailSerializer, CartSerializer
from .models import Order, Cart


class OrderListView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """List of orders with fields: customer name,
    date, total price, number of dishes, status.Orders API for a logged in user"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        qs = Order.objects.filter(customer=self.request.user)
        return qs

    def get_serializer_class(self):
        """on assignment. in the detailed information
        about the restaurant"""
        if self.action == "retrieve":
            return OrderDetailSerializer

        return self.serializer_class


class CartCreateView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """create cart"""

    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = Cart.objects.filter(customer=self.request.user, order=None)
        else:
            qs = Cart.objects.filter(order=None)
        return qs

    def perform_create(self, serializer):
        anonymous = self.request.user.is_authenticated
        if anonymous is False:
            serializer.save(customer=None)
        else:
            serializer.save()
