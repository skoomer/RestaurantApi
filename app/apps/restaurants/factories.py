import factory
from django.contrib.gis.geos import Point
from .models import Restaurant, Cuisines, Dishes


class RestaurantFactory(factory.django.DjangoModelFactory):
    """Used to test  Restaurant object"""

    class Meta:
        """set model object"""

        model = Restaurant

    title = "test"
    description = "description restaurant"
    photo = factory.django.ImageField(color="blue")
    location = Point(10.0, 20.0)
    status = Restaurant.STATUS.open
    email = factory.LazyAttribute(lambda o: "%s@example.org" % o.title)


class CuisinesFactory(factory.django.DjangoModelFactory):
    """Used to test  Restaurant object"""

    class Meta:
        """set model object"""

        model = Cuisines

    name = "test_cuisines"
    restaurants = factory.SubFactory(RestaurantFactory)


class DishesFactory(factory.django.DjangoModelFactory):
    """Used to test  Restaurant object"""

    class Meta:
        """set model object"""

        model = Dishes

    title = "test_dishes"
    description = "description dishes"
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    like = factory.Faker("random_int", min=0, max=100)
    cuisines = factory.SubFactory(CuisinesFactory)
