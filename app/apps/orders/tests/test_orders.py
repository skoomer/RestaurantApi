from django.test import TestCase
from apps.orders.factories import CartFactory, CartItemsFactory, OrdersFactory


class CartTestCase(TestCase):
    """unittest cart model object"""

    def test_cart_creation(self):
        cart = CartFactory()
        self.assertEqual(str(cart), f"Cart {cart.id}")


class CartItemsTestCase(TestCase):
    """unittest cart items model object"""

    def test_cart_items_creation(self):
        cart = CartFactory()
        cart_item = CartItemsFactory(cart=cart)
        self.assertEqual(str(cart_item), f"Cart items {cart_item.id}")

    def test_cart_items_quantity(self):
        cart_item = CartItemsFactory(quantity=5)
        self.assertEqual(cart_item.quantity, 5)

    def test_cart_items_dishes(self):
        cart_item = CartItemsFactory()
        self.assertIsNotNone(cart_item.dishes)


class OrdersTestCase(TestCase):
    """unittest orders model object"""

    def test_order_creation(self):
        order = OrdersFactory()
        self.assertEqual(str(order), f"Order number {order.id}")
