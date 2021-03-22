import pytest
from tests.test_api.factories import OrderFactory, CourierFactory


@pytest.mark.django_db
class TestOrder:
    def test_order_create(self):
        order = OrderFactory.build_batch(3)
        assert order


@pytest.mark.django_db
class TestCourier:
    def test_courier_create(self):
        courier = CourierFactory.build_batch(3)
        assert courier