from rest_framework import serializers
from order.models import Order, OrderItem
from store.models import Product, Review

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        fields = [
            'id', 
            'user', 
            'user_name', 
            'status', 
            'total_amount', 
            'city', 
            'zip_code', 
            'street', 
            'phone_number', 
            'country', 
            'created_at', 
            'items'
        ]
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'status',
            'payment_method', 'vodafone_number',
            'total_amount', 'city', 'zip_code', 'street',
            'phone_number', 'country', 'created_at', 'items'
        ]
        read_only_fields = ['user', 'total_amount', 'status']
        