from rest_framework import serializers
from .models import Courier, Order, CouriersAndOrders
from rest_framework.validators import UniqueValidator

class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
    '''  order_id = serializers.IntegerField(validators=[UniqueValidator(Order.objects.all())])
    weight = serializers.FloatField()
    region = serializers.IntegerField()
    delivery_hours = serializers.ListField(child=serializers.CharField(max_length=128))
    courier_id = serializers.IntegerField(default=None)
    completed = serializers.BooleanField(default=False)'''

    def validate_weight(self, value):
        if (value > 50 or value < 0.01):
            raise serializers.ValidationError("Invalid weight")
        return value



class AssignSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()
    order_id = serializers.IntegerField(required=False)

    def validate_courier_id(self, value):
        if Courier.objects.all().get(pk=value).courier_id:
            return value

    def create(self, validated_data):
        return CouriersAndOrders.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.courier_id = validated_data.get('courier_id', instance.courier_id)
        instance.save()
        return instance