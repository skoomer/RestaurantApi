from django.contrib import admin
from django.contrib.gis import admin as geoadmin
from .models import Restaurant, Cuisines, Dishes


class CuisinesInline(admin.TabularInline):
    """inline filed cuisines for restaurant list display"""
    model = Restaurant.cuisines.through


class RestaurantAdmin(geoadmin.OSMGeoAdmin):
    """add restaurant model to dashboard admin"""

    list_display = ["title", "description", "status", "email"]
    inlines = [CuisinesInline]


class CuisinesAdmin(admin.ModelAdmin):
    """add cuisines model to dashboard admin"""

    list_display = ["name"]


class DishesAdmin(admin.ModelAdmin):
    """add dishes model to dashboard admin"""

    list_display = [
        "title",
        "description",
        "price",
        "like_user",
        "restaurants",
        "cuisines",
    ]


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Cuisines, CuisinesAdmin)
admin.site.register(Dishes, DishesAdmin)
