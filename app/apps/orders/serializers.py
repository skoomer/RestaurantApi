from rest_framework import serializers
from django.db.models import Sum
from apps.restaurants.serializers import DishesSerializer
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
    creation_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    class Meta(OrderSerializer.Meta):
        """set fields , models serializers"""

        model = Order
        fields = OrderSerializer.Meta.fields + ["number_dishes"]

    def get_number_dishes(self, obj):
        cart_items = CartItems.objects.filter(cart__order=obj)
        total_quantity = cart_items.aggregate(total_quantity=Sum("quantity"))[
            "total_quantity"
        ]
        return total_quantity or 0


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

        dishes = [item.dish for item in cart_items]
        return DishesSerializer(instance=dishes, many=True).data
