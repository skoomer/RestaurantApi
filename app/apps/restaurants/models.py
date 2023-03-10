from django.db import models
from model_utils import Choices
from django.contrib.gis.db import models as gis_models
from django.utils import timezone


class Restaurant(models.Model):
    """model object"""

    STATUS = Choices("open", "close")

    def upload_to(self, filename):
        return "images/restaurant/{filename}".format(filename=filename)

    title = models.CharField(max_length=100, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    photo = models.ImageField(
        upload_to=upload_to, blank=True, null=True, verbose_name="Photo"
    )
    location = gis_models.PointField(
        srid=4326, geography=True, blank=True, null=True, verbose_name="Location"
    )

    status = models.CharField(
        max_length=10, choices=STATUS, verbose_name="Status", default=STATUS.close
    )
    email = models.EmailField(verbose_name="Email")

    creation_date = models.DateTimeField(
        default=timezone.now, verbose_name="Creation date"
    )

    def __str__(self):
        return self.title


class Cuisines(models.Model):
    """model object"""

    name = models.CharField(max_length=100, verbose_name="cuisines")
    restaurants = models.ManyToManyField(
        Restaurant,
        verbose_name="Restaurants",
        related_name="cuisines",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Dishes(models.Model):
    """model object"""

    title = models.CharField(max_length=100, verbose_name="Dishes name")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(verbose_name="Price", max_digits=6, decimal_places=2)
    like = models.IntegerField(verbose_name="Like a dishes", default=0)
    restaurants = models.ForeignKey(
        Restaurant,
        blank=True,
        null=True,
        related_name="dishes_restaurant",
        on_delete=models.CASCADE,
        verbose_name="Dishes restaurants",
    )
    cuisines = models.ForeignKey(
        Cuisines,
        verbose_name="Cuisines",
        related_name="dishes",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title
