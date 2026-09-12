from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'name', 'price', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 
            'user', 
            'city', 
            'zip_code', 
            'street', 
            'phone_number', 
            'country', 
            'total_amount', 
            'status', 
            'created_at', 
            'order_items'
        )