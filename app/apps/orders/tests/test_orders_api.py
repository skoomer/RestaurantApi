import pytest
import factory
from django.test import TestCase
from django.urls import reverse
from apps.accounts.factories import UserFactory
from apps.orders.factories import OrdersFactory, CartFactory, CartItemsFactory


@pytest.mark.django_db
class TestOrdersApi(TestCase):
    """unittest orders api"""

    def setUp(self):
        self.url_orders = reverse("orders:orders-list")
        self.data_login = {
            "email": "testgmail@mail.com",
            "password": "password1245",
        }
        self.user = UserFactory(
            email=self.data_login["email"],
            password=factory.PostGenerationMethodCall(
                "set_password", self.data_login["password"]
            ),
        )

        self.cart = CartFactory(customer=self.user)
        self.cart_items = CartItemsFactory(cart=self.cart, quantity=1)
        self.orders = OrdersFactory(costumer=self.user, cart=self.cart)
        self.url_order_detail = reverse("orders:orders-detail", args=[self.orders.id])

    def test_get_all_orders_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_orders)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

        self.assertEqual(response.data["results"][0]["costumer_name"], self.user.email)
        self.assertEqual(
            float(response.data["results"][0]["total_price"]), self.orders.total_price
        )
        self.assertEqual(
            response.data["results"][0]["number_dishes"], self.cart_items.quantity
        )

        self.assertEqual(
            response.data["results"][0]["creation_date"],
            self.orders.creation_date.strftime("%d-%m-%Y %H:%M:%S"),
        )
        self.assertEqual(response.data["results"][0]["status"], self.orders.status)

    def test_get_orders_without_user(self):
        response = self.client.get(self.url_orders)
        self.assertEqual(response.status_code, 403)

    def test_get_orders_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_order_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["costumer_name"], self.user.email)
        self.assertEqual(
            response.data["list_of_dishes"][0]["title"], self.cart_items.dish.title
        )

        self.assertEqual(float(response.data["total_price"]), self.orders.total_price)
