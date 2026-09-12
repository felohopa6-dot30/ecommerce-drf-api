from rest_framework import serializers
from .models import Product, Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = Review
        fields = ('id', 'product', 'user', 'user_name', 'rating', 'comment', 'createdAt')


class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'brand',
            'category',
            'ratings',
            'stock',
            'user',
            'createdAt',
            'reviews',
        )
