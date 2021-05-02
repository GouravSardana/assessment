from rest_framework import serializers
from api.models import AssignedOrder, DeliveryPartner, Order
from datetime import datetime


class AssignedOrderSerializer(serializers.ModelSerializer):
    list_order_ids_assigned = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = AssignedOrder
        fields = ['vehicle_type', 'delivery_partner_id', 'list_order_ids_assigned']

    def create(self, validated_data):
        instance = AssignedOrder.objects.create(**validated_data)
        for data in self.initial_data:
            list_order_ids_assigned = data.get('list_order_ids_assigned')
            instance.list_order_ids_assigned.set(list_order_ids_assigned)


class DeliveryPartnerSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True, default=True)
    class Meta:
        model = DeliveryPartner
        fields = ['delivery_partner_id', 'name', 'vehicle_type', 'is_available']


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['order_id', 'order_weight']
