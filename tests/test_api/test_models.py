import pytest
from tests.test_api.factories import OrderFactory, CourierFactory
from pokemon.pokemon.models import Order, Courier


@pytest.mark.django_db
class TestOrder:
    def test_order_create(self):
        OrderFactory.create_batch(3)
        assert len(Order.objects.all()) == 3


@pytest.mark.django_db
class TestCourier:
    def test_courier_create(self):
        CourierFactory.create_batch(3)
        assert len(Courier.objects.all()) == 3


@pytest.mark.django_db
class TestManyOrders:
    def test_many_orders_create(self):
        OrderFactory.create_batch(1000)
        assert len(Order.objects.all()) == 1000


@pytest.mark.django_db
class TestManyCouriers:
    def test_many_couriers_create(self):
        CourierFactory.create_batch(1000)
        assert len(Courier.objects.all()) == 1000
