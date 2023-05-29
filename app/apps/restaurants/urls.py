from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantListView, MenuEndpointViews


app_name = "apps.restaurants"


router = DefaultRouter()
router.register(r"restaurants", RestaurantListView, basename="restaurant")
router.register(r'restaurants/(?P<restaurant_pk>\d+)/menu', MenuEndpointViews, basename='cuisines-menu')


urlpatterns = [
    path("", include(router.urls)),

    path(
        "restaurants/<int:pk>/menu/<int:dish_pk>/like/",
        MenuEndpointViews.as_view(
            {
                "post": "like_dish",
            }
        ),
        name="like_dish",
    ),
]
