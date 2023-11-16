from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderListView, CartCreateView


app_name = "apps.orders"

router = DefaultRouter()

router.register(r"orders", OrderListView, basename="orders")
router.register(r"cart", CartCreateView, basename="carts")


urlpatterns = [
    path("", include(router.urls)),
]
