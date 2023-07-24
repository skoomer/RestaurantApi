from rest_framework import serializers
from django.db.models import Sum
from .models import Order, CartItems


class OrderListSerializer(serializers.ModelSerializer):
    """List of orders with fields: customer name, date, total price, number_dishes(total number), status"""

    number_dishes = serializers.SerializerMethodField()
    creation_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    class Meta:
        """set fields , models serializers"""

        model = Order
        fields = (
            "id",
            "costumer_name",
            "creation_date",
            "total_price",
            "number_dishes",
            "status",
        )

    def get_number_dishes(self, obj):
        cart_items = CartItems.objects.filter(cart__order=obj)
        total_quantity = cart_items.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        return total_quantity or 0
