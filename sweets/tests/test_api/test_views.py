import factory
import json
import pytest
from sweets.models import Courier, Order
from sweets.tests.test_api.factories import CourierFactory, gen_courier_json, gen_order_json


pytestmark = pytest.mark.django_db


class TestCouriersEndpoints:
    def test_post_couriers(self, api_client):
        endpoint = '/couriers'
        courier_json = gen_courier_json(3)

        expected_response = {"couriers": [{"id": courier_json['data'][i]['courier_id']} for i in range(3)]}

        response = api_client().post(endpoint, courier_json, format='json')
        print(json.loads(response.content))
        assert response.status_code == 201
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

        def test_get_courier(self, api_client):
            endpoint = '/couriers/'

            courier = CourierFactory.create()

            endpoint += str(courier.courier_id)

class TestOrdersEndpoints:
    def test_post_orders(self, api_client):
        endpoint = '/orders'
        order_json = gen_order_json(3)

        expected_response = {"orders": [{"id": order_json['data'][i]['order_id']} for i in range(1)]}
        response = api_client().post(endpoint, order_json, format='json')
        assert response.status_code == 201
        assert expected_response == response.data


class TestAssignOrdersEndpoints:
    def test_something(self, api_client):
        courier = CourierFactory.create(courier_id=3, courier_type='foot')
        print(courier.courier_type)
