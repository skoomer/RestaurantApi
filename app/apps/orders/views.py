from django.db.models import Q
from django.shortcuts import get_object_or_404
import stripe
from stripe.error import StripeError
from django.conf import settings
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, mixins, response, status
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CartSerializer,
    OrderCreateSerializer,
)
from .models import Order, Cart


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
            cookie_str = self.request.headers.get("Cookie", "")
            cookie_parts = cookie_str.split("; ")

            # Initialize a variable to store the cart_uuid
            cart_uuid = None

            # Loop through the cookie parts to find 'cart_uuid'
            for part in cookie_parts:
                if part.startswith("cart_uuid="):
                    cart_uuid = part[len("cart_uuid="):]

            qs = Cart.objects.filter(customer=None, order=None, cart_uuid=cart_uuid)
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_authenticated is False:
            serializer.save(customer=None)
        serializer.save(customer=self.request.user)


class OrderCreateView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
):
    """Order. Create an order."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentIntentView(viewsets.ViewSet):
    """Stripe api. Payment create view. Add payment id to order"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def create_payment_intent(self, request, pk=None):
        order = get_object_or_404(Order, id=pk, customer=request.user)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Create a Payment Intent for the order
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_price),
                currency="usd",
                payment_method_types=["card"],
                metadata={"order_id": order.id},
            )
            # save intent id in order
            order.intent_id = intent.id
            order.save()
            payment_intent = stripe.PaymentIntent.retrieve(order.intent_id)
            payment_status = payment_intent.status
            return response.Response(
                {
                    "client_secret": intent.client_secret,
                    "payment_status": payment_status,
                    "order_intent": intent.id,
                }
            )

        except StripeError as e:
            # Handle Stripe errors
            return response.Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
