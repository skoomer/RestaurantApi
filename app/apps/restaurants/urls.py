from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantListView


app_name = "apps.restaurants"


router = DefaultRouter()
router.register(r"restaurants", RestaurantListView, basename="restaurant")

urlpatterns = [
    path("", include(router.urls)),
]
