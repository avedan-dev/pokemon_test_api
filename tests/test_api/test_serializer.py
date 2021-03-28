import pytest
import factory
from sweets_api.sweets.serializers import CourierSerializer, OrderSerializer, \
    AssignSerializer, CompleteSerializer
from tests.test_api.factories import CourierFactory, OrderFactory, \
    CouriersAndOrdersFactory

pytestmark = pytest.mark.django_db


class TestCourierSerializer:
    def test_serialize_model(self):
        currency = CourierFactory.build()
        serializer = CourierSerializer(currency)
        assert serializer.data

    def test_serialized_data(self):
        valid_serialized_data = factory.build(
            dict,
            FACTORY_CLASS=CourierFactory
        )

        serializer = CourierSerializer(data=valid_serialized_data)
        serializer.is_valid()
        assert serializer.is_valid()
        assert serializer.errors == {}


class TestOrderSerializer:
    def test_serialize_model(self):
        currency = OrderFactory.build()
        serializer = OrderSerializer(currency)
        assert serializer.data

    def test_serialized_data(self):
        valid_serialized_data = factory.build(
            dict,
            FACTORY_CLASS=OrderFactory
        )

        serializer = OrderSerializer(data=valid_serialized_data)
        serializer.is_valid()
        assert serializer.is_valid()
        assert serializer.errors == {}


class TestAssignSerializer:
    def test_serialized_data(self):
        courier = CourierFactory.create()
        order = OrderFactory.create()
        valid_serialized_data = factory.build(
            dict,
            courier_id=courier.courier_id,
            order_id=order.order_id,
        )
        serializer = AssignSerializer(data=valid_serialized_data)
        serializer.is_valid()
        assert serializer.is_valid()
        assert serializer.errors == {}


class TestCompleteSerializer:
    def test_serialized_data(self):
        courier = CourierFactory.create()
        order = OrderFactory.create()
        CouriersAndOrdersFactory.create(courier_id=courier, order_id=order)
        valid_serialized_data = factory.build(
            dict,
            courier_id=courier.courier_id,
            order_id=order.order_id,
            complete_time='2031-01-10T10:33:01.42Z',
        )
        serializer = CompleteSerializer(data=valid_serialized_data)
        serializer.is_valid()
        assert serializer.is_valid()
        assert serializer.errors == {}
