from rest_framework import serializers
from django.db.models import Count, Sum
from apps.accounts.serializers import UserSerializer
from .models import Restaurant, Cuisines, Dishes, Review


class DishesSerializer(serializers.ModelSerializer):
    """Main serializer.used in restaurants, filters ,cuisines"""

    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        """set fields , models serializers"""

        model = Dishes
        fields = ["title", "description", "price", "like_user", "cuisines"]
        read_only_fields = ["title", "description", "cuisines"]


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


class RestaurantDetailSerializer(RestaurantListSerializer):
    """Detail info for restaurants"""

    number_of_dishes = serializers.SerializerMethodField()

    class Meta(RestaurantListSerializer.Meta):
        """set fields , models serializers"""

        fields = RestaurantListSerializer.Meta.fields + [
            "creation_date",
            "number_of_dishes",
        ]

    def get_number_of_dishes(self, obj):
        return (
            obj.cuisines.all()
            .annotate(numb_dishes=Count("dishes"))
            .aggregate(total=Sum("numb_dishes"))["total"] or 0
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Main serializers for restaurant review in restaurant"""

    message = serializers.CharField(max_length=200)
    creation_date = serializers.DateTimeField(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        """set fields , models serializers"""

        model = Review
        fields = ["reviewer", "message", "creation_date"]
