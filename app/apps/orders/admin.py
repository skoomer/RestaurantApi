from django.contrib import admin
from .models import Order, Cart, CartItems


class OrderAdmin(admin.ModelAdmin):
    """add Orders model to dashboard admin"""

    list_display = ["id", "restaurant", "status", "total_price"]


class CartAdmin(admin.ModelAdmin):
    """add Cart model to dashboard admin"""

    list_display = ["id", "customer", "restaurant"]


class CartItemsAdmin(admin.ModelAdmin):
    """add CartItems model to dashboard admin"""

    list_display = ["id", "cart", "dish", "quantity"]


admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItems, CartItemsAdmin)
