import pytest
from django.test import TestCase
from django.urls import reverse
from apps.restaurants.factories import RestaurantFactory, CuisinesFactory, DishesFactory
from apps.restaurants.models import Restaurant
from django.contrib.gis.geos import Point
from apps.restaurants.filters import RestaurantFilter
from django.db.models import Avg
from django.contrib.gis.db.models.functions import Distance
from apps.restaurants.serializers import RestaurantDetailSerializer


@pytest.mark.django_db
class RestaurantListViewTestCase(TestCase):
    """unittest restaurant api"""

    def setUp(self):
        self.url_restaurants = reverse("restaurants:restaurant-list")

        self.cuisines1 = CuisinesFactory(
            name="Cuisines1",
        )
        self.cuisines2 = CuisinesFactory(
            name="Cuisines2",
        )
        self.cuisines3 = CuisinesFactory(
            name="Cuisines3",
        )

        self.restaurant1 = RestaurantFactory(
            title="Restaurant1",
            description="Description1",
            location=Point(1, 1),
            cuisines=self.cuisines1,
        )
        self.restaurant1.cuisines.set([self.cuisines1])

        self.restaurant2 = RestaurantFactory(
            title="Restaurant2",
            description="Description2",
            location=Point(2, 2),
            cuisines=self.cuisines2,
        )

        self.restaurant3 = RestaurantFactory(
            title="Restaurant3",
            description="Description3",
            location=Point(3, 3),
            cuisines=self.cuisines3,
        )

        self.dish1 = DishesFactory(
            cuisines=self.cuisines1, price=10, restaurants=self.restaurant1
        )
        self.dish2 = DishesFactory(
            cuisines=self.cuisines2, price=20, restaurants=self.restaurant2
        )
        self.dish3 = DishesFactory(
            cuisines=self.cuisines3, price=30, restaurants=self.restaurant3
        )
        self.filter = RestaurantFilter

    def test_list_restaurants(self):
        response = self.client.get(self.url_restaurants)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)

    def test_filter_by_cuisines(self):
        data = {"cuisines": self.cuisines1.name}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant1.title)

    def test_filter_by_description(self):

        data = {"search": self.restaurant2.description}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant2.title)

    def test_filter_by_title(self):

        data = {"search": self.restaurant3.title}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant3.title)

    def test_filter_by_price_gt(self):
        data = {"min_price": 20.0}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant3.title)

    def test_filter_by_price_lt(self):
        data = {"max_price": 20.0}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_list_restaurants_filter_by_price_range(self):
        response = self.client.get(
            self.url_restaurants, data={"min_price": 12, "max_price": 22}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant2.title)

    def test_filter_restaurants_by_coordinates(self):
        query_params = {"coordinates": "2,2"}
        instance = self.filter(query_params, queryset=Restaurant.objects.all())
        queryset = instance.qs

        self.assertEqual(queryset.count(), 3)
        self.assertEqual(queryset.first(), self.restaurant2)
        self.assertEqual(queryset.last(), self.restaurant1)

    def test_filter_restaurants_by_invalid_coordinates(self):
        query_params = {"coordinates": "invalid"}
        instance = self.filter(query_params, queryset=Restaurant.objects.all())
        queryset = instance.qs

        self.assertEqual(queryset.count(), 0)

    def test_average_price_ordering(self):
        queryset = (
            Restaurant.objects.annotate(average_price=Avg("dishes_restaurant__price"))
            .order_by("average_price")
            .distinct()
        )
        request = self.client.get(self.url_restaurants, {"ordering": "-average_price"})
        # create  filter obj
        instance = self.filter(request, queryset=queryset)
        filtered_queryset = instance.qs

        self.assertEqual(len(filtered_queryset), len(queryset))
        #  check change ordering qs - before
        self.assertEqual(filtered_queryset[0].id, queryset[0].id)
        # check change ordering qs - after
        self.assertEqual(filtered_queryset.reverse()[0].id, queryset.reverse()[0].id)
        self.assertNotEqual(request.data["results"][0]["title"], queryset[0].title)

    def test_distance_ordering(self):
        user_location = Point(40.7128, -74.0060, srid=4326)
        queryset = (
            Restaurant.objects.annotate(
                average_price=Avg("dishes_restaurant__price"),
                distance=Distance("location", user_location),
            )
            .order_by("distance")
            .distinct()
        )
        request = self.client.get(
            self.url_restaurants,
            {"ordering": "distance", "coordinates": "40.7128,-74.0060"},
        )
        instance = self.filter(request, queryset=queryset)
        filtered_queryset = instance.qs
        self.assertEqual(len(filtered_queryset), len(queryset))
        self.assertEqual(filtered_queryset[0].id, queryset[0].id)
        self.assertEqual(filtered_queryset.reverse()[0].id, queryset.reverse()[0].id)

    def test_detail_restaurants(self):
        url_restaurants_detail = reverse(
            "restaurants:restaurant-detail", args=[self.restaurant1.pk]
        )
        response = self.client.get(url_restaurants_detail)
        self.assertEqual(response.status_code, 200)

        serializer = RestaurantDetailSerializer(self.restaurant1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_number_of_dishes(self):
        serializer = RestaurantDetailSerializer(self.restaurant1)
        self.assertEqual(serializer.get_number_of_dishes(self.restaurant1), 1)
