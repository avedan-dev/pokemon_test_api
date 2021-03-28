import factory
from sweets_api.sweets.models import Courier, Order, CouriersAndOrders
import random


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    order_id = factory.Sequence(lambda n: 2 * n + 1)
    weight = random.uniform(0.02, 49)
    region = factory.Sequence(lambda n: random.randint(1, 11))
    delivery_hours = [
        f"{random.randint(0, 11)}:{(random.randint(0, 59))}-{random.randint(12, 23)}:{(random.randint(0, 59))}" for x
        in range(3)]


class CourierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Courier

    courier_id = factory.Sequence(lambda n: n + 1)
    courier_type = random.choice(['foot', 'bike', 'car'])
    regions = random.sample(range(1, 100), 3)
    working_hours = [
        f"{random.randint(0, 11)}:{(random.randint(0, 59))}-{random.randint(12, 23)}:{(random.randint(0, 59))}" for x
        in range(3)]


class CouriersAndOrdersFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CouriersAndOrders
    courier_id = factory.SubFactory(CourierFactory)
    order_id = factory.SubFactory(OrderFactory)


def gen_courier_json(n=1):
    json = {"data": [{
        "courier_id": i + 1,
        "courier_type": random.choice(['foot', 'bike', 'car']),
        "regions": random.sample(range(1, 100), 3),
        "working_hours": [
            f"{random.randint(0, 11)}:{(random.randint(0, 59))}-{random.randint(11, 23)}:{(random.randint(0, 59))}" for
            x in range(3)]} for i in range(n)]}
    return json


def gen_order_json(n=1):
    json = {"data": [{
        "order_id": random.randint(1, 100),
        "weight": random.uniform(0.02, 49),
        "region": random.randint(1, 100),
        "delivery_hours": [
            f"{random.randint(0, 11)}:{(random.randint(0, 59))}-{random.randint(11, 23)}:{(random.randint(0, 59))}" for
            i in range(n)]
    }]}
    return json
