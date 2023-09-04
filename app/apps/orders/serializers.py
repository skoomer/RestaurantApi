from rest_framework import serializers
from apps.restaurants.serializers import RestaurantListSerializer
from django.db.models import Sum
from apps.accounts.serializers import UserSerializer
from apps.restaurants.serializers import DishesSerializer
from .models import Order, CartItems, Cart


class OrderSerializer(serializers.ModelSerializer):
    """Base order serializer"""

    class Meta:
        """set fields , models serializers"""

        model = Order
        fields = [
            "id",
            "customer_name",
            "creation_date",
            "total_price",
            "address",
            "status",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    """Base cart item serializer"""

    quantity = serializers.IntegerField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        """set fields , models serializers"""

        model = CartItems
        fields = (
            "id",
            "dish",
            "quantity",
            "total_price",
        )

    def get_total_price(self, obj):
        total_price = 0
        price = obj.dish.price
        total_price += price * obj.quantity
        return total_price


class CartSerializer(serializers.ModelSerializer):
    """Base cart model serializer"""

    cart_items = CartItemSerializer(many=True, partial=True)

    restaurant = RestaurantListSerializer(read_only=True)
    order = OrderSerializer(read_only=True, many=True)
    customer = UserSerializer(read_only=True)

    class Meta:
        """set fields , models serializers"""

        model = Cart

        fields = ["id", "restaurant", "cart_items", "order", "customer", "cart_uuid"]

    def update(self, instance, validated_data):
        # if items  update quantity eq 0 delete items
        # if cart empty cart_items delete cart

        # get objects cart_items
        cart_items_data = validated_data.get("cart_items")

        if cart_items_data is not None:
            cart_items = instance.cart_items.all()
            cart_items_dict = {item.dish.id: item for item in cart_items}

            # Create a set of cart item ids from the updated cart items data
            updated_cart_item_ids = {
                item_data.get("dish").id for item_data in cart_items_data
            }

            for cart_item in cart_items:
                if cart_item.dish.id not in updated_cart_item_ids:
                    cart_item.delete()

            for cart_item_data in cart_items_data:
                # get id objects in cart_items
                cart_item_id = cart_item_data.get("dish").id

                # get eq object from cart items
                cart_item = cart_items_dict.get(cart_item_id)

                # get current object
                if cart_item:
                    # get quantity or set default quantity ( safely access if key not found )
                    cart_item.quantity = cart_item_data.get(
                        "quantity", cart_item.quantity
                    )

                    # delete object cart_items from cart if quantity eq 0
                    if cart_item.quantity == 0:
                        cart_item.delete()
                    else:
                        cart_item.save()

        # delete instance cart if cart_items empty
        if instance.cart_items.count() == 0:
            instance.delete()

        return instance

    def create(self, validated_data):

        cart_items = validated_data.pop("cart_items")

        # Group the cart items by restaurant

        items_by_restaurant = {}
        user = self.context["request"].user.id

        for cart_item in cart_items:
            # Get all restaurants id

            restaurant_id = cart_item["dish"].restaurants_id
            if restaurant_id not in items_by_restaurant:
                items_by_restaurant[restaurant_id] = []
            items_by_restaurant[restaurant_id].append(cart_item)

        for restaurant_id, items in items_by_restaurant.items():
            # Create a cart for each restaurant and add the items

            # Check if the user already has a cart for this restaurant
            existing_cart = Cart.objects.filter(
                customer_id=user, restaurant_id=restaurant_id, order=None
            )

            if not existing_cart.first():
                # If the cart does not exist or an order already exists, create a new cart
                cart = Cart.objects.create(
                    customer_id=user, restaurant_id=restaurant_id
                )
            else:
                cart = existing_cart.first()

            for item in items:
                # Add the cart items to the cart, create cart items

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

            return cart


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


class OrderCreateSerializer(serializers.ModelSerializer):
    """Create an order with fields: list of dishes, address, customer name"""

    list_of_dishes = CartItemSerializer(
        many=True, source="cart.cart_items.all", read_only=True
    )

    class Meta:
        """set fields , models serializers"""
        model = Order
        fields = ("id", "address", "customer_name", "list_of_dishes")

    def create(self, validated_data):

        user = self.context["request"].user.id

        token = self.context["request"].data["cart_uuid"]

        cart = Cart.objects.filter(
            customer_id=user, order=None, cart_uuid=str(token)
        ).first()

        total_price = 0
        for item in cart.cart_items.all():
            total_price += item.dish.price * item.quantity

        order = Order.objects.create(
            cart_id=cart.id,
            total_price=total_price,
            customer_id=user,
            restaurant_id=cart.restaurant.id,
            status=Order.STATUS.in_processing,
            **validated_data,
        )
        return order
