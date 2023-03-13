import pytest
from django.test import TestCase
from django.urls import reverse
from apps.restaurants.factories import RestaurantFactory, CuisinesFactory, DishesFactory
from apps.restaurants.models import Restaurant
from django.contrib.gis.geos import Point
from apps.restaurants.filters import RestaurantFilter


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

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant2.title)

    def test_filter_by_title(self):

        data = {"search": self.restaurant3.title}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant3.title)

    def test_filter_by_price_gt(self):
        data = {"min_price": 20.0}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant3.title)

    def test_filter_by_price_lt(self):
        data = {"max_price": 20.0}
        response = self.client.get(self.url_restaurants, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_restaurants_filter_by_price_range(self):
        response = self.client.get(
            self.url_restaurants, data={"min_price": 12, "max_price": 22}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.restaurant2.title)

    def test_filter_restaurants_by_coordinates(self):
        query_params = {"coordinates": "2,2"}
        instance = RestaurantFilter(query_params, queryset=Restaurant.objects.all())
        queryset = instance.qs

        self.assertEqual(queryset.count(), 3)
        self.assertEqual(queryset.first(), self.restaurant2)
        self.assertEqual(queryset.last(), self.restaurant1)

    def test_filter_restaurants_by_invalid_coordinates(self):
        query_params = {"coordinates": "invalid"}
        instance = RestaurantFilter(query_params, queryset=Restaurant.objects.all())
        queryset = instance.qs

        self.assertEqual(queryset.count(), 0)
