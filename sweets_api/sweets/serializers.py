from rest_framework import serializers
from .models import Courier, Order, CouriersAndOrders
from django.core.exceptions import ObjectDoesNotExist


class CourierSerializer(serializers.ModelSerializer):
    working_hours = serializers.ListField(
        child=serializers.CharField(max_length=128), allow_empty=True)
    regions = serializers.ListField(
        child=serializers.IntegerField(allow_null=False), allow_empty=False)

    class Meta:
        model = Courier
        fields = '__all__'

    def validate_regions(self, regions):
        if len(regions) != len(set(regions)):
            raise serializers.ValidationError(
                "The regions shouldn`t be repeated")
        else:
            return regions


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def validate_weight(self, value):
        if value > 50 or value < 0.01:
            raise serializers.ValidationError("Invalid weight")
        return value


class AssignSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()
    order_id = serializers.IntegerField(required=False)
    assign_time = serializers.DateTimeField(required=False)

    def validate_courier_id(self, value):
        try:
            if Courier.objects.all().get(pk=value).courier_id:
                return value
        except (AttributeError, ObjectDoesNotExist):
            raise serializers.ValidationError("This courier id does not exist")

    def create(self, validated_data):
        return CouriersAndOrders.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.courier_id = validated_data.get('courier_id',
                                                 instance.courier_id)
        instance.save()
        return instance


class CompleteSerializer(serializers.Serializer):
    def validate(self, data):
        new = CouriersAndOrders.objects.get(courier_id=data["courier_id"],
                                            order_id=data["order_id"])
        if int((data['complete_time'] - new.assign_time).total_seconds()) >= 0:
            return data
        else:
            raise serializers.ValidationError(
                "Complete time less than assign time")

    courier_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    complete_time = serializers.DateTimeField()

    def validate_courier_id(self, value):
        try:
            if Courier.objects.all().get(pk=value).courier_id:
                return value
        except (AttributeError, ObjectDoesNotExist):
            raise serializers.ValidationError("This courier id does not exist")

    def validate_order_id(self, value):
        try:
            if Order.objects.all().get(pk=value).order_id:
                return value
        except (AttributeError, ObjectDoesNotExist):
            raise serializers.ValidationError("This order id does not exist")
