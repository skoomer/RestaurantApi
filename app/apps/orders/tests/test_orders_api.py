import pytest
import factory
from django.test import TestCase
from django.urls import reverse
from apps.accounts.factories import UserFactory
from apps.restaurants.factories import DishesFactory, RestaurantFactory
from apps.orders.factories import OrdersFactory, CartFactory, CartItemsFactory
from apps.orders.models import Cart


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

        self.restaurant = RestaurantFactory()
        self.cart = CartFactory(customer=self.user, restaurant=self.restaurant)
        self.orders = OrdersFactory(
            cart=self.cart, customer=self.user, restaurant=self.restaurant
        )
        self.cart_items = CartItemsFactory(cart=self.cart, quantity=1)
        self.url_order_detail = reverse("orders:orders-detail", args=[self.orders.id])
        self.dish = DishesFactory()

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

        self.assertEqual(response.status_code, 201)
        self.assertTrue("id" in response.data)

        self.assertEqual(
            response.data["cart_items"][0]["dish"], data["cart_items"][0]["dish"]
        )
        self.assertEqual(
            response.data["cart_items"][0]["quantity"],
            data["cart_items"][0]["quantity"],
        )
        total_price = self.dish.price * data["cart_items"][0]["quantity"]

        # # check total price
        self.assertEqual(
            response.data["cart_items"][0]["total_price"],
            total_price,
        )

        # counting the quantity of objects in the cart, if this dish is already in the cart - increase the quantity
        response = self.client.post(
            cart_create_url, data, content_type="application/json"
        )
        self.assertNotEqual(
            response.data["cart_items"][0]["quantity"],
            data["cart_items"][0]["quantity"],
        )

    def test_create_cart_if_cart_order_exists(self):
        restaurant = RestaurantFactory()
        dish = DishesFactory(restaurants=restaurant)
        cart = CartFactory(customer=self.user, restaurant=restaurant)
        orders = OrdersFactory(
            cart_id=cart.id, customer=self.user, restaurant=restaurant
        )

        self.client.force_login(self.user)
        data = {
            "customer": self.user.email,
            "cart_items": [
                {
                    "dish": dish.id,
                    "quantity": 2,
                }
            ],
        }
        cart_create_url = reverse("orders:carts-list")

        # get cart with orders,restaurant,customer
        cart_order_exists = Cart.objects.filter(
            order=orders, restaurant=restaurant, customer=self.user
        )
        self.assertTrue(cart_order_exists.exists())

        response = self.client.post(
            cart_create_url, data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(
            response.data["id"], cart_order_exists.values("id")[0]["id"]
        )

    def test_cart_add_new_items(self):
        dish = DishesFactory(restaurants=self.restaurant)
        dish_2 = DishesFactory(restaurants=self.restaurant)

        self.client.force_login(self.user)
        data = {
            "customer": self.user.email,
            "cart_items": [
                {
                    "dish": dish.id,
                    "quantity": 33,
                }
            ],
        }

        add_new_item_data = {
            "customer": self.user.email,
            "cart_items": [
                {
                    "dish": dish_2.id,
                    "quantity": 33,
                }
            ],
        }
        cart_create_url = reverse("orders:carts-list")

        # create cart with item
        response = self.client.post(
            cart_create_url, data, content_type="application/json"
        )
        new_cart = Cart.objects.get(id=response.data["id"])

        # add new item to cart
        response = self.client.post(
            cart_create_url, add_new_item_data, content_type="application/json"
        )
        # check that the quantity has changed after the request
        self.assertEqual(new_cart.cart_items.all().count(), 2)
        self.assertEqual(
            response.data["cart_items"][1]["dish"],
            add_new_item_data["cart_items"][0]["dish"],
        )
        self.assertEqual(response.status_code, 201)
