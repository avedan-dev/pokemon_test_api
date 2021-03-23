from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from .models import Courier, Order, CouriersAndOrders
from .serializers import CourierSerializer, OrderSerializer, AssignSerializer, CompleteSerializer
from django.db.models import Avg
import datetime as dt

courier_lifting = {
    'foot': 10,
    'bike': 15,
    'car': 50,
}

courier_salary = {
    'foot': 2,
    'bike': 5,
    'car': 9,
}


def str_to_time(working_hours):
    start_time = dt.datetime.strptime(str(dt.date.today()) + working_hours.split('-')[0], '%Y-%m-%d%H:%M')
    end_time = dt.datetime.strptime(str(dt.date.today()) + working_hours.split('-')[1], '%Y-%m-%d%H:%M')
    return [start_time, end_time]


def courier_check(courier):
    cour_order = CouriersAndOrders.objects.filter(courier_id=courier.courier_id).values(
        "order_id")  # Получаю класс id заказов, записанных на курьера
    orders = Order.objects.filter(order_id__in=cour_order)  # Получаю заказы по их id
    orders_del = list(orders.exclude(region__in=courier.regions, weight__lte=courier_lifting[
        courier.courier_type]))  # Выбираю заказы не подходящие по региону и весу
    s = [str_to_time(courier.working_hours[i]) for i in range(len(courier.working_hours))]
    for order in orders:
        if order not in orders_del:
            x = 0
            for work_time in s:
                for i in range(len(order.delivery_hours)):
                    order_time = str_to_time(order.delivery_hours[i])
                    if (work_time[0] < order_time[0] < work_time[1]) or (
                            work_time[1] > order_time[1] and work_time[0] < order_time[0]):
                        x = 1
                        break
                    else:
                        orders_del.append(order)
                if x == 1:
                    break
            CouriersAndOrders.objects.filter(courier_id=courier.courier_id,
                                             order_id__in=orders_del).delete()  # Удаляю объекты CouriersAndOrders


def courier_data(courier):
    courier.pop('last_order')
    if not courier['rating']:
        courier.pop('rating')
    if not courier['earning']:
        courier.pop('earning')
    return courier


class CourierView(APIView):
    def patch(self, request, pk):
        saved_courier = get_object_or_404(Courier.objects.all(), pk=pk)
        data = request.data
        serializer = CourierSerializer(instance=saved_courier, data=data, partial=True)
        if serializer.is_valid(raise_exception=False):
            courier_saved = serializer.save()
            courier_check(courier_saved)
            courier = Courier.objects.filter(courier_id=pk).values()[0]
            return Response(courier_data(courier), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        saved_courier = get_object_or_404(Courier.objects.all(), pk=pk)
        data = request.data
        serializer = CourierSerializer(instance=saved_courier, data=data, partial=True)
        if serializer.is_valid():
            courier = Courier.objects.filter(courier_id=pk).values()[0]
            return Response(courier_data(courier), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        ans = []
        courier = request.data.get("data")
        serializer = CourierSerializer(data=courier, many=True)
        if serializer.is_valid(raise_exception=False):
            courier_saved = serializer.save()
            return Response({"couriers": [{"id": x.courier_id} for x in courier_saved]}, status=status.HTTP_201_CREATED)
        else:
            for i in range(len(serializer.errors)):
                if serializer.errors[i] != {}:
                    ans.append(courier[i]['courier_id'])
            print(serializer.errors)
            return Response({"validation_error": {"couriers": [{"id": ans[j]} for j in range(len(ans))]}},
                            status=status.HTTP_400_BAD_REQUEST)


class OrderView(APIView):
    def post(self, request):
        ans = []
        order = request.data.get("data")
        serializer = OrderSerializer(data=order, many=True)
        if serializer.is_valid(raise_exception=False):
            order_saved = serializer.save()
            return Response({"orders": [{"id": x.order_id} for x in order_saved]}, status=status.HTTP_201_CREATED)
        else:
            for i in range(len(serializer.errors)):
                if serializer.errors[i] != {}:
                    ans.append(serializer.data[i]['order_id'])
            print(serializer.errors)
            return Response({"validation_error": {"orders": [{"id": ans[j]} for j in range(len(ans))]}},
                            status=status.HTTP_400_BAD_REQUEST)


class AssignView(APIView):
    def post(self, request):
        ans = []
        data = request.data
        serializer = AssignSerializer(data=data, many=False)
        if serializer.is_valid(raise_exception=False):
            courier = Courier.objects.all().get(pk=(serializer.validated_data['courier_id']))
            s = [str_to_time(courier.working_hours[i]) for i in range(len(courier.working_hours))]
            orders = Order.objects.filter(region__in=courier.regions, weight__lte=courier_lifting[courier.courier_type])
            for order in orders:
                x = 0
                for work_time in s:
                    for i in range(len(order.delivery_hours)):
                        order_time = str_to_time(order.delivery_hours[i])
                        if work_time[0] < order_time[0] < work_time[1] or (
                                order_time[0] < work_time[0] < order_time[1]):
                            if not CouriersAndOrders.objects.filter(order_id=order):
                                ans.append(order)
                                new = CouriersAndOrders(courier_id=courier, order_id=order)
                                try:
                                    new.save()
                                except ValueError:
                                    pass
                                x = 1
                                break
                    if x == 1:
                        break
            if ans:
                return Response({"orders": [{"id": ans[j].order_id} for j in range(len(ans))],
                                 "assign_time": str(dt.datetime.today().isoformat()) + 'Z'}, status=status.HTTP_200_OK)
            else:
                return Response({"orders": []}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteView(APIView):
    def post(self, request):
        data = request.data
        serializer = CompleteSerializer(data=data, many=False)
        if serializer.is_valid(raise_exception=False):
            new = CouriersAndOrders.objects.get(courier_id=serializer.validated_data["courier_id"],
                                                order_id=serializer.validated_data["order_id"])
            new.completed = True
            comlete_time = dt.datetime.strptime(data['complete_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
            courier = Courier.objects.get(courier_id=serializer.validated_data["courier_id"])

            order = Order.objects.get(order_id=serializer.validated_data["order_id"])
            if not courier.last_order:
                order.finish_time = (comlete_time - new.assign_time).total_seconds()
            else:
                order.finish_time = (comlete_time - courier.last_order).total_seconds()
            order.save()
            c = courier_salary[courier.courier_type]
            courier.earning += 500 * c
            t = Order.objects.values('region').filter(finish_time__gt=0).annotate(Avg('finish_time')).order_by(
                "finish_time__avg")[0]['finish_time__avg']
            courier.rating = round((60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5, 2)
            courier.last_order = comlete_time
            courier.save()
            return Response({"order_id": serializer.validated_data["order_id"]}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
