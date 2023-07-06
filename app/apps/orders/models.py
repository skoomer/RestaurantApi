from django.db import models
from model_utils import Choices
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.accounts.models import User
from apps.restaurants.models import Restaurant, Dishes


class Cart(models.Model):
    """model object cart"""

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart", verbose_name="customer"
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="cart", verbose_name="restaurant"
    )

    def __str__(self):
        return f"Cart {self.id}"


class CartItems(models.Model):
    """model object cart items"""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Cart",
    )
    dish = models.ForeignKey(
        Dishes,
        on_delete=models.CASCADE,
        related_name="cart_item_dishes",
        verbose_name="dish",
    )
    quantity = models.PositiveIntegerField(verbose_name="quantity dishes")

    def __str__(self):
        return f"Cart items {self.id}"


class Order(models.Model):
    """model object orders api"""

    STATUS = Choices("in_processing", "delivered", "completed", "canceled")
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="order",
        verbose_name="Restaurant",
    )
    costumer = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="costumer", related_name="costumer"
    )

    creation_date = models.DateTimeField(
        default=timezone.now, verbose_name=_("Creation date")
    )
    total_price = models.DecimalField(
        verbose_name=_("Total price"), max_digits=6, decimal_places=2
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS,
        verbose_name=_("Status"),
        default=STATUS.in_processing,
    )

    address = models.CharField(max_length=200, verbose_name="address delivery")
    costumer_name = models.CharField(verbose_name="costumer name", max_length=100)

    def __str__(self):
        return f"Order number {self.id}"
