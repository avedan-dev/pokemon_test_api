import factory
from sweets.models import Courier


class CourierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Courier

print(CourierFactory())
(CourierFactory.create_batch(3))