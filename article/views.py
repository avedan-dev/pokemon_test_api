from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from .models import Courier, Order, CouriersAndOrders
from .serializers import CourierSerializer, OrderSerializer, AssignSerializer
from django.db.models import Min, Max
import datetime as dt

courier_lifting = {
    'foot': 10,
    'bike': 15,
    'car': 50,
}


def str_to_time(working_hours):
    start_time = dt.datetime.strptime(working_hours.split('-')[0], '%H:%M')
    end_time = dt.datetime.strptime(working_hours.split('-')[1], '%H:%M')
    return [start_time, end_time]


class CourierView(APIView):
    def patch(self, request, pk):
        saved_courier = get_object_or_404(Courier.objects.all(), pk=pk)
        data = request.data
        serializer = CourierSerializer(instance=saved_courier, data=data, partial=True)
        if serializer.is_valid(raise_exception=False):
            courier_saved = serializer.save()
            return Response(Courier.objects.filter(courier_id=pk).values()[0], status=status.HTTP_200_OK)
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
                        if (work_time[0] <= order_time[0] and work_time[1] >= order_time[0]) or (
                                work_time[1] >= order_time[1] and work_time[0] <= order_time[0]):
                            ans.append(order)
                            new = CouriersAndOrders(courier_id=courier, order_id=order)
                            try:
                                new.save(force_update=False)
                            except Exception as e:
                                print(e)
                                pass
                            x = 1
                            break
                    if x == 1:
                        break
            return Response({"orders": [{"id": ans[j].order_id} for j in range(len(ans))]}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteView(APIView):
    def post(self, request):
        data = request.data
        serializer = AssignSerializer(data=data, many=False)
        if serializer.is_valid(raise_exception=False):
            try:
                new = CouriersAndOrders.objects.get(courier_id=serializer.validated_data["courier_id"],
                                                    order_id=serializer.validated_data["order_id"])
                new.completed = True
                new.save(force_update=True)
                return Response({"order_id": serializer.validated_data["order_id"]}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
