from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import RestaurantListView

app_name = "apps.restaurants"
urlpatterns = [
    path(
        "restaurants/",
        RestaurantListView.as_view(
            {
                "get": "list",
            }
        ),
        name="restaurant-list",
    ),
    path(
        "restaurants/",
        RestaurantListView.as_view(
            {
                "post": "retrieve",
            }
        ),
        name="restaurant-create",
    ),
    path(
        "restaurants/<int:pk>/",
        RestaurantListView.as_view(
            {
                "get": "retrieve",
            }
        ),
        name="restaurant-detail",
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
