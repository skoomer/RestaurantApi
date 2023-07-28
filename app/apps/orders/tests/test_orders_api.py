import pytest
import factory
from django.test import TestCase
from django.urls import reverse
from apps.accounts.factories import UserFactory
from apps.restaurants.factories import DishesFactory, RestaurantFactory
from apps.orders.factories import OrdersFactory, CartFactory, CartItemsFactory
from apps.orders.models import CartItems
from apps.orders.serializers import CartItemSerializer


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
        self.orders = OrdersFactory(cart=self.cart, customer=self.user)
        self.cart_items = CartItemsFactory(cart=self.cart, quantity=1)
        self.url_order_detail = reverse("orders:orders-detail", args=[self.orders.id])
        self.dish = DishesFactory()
        self.restaurant = RestaurantFactory()

    def test_get_all_orders_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_orders)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

        self.assertEqual(response.data["results"][0]["customer_name"], self.user.email)
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
        self.assertEqual(response.data["customer_name"], self.user.email)
        self.assertEqual(
            response.data["list_of_dishes"][0]["title"], self.cart_items.dish.title
        )

        self.assertEqual(float(response.data["total_price"]), self.orders.total_price)

    def test_cart_create_with_cart_items(self):
        self.client.force_login(self.user)
        data = {
            "customer": self.user.email,
            "cart_items": [
                {
                    "dish": self.dish.id,
                    "quantity": 2,
                }
            ],
        }
        cart_create_url = reverse("orders:carts-list")

        response = self.client.post(
            cart_create_url, data, content_type="application/json"
        )

        cart_item = CartItems(id=response.data["id"], dish=self.dish, quantity=2)
        serializer = CartItemSerializer(cart_item)

        self.assertEqual(response.status_code, 201)
        self.assertTrue("id" in response.data)
        self.assertEqual(
            response.data["cart_items"][0]["dish"], data["cart_items"][0]["dish"]
        )
        self.assertEqual(
            response.data["cart_items"][0]["quantity"],
            data["cart_items"][0]["quantity"],
        )
        # check total price
        self.assertEqual(
            response.data["cart_items"][0]["total_price"],
            serializer.get_total_price(obj=cart_item),
        )

        # counting the quantity of objects in the cart, if this dish is already in the cart - increase the quantity
        response = self.client.post(
            cart_create_url, data, content_type="application/json"
        )
        self.assertNotEqual(
            response.data["cart_items"][0]["quantity"],
            data["cart_items"][0]["quantity"],
        )
