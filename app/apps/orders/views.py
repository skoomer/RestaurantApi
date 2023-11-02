from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import stripe
from stripe.error import StripeError
from django.conf import settings
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, mixins, response, status, views
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
            cart_uuid = self.request.GET.get("cart_uuid")
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


class PaymentIntentView(viewsets.ViewSet):
    """Stripe api. Payment create view. Add payment id to order"""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def checkout_payment_intent(self, payment_intent_id, pk=None):
        # Create a checkout session
        try:
            payment_intent = self.request.data.get("payment_intent")
            try:
                order = Order.objects.get(intent_id=payment_intent)
            except Order.DoesNotExist:
                return response.Response(
                    {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
                )
            stripe.api_key = settings.STRIPE_SECRET_KEY
            line_items = []
            for cart_item in order.cart.cart_items.all():
                line_item = {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": cart_item.dish.title,
                        },
                        "unit_amount": int(cart_item.dish.price * 100),
                    },
                    "quantity": cart_item.quantity,
                }
                line_items.append(line_item)
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=[
                    "card",
                ],
                customer_email=self.request.user.email,
                line_items=line_items,
                mode="payment",
                success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://127.0.0.1:8000/" + "cancel",
                payment_intent_data={
                    "description": f"Payment for {payment_intent}",
                    "setup_future_usage": "on_session",
                },
            )
            # Return the checkout session ID as JSON response
            return response.Response({"checkout_session_id": checkout_session.id})
        except stripe.error.StripeError as e:
            return response.Response(
                {
                    "error": f"Something went wrong when creating stripe checkout session: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(views.APIView):
    """this webhook catches stripe calls and receives a notification that a payment has been made"""

    permission_classes = [permissions.AllowAny]

    @csrf_exempt
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_intent = self.request.data.get("payment_intent")
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        payload = request.body

        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            print("Error parsing payload: {}".format(str(e)))
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print("Error verifying webhook signature: {}".format(str(e)))
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event["type"] == "checkout.session.completed":
            print("Sessions was completed!")
        elif event.type == "payment_intent.succeeded":
            print("PaymentIntent was successful!")
            order = Order.objects.get(intent_id=payment_intent)
            order.status = Order.STATUS.completed
            order.save()

        elif event["type"] == "requires_payment_method":
            print("PaymentIntent requires_payment_method!")
        else:
            print("Unhandled event type {}".format(event.type))

        return response.Response(status=status.HTTP_200_OK)
