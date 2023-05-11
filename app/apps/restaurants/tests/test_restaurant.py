from django.test import TestCase
from apps.restaurants.factories import RestaurantFactory, CuisinesFactory, DishesFactory


class RestaurantTestCase(TestCase):
    """unittest restaurants object"""

    def setUp(self):
        self.cuisines = CuisinesFactory()
        self.restaurant = RestaurantFactory()
        self.restaurant.cuisines.set([self.cuisines])

    def test_restaurant_str(self):
        self.assertEqual(str(self.restaurant), self.restaurant.title)

    def test_restaurant_with_cuisines(self):
        self.assertTrue(self.restaurant.cuisines.exists())
        self.assertIn(self.restaurant, self.cuisines.restaurants_cuisines.all())

    def test_cuisines_count(self):
        cuisines = CuisinesFactory.create_batch(3)
        self.assertEqual(len(cuisines), 3)

    def test_dishes_count(self):
        DishesFactory.create_batch(5, cuisines=self.cuisines)
        self.assertEqual(self.cuisines.dishes.count(), 5)
