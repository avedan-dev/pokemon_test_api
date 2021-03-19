import factory
from factory.fuzzy import FuzzyFloat, FuzzyChoice
from sweets.models import Courier, Order
import random


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    order_id = factory.Sequence(lambda n: 2 * n + 1)
    weight = FuzzyFloat(0.01, 50)
    region = factory.Sequence(lambda n: random.randint(1, 11))
    delivery_hours = factory.Sequence(lambda
                                          n: f'{random.randint(0, 11)}:{(random.randint(0,59))}-{random.randint(12, 23)}:{(random.randint(0,59))}')


class CourierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Courier

    courier_id = random.randint(1,50)
    courier_type = random.choice(['foot', 'bike', 'car'])
    regions = factory.Sequence(lambda n: [random.randint(1, 11), random.randint(1, 11), random.randint(1, 11)])
    working_hours = [f"{random.randint(0, 11)}:{(random.randint(0,59))}-{random.randint(12, 23)}:{(random.randint(0,59))}" for x
         in range(3)]


def gen_courier_json(n=1):
    json = {"data": [{
        "courier_id": random.randint(1, 100),
        "courier_type": random.choice(['foot', 'bike', 'car']),
        "regions": [random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)],
        "working_hours": [
            f"{random.randint(0, 11)}:{(random.randint(0,59))}-{random.randint(11, 23)}:{(random.randint(0,59))}" for
            x in range(3)]
    } for i in range(n)]}
    return json


class CourierGenerator():
    pass
