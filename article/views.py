from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from .models import Courier, Order
from .serializers import CourierSerializer, OrderSerializer, AssignSerializer

courier_type = {
    'foot': 10,
    'bike': 15,
    'car': 50,
}


class CourierView(APIView):
    def patch(self, request, pk):
        saved_courier = get_object_or_404(Courier.objects.all(), pk=pk)
        data = request.data
        serializer = CourierSerializer(instance=saved_courier, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
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
                    ans.append(serializer.data[i]['courier_id'])
            print(serializer.errors)
            return Response({"validation_error": {"couriers": [{"id": ans[j]} for j in range(len(ans))]}}, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"validation_error": {"orders": [{"id": ans[j]} for j in range(len(ans))]}}, status=status.HTTP_400_BAD_REQUEST)


class AssignView(APIView):
    def post(self, request):
        data = request.data
        serializer = AssignSerializer(data=data, many=False)
        if serializer.is_valid(raise_exception=False):
            courier = Courier.objects.all().get(pk=(serializer.validated_data['courier_id']))
            orders = Order.objects.filter(region__in=courier.regions)
            print(orders)
            return Response(status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)