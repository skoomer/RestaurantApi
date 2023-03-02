from rest_framework import serializers
from .models import Restaurant, Cuisines, Dishes


class DishesSerializer(serializers.ModelSerializer):
    """dishes serializer"""
    price = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        """set fields , models serializers"""
        model = Dishes
        fields = ["title", "description", "price", "like", "cuisines"]

    def to_representation(self, instance):
        representation = super().to_representation(instance.price)
        return representation


class CuisinesSerializer(serializers.ModelSerializer):
    """cuisines serializer"""
    dishes = DishesSerializer(many=True, read_only=True)

    class Meta:
        """set fields , models serializers"""
        model = Cuisines
        fields = ["name", "restaurants", "dishes"]


class RestaurantListSerializer(serializers.ModelSerializer):
    """restaurant serializer"""
    class Meta:
        """set fields , models serializers"""
        model = Restaurant
        fields = [
            "title",
            "description",
            "photo",
            "location",
        ]
