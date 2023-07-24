from rest_framework import viewsets, permissions, mixins
from .serializers import OrderListSerializer

from .models import Order


class OrderListView(viewsets.GenericViewSet, mixins.ListModelMixin):
    """List of orders with fields: customer name,
    date, total price, number of dishes, status.Orders API for a logged in user"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        qs = Order.objects.filter(costumer=self.request.user)
        return qs
