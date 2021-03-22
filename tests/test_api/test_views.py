import pytest
from tests.test_api.factories import CourierFactory, gen_courier_json, gen_order_json, OrderFactory


@pytest.mark.django_db
class TestCouriersEndpoints:
    def test_post_couriers(self, api_client):
        endpoint = '/couriers'
        courier_json = gen_courier_json(3)

        expected_response = {"couriers": [{"id": courier_json['data'][i]['courier_id']} for i in range(3)]}

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

        def test_get_courier(self, api_client):
            endpoint = '/couriers/'
            courier = CourierFactory.create()
            endpoint += str(courier.courier_id)


@pytest.mark.django_db
class TestOrdersEndpoints:
    def test_post_orders(self, api_client):
        endpoint = '/orders'
        order_json = gen_order_json(3)

        expected_response = {"orders": [{"id": order_json['data'][i]['order_id']} for i in range(1)]}
        response = api_client().post(endpoint, order_json, format='json')
        assert response.status_code == 201
        assert expected_response == response.data


@pytest.mark.django_db
class TestAssignOrdersEndpoints:
    def test_something(self, api_client):
        endpoint = '/orders/assign'
        CourierFactory.create(courier_id=3, courier_type='foot', regions=[1, 2, 3],
                              working_hours=['12:00-14:00'])
        OrderFactory.create(order_id=1, weight=5.0, region=2, delivery_hours=['9:00-12:01'])
        OrderFactory.create(order_id=2, weight=5.0, region=2, delivery_hours=['9:00-12:00'])
        OrderFactory.create(order_id=3, weight=7.0, region=2, delivery_hours=['13:59-16:00'])
        OrderFactory.create(order_id=4, weight=7.0, region=2, delivery_hours=['14:00-16:00'])
        OrderFactory.create(order_id=5, weight=7.0, region=2, delivery_hours=['13:00-13:30'])
        response = api_client().post(endpoint, {'courier_id': 3})
        expected = [{'id': 1}, {'id': 3}, {'id': 5}]
        assert response.data['orders'] == expected
        CourierFactory.create(courier_id=4, courier_type='foot', regions=[1, 2, 3],
                              working_hours=['12:00-14:00'])
        response = api_client().post(endpoint, {'courier_id': 4})
        assert response.data == {"orders": []}
