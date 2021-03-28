import pytest
from tests.test_api.factories import CourierFactory, OrderFactory
import datetime as dt
import pytz
from sweets_api.sweets.models import Courier
import factory

order_valid_list = [OrderFactory.build(order_id=1, weight=5.0, region=2, delivery_hours=['9:00-12:01']),
                    OrderFactory.build(order_id=2, weight=7.0, region=2, delivery_hours=['13:59-16:00']),
                    OrderFactory.build(order_id=3, weight=7.0, region=2, delivery_hours=['13:00-13:30']),
                    OrderFactory.build(order_id=4, weight=7.0, region=2, delivery_hours=['12:00-14:00'])]

order_invalid_list = [OrderFactory.build(order_id=5, weight=5.0, region=2, delivery_hours=['9:00-12:00']),
                      OrderFactory.build(order_id=6, weight=7.0, region=2, delivery_hours=['14:00-16:00'])]

pytestmark = pytest.mark.django_db


class TestCouriersEndpoints:
    def test_post_couriers(self, api_client):
        endpoint = '/couriers'
        courier_json = {'data': factory.build_batch(dict, 3, FACTORY_CLASS=CourierFactory)}
        expected_response = {"couriers": [{"id": courier_json['data'][i]['courier_id']} for i in range(3)]}
        response = api_client().post(endpoint, courier_json, format='json')
        assert response.status_code == 201
        assert expected_response == response.data

    def test_post_couriers_invalid(self, api_client):
        endpoint = '/couriers'
        courier_json = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22], },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "regions": [12, 22, 23, 33],
                    "working_hours": []
                },
            ]}
        expected_response = {"validation_error": {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]}}
        response = api_client().post(endpoint, courier_json, format='json')
        assert response.status_code == 400
        assert expected_response == response.data

    def test_patch(self, api_client):
        endpoint = '/couriers/'

        courier = CourierFactory.create()

        endpoint += str(courier.courier_id)

        response = api_client().patch(endpoint, {'regions': [1, 2, 3]}, format='json')

        assert response.status_code == 200
        assert response.data['regions'] == [1, 2, 3]

        response = api_client().patch(endpoint, {'courier_type': 'foot'}, format='json')

        assert response.status_code == 200
        assert response.data['courier_type'] == 'foot'

        response = api_client().patch(endpoint, {'working_hours': ["11:35-14:05", "09:00-11:00"]}, format='json')

        assert response.status_code == 200
        assert response.data['regions'] == [1, 2, 3]
        assert response.data['courier_type'] == 'foot'
        assert response.data['working_hours'] == ["11:35-14:05", "09:00-11:00"]

    def test_patch_idempotens(self, api_client):
        CourierFactory.create(courier_id=2, courier_type='foot', regions=[1, 2, 3], working_hours=['12:00-14:00'])
        CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3], working_hours=['12:00-14:00'])
        orders = order_valid_list + order_invalid_list
        for order in orders:
            order.save()
        response = api_client().post('/orders/assign', {'courier_id': 2}, format='json')
        first = response.data['orders']
        response = api_client().patch('/couriers/2', {'working_hours': ['18:00-21:00']}, format='json')
        response = api_client().post('/orders/assign', {'courier_id': 3}, format='json')
        assert response.data['orders'] == first

    def test_get_courier(self, api_client):
        endpoint = '/couriers/'
        courier = CourierFactory.create()
        endpoint += str(courier.courier_id)
        response = api_client().get(endpoint)
        assert response.data
        assert response.status_code == 200

    def test_get_courier_invalid(self, api_client):
        endpoint = '/couriers/dg'
        response = api_client().get(endpoint)
        assert response.status_code == 404


class TestOrdersEndpoints:
    def test_post_orders(self, api_client):
        endpoint = '/orders'
        order_json = {'data': factory.build_batch(dict, 3, FACTORY_CLASS=OrderFactory)}
        expected_response = {"orders": [{"id": order_json['data'][i]['order_id']} for i in range(3)]}
        response = api_client().post(endpoint, order_json, format='json')
        assert response.status_code == 201
        assert expected_response == response.data


class TestAssignOrdersEndpoints:
    @pytest.mark.parametrize('order', order_valid_list)
    def test_valid_assign(self, api_client, order):
        endpoint = '/orders/assign'
        CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3],
                              working_hours=['12:00-14:00'])
        order.save()
        response = api_client().post(endpoint, {'courier_id': 3})
        expected = [{'id': order.order_id}]
        assert response.data['orders'] == expected
        CourierFactory.create(courier_id=4, courier_type='foot', regions=[1, 2, 3],
                              working_hours=['12:00-14:00'])
        response = api_client().post(endpoint, {'courier_id': 4})
        assert response.data == {"orders": []}

    @pytest.mark.parametrize('order', order_invalid_list)
    def test_invalid_assign(self, api_client, order):
        endpoint = '/orders/assign'
        CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3],
                              working_hours=['12:00-14:00'])
        order.save()
        response = api_client().post(endpoint, {'courier_id': 3})
        expected = []
        assert response.data['orders'] == expected


