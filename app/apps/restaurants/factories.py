import factory
from django.contrib.gis.geos import Point
from django.utils import timezone
from .models import Restaurant, Cuisines, Dishes


class RestaurantFactory(factory.django.DjangoModelFactory):
    """Used to test  Restaurant object"""

    class Meta:
        """set model object"""

        model = Restaurant

    title = factory.Sequence(lambda n: "Restaurant%s" % n)
    description = factory.Sequence(lambda n: "Description%s" % n)
    photo = factory.django.ImageField(color="blue")
    location = Point(10.0, 20.0)
    status = Restaurant.STATUS.open
    creation_date = factory.LazyFunction(timezone.now)
    email = factory.LazyAttribute(lambda o: "%s@example.org" % o.title)


class CuisinesFactory(factory.django.DjangoModelFactory):
    """Used to test  Restaurant object"""

    class Meta:
        """set model object"""

        model = Cuisines

    name = factory.Sequence(lambda n: "Cuisines%s" % n)
    restaurants = factory.SubFactory(RestaurantFactory)


class DishesFactory(factory.django.DjangoModelFactory):
    """Used to test  Restaurant object"""

    class Meta:
        """set model object"""

        model = Dishes

    title = factory.Sequence(lambda n: "Dishes%s" % n)
    description = "description dishes"
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    like_user = None
    cuisines = factory.SubFactory(CuisinesFactory)
