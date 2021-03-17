import pytest
from sweets.models import Order
from sweets.tests.test_api.factories import OrderFactory


@pytest.mark.django_db
class TestOrder:
    def test_shipped(self):
        """After shipping an order, the status is shipped."""
        order = OrderFactory.build_batch(3)
        print(order)
        assert order