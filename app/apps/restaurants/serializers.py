from rest_framework import serializers
from .models import Restaurant, Cuisines, Dishes


class DishesSerializer(serializers.ModelSerializer):
    """Main serializer.used in restaurants, filters ,cuisines"""

    price = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        """set fields , models serializers"""

        model = Dishes
        fields = ["title", "description", "price", "like", "cuisines"]


class CuisinesSerializer(serializers.ModelSerializer):
    """Main serializers for cuisines.Used in restaurants,cuisines list,
    used in filters"""

    dishes = DishesSerializer(many=True, read_only=True)

    class Meta:
        """set fields , models serializers"""

        model = Cuisines
        fields = ["name", "restaurants", "dishes"]


class RestaurantListSerializer(serializers.ModelSerializer):
    """Main serializers for restaurant.Used in restaurant list,detail inf, filters, orders"""

    class Meta:
        """set fields , models serializers"""

        model = Restaurant
        fields = [
            "title",
            "description",
            "photo",
            "location",
        ]