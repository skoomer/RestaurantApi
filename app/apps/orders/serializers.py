from rest_framework import serializers
from apps.restaurants.serializers import RestaurantListSerializer
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


class CartItemSerializer(serializers.ModelSerializer):
    """"Base cart item serializer"""
    quantity = serializers.IntegerField()
    price = serializers.SerializerMethodField()

    class Meta:
        """set fields , models serializers"""
        model = CartItems
        fields = (
            "id",
            "dish",
            "quantity",
            "price",
        )

    def get_price(self, obj):
        total_price = 0
        price = obj.dish.price
        total_price += price * obj.quantity
        return total_price


class CartSerializer(serializers.ModelSerializer):
    """Base cart model serializer"""
    # пізніше запитать як обробляти помилки - якщо створити корзину  з ресторан 1 а блюдо з ресторану 2

    items = CartItemSerializer(many=True)

    restaurant = RestaurantListSerializer(many=True, read_only=True)

    class Meta:
        """set fields , models serializers"""
        model = Cart

        fields = ["id", "restaurant", "items"]

    def create(self, validated_data):
        # issue - if create cart with restaurant 1 with dishes restaurant 2 have error , add exceptions
        cart_items = validated_data.pop("items")

        # Group the cart items by restaurant for convenience and iteration
        items_by_restaurant = {}
        user = self.context["request"].user.id

        for cart_item in cart_items:

            restaurant_id = cart_item["dish"].restaurants_id
            if restaurant_id not in items_by_restaurant:
                items_by_restaurant[restaurant_id] = []
            items_by_restaurant[restaurant_id].append(cart_item)

        # Create a cart for each restaurant and add the items
        carts = []

        for restaurant_id, items in items_by_restaurant.items():

            # Check if the user already has a cart for this restaurant
            existing_cart = Cart.objects.filter(
                customer_id=user, restaurant_id=restaurant_id, order=None
            )

            if not existing_cart:
                # If the cart does not exist or an order already exists, create a new cart
                cart = Cart.objects.create(
                    customer_id=user, restaurant_id=restaurant_id
                )
            else:
                cart = existing_cart.first()

            # Use the existing cart

            # Add the cart items to the cart

            for item in items:

                existing_item = CartItems.objects.filter(
                    cart=cart, dish=item["dish"], cart__restaurant__id=restaurant_id
                ).first()

                if existing_item:
                    existing_item.quantity += item["quantity"]
                    existing_item.save()
                else:

                    CartItems.objects.create(
                        cart=cart, dish=item["dish"], quantity=item["quantity"]
                    )
            carts.append(cart)

        return carts


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
