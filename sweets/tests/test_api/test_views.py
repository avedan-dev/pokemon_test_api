import factory
import json
import pytest
from django.core.serializers import serialize, json
from sweets.models import Courier, Order
from sweets.tests.test_api.factories import CourierFactory, gen_courier_json
from django.core.serializers.json import DjangoJSONEncoder

pytestmark = pytest.mark.django_db


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Courier):
            return str(obj)
        return super().default(obj)


@pytest.mark.django_db
class TestCouriersEndpoints:

    def test_post_list(self, api_client):
        endpoint = '/couriers'
        courier_json = gen_courier_json(3)

        expected_response = {"couriers":[{"id": courier_json['data'][i]['courier_id']} for i in range(3)]}

        response = api_client().post(endpoint, courier_json, format='json')


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




