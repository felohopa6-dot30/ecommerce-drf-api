from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Order, OrderItem
from store.models import Product
from .serializers import OrderSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_order(request):
    user = request.user
    data = request.data
    order_items = data.get('order_items', [])

    if not order_items or len(order_items) == 0:
        return Response({'error': 'No order items received'}, status=status.HTTP_400_BAD_REQUEST)

    total_amount = sum(item['price'] * item['quantity'] for item in order_items)

    order = Order.objects.create(
        user=user,
        city=data.get('city'),
        zip_code=data.get('zip_code'),
        street=data.get('street'),
        phone_number=data.get('phone_number'),
        country=data.get('country'),
        total_amount=total_amount
    )

    for i in order_items:
        product = get_object_or_404(Product, id=i['product'])
        
        if product.stock < i['quantity']:
            order.delete()
            return Response(
                {'error': f'Not enough stock for product: {product.name}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        OrderItem.objects.create(
            product=product,
            order=order,
            name=product.name,
            quantity=i['quantity'],
            price=i['price']
        )
        
        product.stock -= i['quantity']
        product.save()

    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response({'orders': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    
    if order.user != request.user and not request.user.is_staff:
        return Response({'error': 'You are not authorized to view this order'}, status=status.HTTP_403_FORBIDDEN)
        
    serializer = OrderSerializer(order, many=False)
    return Response({'order': serializer.data})


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def process_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    status_data = request.data.get('status')
    
    if status_data:
        order.status = status_data
        order.save()
        serializer = OrderSerializer(order, many=False)
        return Response({'order': serializer.data})
        
    return Response({'error': 'Please provide a valid status'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    order.delete()
    return Response({'detail': 'Order successfully deleted'}, status=status.HTTP_200_OK)