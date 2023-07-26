from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderListView


app_name = "apps.orders"

router = DefaultRouter()

router.register(r"orders", OrderListView, basename="orders")


urlpatterns = [
    path("", include(router.urls)),
]
