from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderListView, CartCreateView, PaymentIntentView


app_name = "apps.orders"

router = DefaultRouter()

router.register(r"orders", OrderListView, basename="orders")
router.register(r"cart", CartCreateView, basename="carts")
router.register(r"payment", PaymentIntentView, basename="payment")


urlpatterns = [
    path("", include(router.urls)),
]
