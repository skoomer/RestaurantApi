import uuid
import time
import hmac
import hashlib
import json
import stripe
import pytest
import factory
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from django.urls import reverse
from apps.accounts.factories import UserFactory
from apps.restaurants.factories import DishesFactory, RestaurantFactory
from apps.orders.factories import OrdersFactory, CartFactory, CartItemsFactory
from apps.orders.models import Cart, Order
from django.conf import settings


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
        self.user2 = UserFactory(
            email="user2@gmail.com",
            password=factory.PostGenerationMethodCall(
                "set_password", self.data_login["password"]
            ),
        )

        self.restaurant = RestaurantFactory()
        self.cart = CartFactory(customer=self.user, restaurant=self.restaurant)
        self.orders = OrdersFactory(
            cart=self.cart, customer=self.user, restaurant=self.restaurant
        )
        self.url_order_detail = reverse("orders:orders-detail", args=[self.orders.id])
        self.url_cart_detail = reverse("orders:carts-detail", args=[self.cart.id])
        self.url_cart_list = reverse("orders:carts-list")

        self.dish = DishesFactory()
        self.cart_items = CartItemsFactory(cart=self.cart, quantity=1, dish=self.dish)
        self.order_create_url = reverse("orders:order-create-list")

    def test_get_carts_with_user_and_without_user(self):
        cart_2 = CartFactory.create(customer=None, restaurant=self.restaurant)
        url_cart_list = reverse("orders:carts-list")
        data = {"cart_uuid": cart_2.cart_uuid}

        # get cart if user is un authorized and without order
        response = self.client.get(
            url_cart_list, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], cart_2.id)
        self.assertIsNone(response.data["results"][0]["customer"])
        self.assertFalse(response.data["results"][0]["order"])

        # auth user get cart with customer and cart without customer
        self.client.force_login(self.user)
        response = self.client.get(url_cart_list)
        self.assertEqual(len(response.data["results"]), 2)

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

    def test_delete_object_from_cart_items(self):
        url_cart_detail = reverse("orders:carts-detail", args=[self.cart.id])

        dish_2 = DishesFactory()
        # add cart items to cart
        new_cart_items = CartItemsFactory(cart=self.cart, dish=dish_2)

        self.client.force_login(self.user)

        data = {
            "cart_items": [
                {"dish": new_cart_items.dish.id, "quantity": 0},
                {"dish": self.cart_items.dish.id, "quantity": 1},
            ]
        }

        response = self.client.get(url_cart_detail, data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.cart.cart_items.all().count(), 2)

        # update cart items / delete object cart_items from cart set quantity 0
        response = self.client.put(
            self.url_cart_detail, data, content_type="application/json"
        )
        self.assertEqual(self.cart.cart_items.all().count(), 1)

    def test_update_quantity_dish_in_cart_items(self):
        self.client.force_login(self.user)

        data = {"cart_items": [{"dish": self.dish.id, "quantity": 2}]}
        # get cart and check default values
        response = self.client.get(self.url_cart_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cart_items"][0]["quantity"], 1)
        self.assertEqual(
            response.data["cart_items"][0]["total_price"],
            self.dish.price,
        )

        # update cart items
        response = self.client.put(
            self.url_cart_detail, data, content_type="application/json"
        )
        # check change quantity after request
        self.assertEqual(response.data["cart_items"][0]["quantity"], 2)

        # and check total price,after change quantity
        total_price = self.dish.price * data["cart_items"][0]["quantity"]
        self.assertEqual(
            response.data["cart_items"][0]["total_price"],
            total_price,
        )

    def test_delete_cart_if_cart__items_empty(self):
        self.client.force_login(self.user)

        data = {"cart_items": [{"dish": self.cart_items.dish.id, "quantity": 0}]}
        # check  cart,cart_items
        response = self.client.get(self.url_cart_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.cart.cart_items.all().count(), 1)

        # update cart items
        response = self.client.put(
            self.url_cart_detail, data, content_type="application/json"
        )
        # check cart exists, must eq False
        cart = Cart.objects.filter(id=self.cart.id).exists()
        self.assertFalse(cart)

    def test_order_create(self):
        self.client.force_login(self.user)
        cart = CartFactory(customer=self.user, restaurant=self.restaurant)

        data = {
            "address": "test address",
            "customer_name": "test name",
            "cart_uuid": cart.cart_uuid,
            "cart": cart.id
        }
        response = self.client.post(self.order_create_url, data=data)
        self.assertEqual(response.status_code, 201)
        # Check if order create successful
        order = Order.objects.filter(id=response.data["id"]).exists()
        self.assertTrue(order)

    @pytest.mark.vcr()
    def test_payment_intent_authenticated_user(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = UserFactory(email="new_user@gmail.com")
        cart = CartFactory(customer=user, restaurant=self.restaurant)
        CartItemsFactory(cart=cart)
        order = OrdersFactory(customer=user, cart=cart)

        payment_url = reverse("orders:payment-create-payment-intent", args=[order.id])
        self.client.force_login(user)
        response = self.client.post(payment_url)
        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        # # Check if the order's intent_id is set and saved
        self.assertEqual(order.intent_id, response.json()["order_intent"])

    def test_create_payment_intent_with_unauthenticated_user(self):
        order = OrdersFactory(customer=self.user, cart=self.cart)
        payment_url = reverse("orders:payment-create-payment-intent", args=[order.id])
        response = self.client.post(payment_url)
        self.assertEqual(response.status_code, 403)

    def test_create_order_with_invalid_cart_uuid(self):
        user = UserFactory()

        cart_invalid_uuid = uuid.uuid4()
        invalid_data = {
            "address": "test address",
            "customer_name": "test name",
            "cart_uuid": cart_invalid_uuid,
        }

        self.client.force_login(user)

        try:
            response = self.client.post(self.order_create_url, invalid_data)
            self.assertEqual(response.status_code, 400)
        except ValidationError as e:
            self.assertIn("Cart not found", str(e.detail))

    def test_stripe_webhook(self):
        pass

    @pytest.mark.vcr()
    def test_checkout_payment_intent(self):
        self.client.force_login(self.user)
        url = reverse('orders:payment-checkout-payment-intent', args=[self.orders.intent_id])
        data = {
            "payment_intent": self.orders.intent_id
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('checkout_session_id', response.data)

    @pytest.mark.vcr()
    def test_checkout_session_completed(self):
        webhook_secret = settings.WEBHOOK_SECRET
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = UserFactory(email="new_user@gmail.com")
        cart = CartFactory(customer=user, restaurant=self.restaurant)
        CartItemsFactory(cart=cart)
        order = OrdersFactory(customer=user, cart=cart)

        payment_url = reverse("orders:payment-create-payment-intent", args=[order.id])
        self.client.force_login(user)
        req = self.client.post(payment_url)
        order.refresh_from_db()
        order_intent = req.data['order_intent']
        payload = {
            "type": "payment_intent.succeeded",
            "payment_intent": order_intent,
            "amount": 20
        }
        payload_json = json.dumps(payload)
        url = reverse("orders:stripe_webhook")

        # Generate a valid timestamp
        timestamp = str(int(time.time()))

        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            msg=(f'{timestamp},{payload_json}').encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        signature = f't={timestamp},v1={expected_signature}'

        response = self.client.post(
            url,
            data=payload_json,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )

        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
