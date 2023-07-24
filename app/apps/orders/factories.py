import factory
from django.utils import timezone
from apps.accounts.factories import UserFactory
from apps.restaurants.factories import RestaurantFactory, DishesFactory
from .models import Order, Cart, CartItems


class CartFactory(factory.django.DjangoModelFactory):
    """Used to test  Cart object"""

    class Meta:
        """set model object"""

        model = Cart

    customer = factory.SubFactory(UserFactory)
    restaurant = factory.SubFactory(RestaurantFactory)


class CartItemsFactory(factory.django.DjangoModelFactory):
    """Used to test  Cart object"""

    class Meta:
        """set model object"""

        model = CartItems

    cart = factory.SubFactory(CartFactory)

    dish = factory.SubFactory(DishesFactory)

    quantity = 0


class OrdersFactory(factory.django.DjangoModelFactory):
    """Used to test  Orders object"""

    class Meta:
        """set model object"""

        model = Order

    status = Order.STATUS.in_processing
    restaurant = factory.SubFactory(RestaurantFactory)
    costumer = factory.SubFactory(UserFactory, email=factory.Sequence(lambda n: f'test_email{n}@example.com'))

    total_price = 100.00

    address = "street : test , house : 10, city : Test"
    creation_date = factory.LazyFunction(timezone.now)
    costumer_name = factory.LazyAttribute(lambda o: "%s" % o.costumer)
    cart = factory.SubFactory(CartFactory)
