import uuid
from django.db.models import Q
import stripe
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework import viewsets, permissions, mixins, response, status
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CartSerializer,
    OrderCreateSerializer,
)
from .models import Order, Cart

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderListView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """List of orders with fields: customer name,
    date, total price, number of dishes, status.Orders API for a logged in user"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        qs = Order.objects.filter(customer=self.request.user)
        return qs

    def get_serializer_class(self):
        """on assignment. in the detailed information
        about the restaurant"""
        if self.action == "retrieve":
            return OrderDetailSerializer

        return self.serializer_class


class CartCreateView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """create cart"""

    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = Cart.objects.filter(Q(customer=self.request.user) | Q(customer=None))

        else:
            qs = Cart.objects.filter(customer=None, order=None)
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_authenticated is False:
            cart_uuid = uuid.uuid4()
            cart = serializer.save(customer=None)
            cart.cart_uuid = cart_uuid
            cart.save()
            return response.Response(
                {"cart_uuid": cart_uuid}, status=status.HTTP_201_CREATED
            )

        serializer.save(customer=self.request.user)
        return response.Response(
            {"cart_uuid": serializer.instance.cart_uuid},
            status=status.HTTP_201_CREATED,
        )


class PaymentIntentView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    """Payments. Complete an order with a payment."""

    permission_classes = [permissions.AllowAny]
    serializer_class = OrderCreateSerializer

    def get_queryset(self):
        token = self.request.data.get("cart_uuid")
        qs = Order.objects.filter(cart__cart_uuid=token)
        return qs

    def create(self, request, *args, **kwargs):

        token = request.data.get("cart_uuid")

        if not request.user.is_authenticated:
            next_url = reverse("orders:payment-list")
            login_url = reverse("account_login") + "?next=" + next_url
            return redirect(login_url)

        try:

            cart = Cart.objects.get(cart_uuid=token)
            cart.customer = self.request.user
            cart.save()
        except Cart.DoesNotExist:
            return response.Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if cart.customer != self.request.user:
            return response.Response(
                {"error": "Unauthorized access to the cart"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # Create a Stripe payment intent
        intent = stripe.PaymentIntent.create(
            currency="usd",
            payment_method_types=["card"],
            metadata={
                "customer_name": request.data.get("customer_name"),
                "address": request.data.get("address"),
                "list_of_dishes": cart.cart_items.all(),
            },
        )
        serializer.save()

        return response.Response(
            {
                "total": serializer.instance.total_price,
                "client_secret": intent.client_secret,
            },
            status=status.HTTP_201_CREATED,
        )
