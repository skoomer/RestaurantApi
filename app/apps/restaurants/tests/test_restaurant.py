from django.test import TestCase
from apps.restaurants.factories import RestaurantFactory, CuisinesFactory, DishesFactory


class RestaurantTestCase(TestCase):
    """unittest restaurants object"""
    def setUp(self):
        self.restaurant = RestaurantFactory.create()

    def test_restaurant_str(self):
        self.assertEqual(str(self.restaurant), self.restaurant.title)

    def test_cuisines_count(self):
        CuisinesFactory.create_batch(3, restaurants=self.restaurant)
        self.assertEqual(self.restaurant.cuisines.count(), 3)

    def test_dishes_count(self):
        cuisines = CuisinesFactory.create(restaurants=self.restaurant)
        DishesFactory.create_batch(5, cuisines=cuisines)
        self.assertEqual(cuisines.dishes.count(), 5)
