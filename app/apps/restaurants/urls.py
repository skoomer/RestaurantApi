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
]

urlpatterns = format_suffix_patterns(urlpatterns)
