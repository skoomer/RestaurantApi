from rest_framework import serializers
from .models import Order, CartItems, Cart


class OrderListSerializer(serializers.ModelSerializer):
    """List of orders with fields: customer name, date, total price, number_dishes(total number), status"""

    number_dishes = serializers.SerializerMethodField()

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
        cart = Cart.objects.filter(order=obj)
        cart_items = CartItems.objects.filter(cart__in=cart)
        total_quantity = 0
        for cart_item in cart_items:
            total_quantity += cart_item.quantity
        return total_quantity
