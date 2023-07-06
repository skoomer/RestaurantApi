from django.test import TestCase
from apps.orders.factories import OrdersFactory
from apps.restaurants.factories import RestaurantFactory


class OrdersTestCase(TestCase):
    """unittest orders model object"""

    def setUp(self):
        self.orders = OrdersFactory()
        self.restaurant = RestaurantFactory

    def test_order_str(self):
        self.assertEqual(str(self.orders), str(self.orders))

    def test_orders_with_restaurant(self):
        self.assertIsNotNone(self.orders.restaurant)
        self.assertEqual(self.orders.restaurant, self.restaurant)
