from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantListView, MenuEndpointViews, ReViewRestaurant


app_name = "apps.restaurants"


router = DefaultRouter()
router.register(r"restaurants", RestaurantListView, basename="restaurant")
router.register(r'restaurants/(?P<restaurant_pk>\d+)/menu', MenuEndpointViews, basename='cuisines-menu')
router.register(r'restaurants/(?P<restaurant_pk>\d+)/review', ReViewRestaurant, basename='restaurant-review')


urlpatterns = [
    path("", include(router.urls)),
]
