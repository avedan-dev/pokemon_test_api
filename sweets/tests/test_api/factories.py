import factory
from sweets.models import Courier, Order


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    order_id = factory.Sequence(lambda n: 2*n)

