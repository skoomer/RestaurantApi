from django.db import models
from model_utils import Choices
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from apps.accounts.models import User


class Cuisines(models.Model):
    """model object"""

    name = models.CharField(max_length=100, verbose_name=_("cuisines"))

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """model object"""

    STATUS = Choices("open", "close")

    def upload_to(self, filename):
        return "images/restaurant/{filename}".format(filename=filename)

    title = models.CharField(max_length=100, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    photo = models.ImageField(
        upload_to=upload_to, blank=True, null=True, verbose_name=_("Photo")
    )
    location = gis_models.PointField(
        srid=4326, geography=True, blank=True, null=True, verbose_name=_("Location")
    )

    status = models.CharField(
        max_length=10, choices=STATUS, verbose_name=_("Status"), default=STATUS.close
    )
    email = models.EmailField(verbose_name=_("Email"))

    creation_date = models.DateTimeField(
        default=timezone.now, verbose_name=_("Creation date")
    )

    cuisines = models.ManyToManyField(
        Cuisines,
        verbose_name=_("Cuisines"),
        related_name="restaurants_cuisines",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title


class Dishes(models.Model):
    """model object"""

    title = models.CharField(max_length=100, verbose_name=_("Dishes name"))
    description = models.TextField(verbose_name=_("Description"))
    price = models.DecimalField(verbose_name=_("Price"), max_digits=6, decimal_places=2)
    like_user = ArrayField(
        models.IntegerField(),
        default=list,
        verbose_name=_("Like a dishes"),
        blank=True,
        null=True,
    )
    restaurants = models.ForeignKey(
        Restaurant,
        blank=True,
        null=True,
        related_name="dishes_restaurant",
        on_delete=models.CASCADE,
        verbose_name=_("Dishes restaurants"),
    )
    cuisines = models.ForeignKey(
        Cuisines,
        verbose_name=_("Cuisines"),
        related_name="dishes",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title


class Review(models.Model):
    """model object"""

    reviewer = models.ForeignKey(
        User,
        related_name="reviewer_user",
        on_delete=models.CASCADE,
        verbose_name="Reviewer",
        blank=True,
        null=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="restaurant_review",
        on_delete=models.CASCADE,
        verbose_name="Restaurants",
    )
    message = models.TextField(verbose_name="User message")
    creation_date = models.DateTimeField(
        default=timezone.now, verbose_name=_("Creation date")
    )

    def __str__(self):
        return self.reviewer.first_name
