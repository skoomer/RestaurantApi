from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderListView, CartCreateView, PaymentIntentView, OrderCreateView, StripeWebhookView


app_name = "apps.orders"

router = DefaultRouter()

router.register(r"orders", OrderListView, basename="orders")
router.register(r"cart", CartCreateView, basename="carts")
router.register(r"order-create", OrderCreateView, basename="order-create")
router.register(r"order-payment", PaymentIntentView, basename="payment")


urlpatterns = [
    path("", include(router.urls)),
    path("stripe-webhook/", StripeWebhookView.as_view(), name='stripe_webhook'),
]
