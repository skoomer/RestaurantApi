from rest_framework import serializers
from .models import Order, CartItems, Cart


class OrderSerializer(serializers.ModelSerializer):
    """Base order serializer"""

    class Meta:
        """set fields , models serializers"""

        model = Order
        fields = [
            "id",
            "costumer_name",
            "creation_date",
            "total_price",
            "address",
            "status",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """List of orders with fields: customer name, date, total price, number_dishes(total number), status"""

    number_dishes = serializers.SerializerMethodField()

    class Meta(OrderSerializer.Meta):
        """set fields , models serializers"""

        model = Order
        fields = OrderSerializer.Meta.fields + ["number_dishes"]

    def get_number_dishes(self, obj):
        cart = Cart.objects.filter(order=obj)
        cart_items = CartItems.objects.filter(cart__in=cart)
        total_quantity = 0
        for cart_item in cart_items:
            total_quantity += cart_item.quantity
        return total_quantity


class OrderDetailSerializer(OrderSerializer):
    """Order details with fields: customer name, address,
    date, total price, number of orders(=id order), status, list of dishes."""

    list_of_dishes = serializers.SerializerMethodField()

    class Meta(OrderSerializer.Meta):
        """set fields , models serializers"""

        fields = OrderSerializer.Meta.fields + ["id", "list_of_dishes"]

    def get_list_of_dishes(self, obj):
        """get list dishes in orders"""
        cart = Cart.objects.filter(order=obj)
        cart_items = CartItems.objects.filter(cart__in=cart)

        return [
            {
                "name": item.dish.title,
                "price": item.dish.price,
                "quantity": item.quantity,
            }
            for item in cart_items
        ]