class TestCompleteOrderEndpoints:
    def test_simple_complete_orders(self, api_client):
        courier = CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3],
                                        working_hours=['12:00-14:00'])
        order = OrderFactory.create(order_id=4, weight=7.0, region=2, delivery_hours=['13:00-13:30'])
        api_client().post('/orders/assign', {'courier_id': courier.courier_id})
        response = api_client().post('/orders/complete', {'courier_id': courier.courier_id, 'order_id': order.order_id,
                                                          "complete_time": (dt.datetime.now(
                                                              tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                                              seconds=120)).isoformat()})
        expected = {'order_id': order.order_id}
        assert response.data == expected
        assert response.status_code == 200
        assert Courier.objects.filter(courier_id=3)[0].rating == 4.83
        assert Courier.objects.filter(courier_id=3)[0].earnings == 1000

    def test_one_of_two_complete(self, api_client):
        OrderFactory.create(order_id=3, weight=7.0, region=2, delivery_hours=['13:00-13:30'])
        courier = CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3],
                                        working_hours=['12:00-14:00'])
        order = OrderFactory.create(order_id=4, weight=7.0, region=2, delivery_hours=['13:00-13:30'])
        api_client().post('/orders/assign', {'courier_id': courier.courier_id})
        response = api_client().post('/orders/complete', {'courier_id': courier.courier_id, 'order_id': order.order_id,
                                                          "complete_time": (dt.datetime.now(
                                                              tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                                              seconds=150)).isoformat()})
        expected = {'order_id': order.order_id}
        assert response.data == expected
        assert response.status_code == 200
        assert Courier.objects.filter(courier_id=3)[0].rating == 4.79
        assert Courier.objects.filter(courier_id=3)[0].earnings == 0

    def test_two_of_two_complete(self, api_client):
        order_1 = OrderFactory.create(order_id=1, weight=7.0, region=2, delivery_hours=['13:00-13:30'])
        order_2 = OrderFactory.create(order_id=2, weight=7.0, region=2, delivery_hours=['13:00-14:30'])
        courier = CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3],
                                        working_hours=['12:00-14:00'])
        api_client().post('/orders/assign', {'courier_id': courier.courier_id})
        api_client().post('/orders/complete', {'courier_id': courier.courier_id,
                                               'order_id': order_1.order_id,
                                               "complete_time": (dt.datetime.now(
                                                   tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                                   seconds=150)).isoformat()})
        api_client().post('/orders/complete', {'courier_id': courier.courier_id,
                                               'order_id': order_2.order_id,
                                               "complete_time": (dt.datetime.now(
                                                   tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                                   seconds=250)).isoformat()})
        assert round(Courier.objects.filter(courier_id=3)[0].rating, 1) == 4.8
        assert Courier.objects.filter(courier_id=3)[0].earnings == 1000

    def test_two_assigns(self, api_client):
        order_1 = OrderFactory.create(order_id=1, weight=7.0, region=2, delivery_hours=['13:00-13:30'])
        order_2 = OrderFactory.create(order_id=2, weight=7.0, region=2, delivery_hours=['13:00-14:30'])
        courier = CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3],
                                        working_hours=['12:00-14:00'])
        api_client().post('/orders/assign', {'courier_id': courier.courier_id})
        order_3 = OrderFactory.create(order_id=3, weight=7.0, region=2, delivery_hours=['13:00-14:30'])
        api_client().post('/orders/assign', {'courier_id': courier.courier_id})
        api_client().post('/orders/complete', {'courier_id': courier.courier_id,
                                               'order_id': order_1.order_id,
                                               "complete_time": (dt.datetime.now(
                                                   tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                                   seconds=150)).isoformat()})
        api_client().post('/orders/complete', {'courier_id': courier.courier_id,
                                               'order_id': order_2.order_id,
                                               "complete_time": (dt.datetime.now(
                                                   tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                                   seconds=250)).isoformat()})
        assert round(Courier.objects.filter(courier_id=3)[0].rating, 1) == 4.8
        assert Courier.objects.filter(courier_id=3)[0].earnings == 1000
        api_client().post('/orders/complete', {'courier_id': courier.courier_id,
                                               'order_id': order_3.order_id,
                                               "complete_time": (dt.datetime.now(
                                                   tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                                   seconds=500)).isoformat()})
        assert round(Courier.objects.filter(courier_id=3)[0].rating, 1) == 4.8
        assert Courier.objects.filter(courier_id=3)[0].earnings == 2000


class TestIntegral:
    def test_views(self, api_client):
        courier_json = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 23, 33],
                    "working_hours": []
                }]}
        order_json = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 2,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 11,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }]}
        response = api_client().post('/couriers', courier_json, format='json')
        assert response.data == {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]}
        assert response.status_code == 201
        response = api_client().post('/orders', order_json, format='json')
        assert response.data == {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]}
        assert response.status_code == 201
        response = api_client().patch('/couriers/2', {"regions": [11, 33, 2]}, format='json')
        expected = {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [11, 33, 2],
            "working_hours": ["09:00-18:00"]
        }
        assert response.data == expected
        assert response.status_code == 200
        response = api_client().post('/orders/assign', {"courier_id": 2}, format='json')
        expected_assign = [{'id': 2}, {'id': 3}]
        assert response.data['orders'] == expected_assign
        assert response.status_code == 200
        response = api_client().post('/orders/complete',
                                     {'courier_id': 2, 'order_id': 3, 'complete_time': (dt.datetime.now(
                                         tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                         seconds=150)).isoformat()}, format='json')
        assert response.data == {"order_id": 3}
        assert response.status_code == 200
        assert Courier.objects.get(pk=2).earnings == 0
        response = api_client().post('/orders/complete',
                                     {'courier_id': 2, 'order_id': 2, 'complete_time': (dt.datetime.now(
                                         tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(
                                         seconds=150)).isoformat()}, format='json')
        assert Courier.objects.get(pk=2).rating == 4.79
        assert Courier.objects.get(pk=2).earnings == 2500
        response = api_client().get('/couriers/2')
        expected_get = {'courier_id': 2, 'courier_type': 'bike', 'regions': [11, 33, 2],
                        'working_hours': ['09:00-18:00'], 'rating': 4.79, 'earnings': 2500}
        assert response.data == expected_get
        assert response.status_code == 200
