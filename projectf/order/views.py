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
    
    # دعم الحالتين: لو جاية باسم order_items أو items من الواجهة
    order_items = data.get('order_items', [])
    if not order_items and 'items' in data:
        raw_items = data.get('items', [])
        # تحويل العناصر القادمة من الواجهة لتتوافق مع منطق الـ View
        order_items = []
        for item in raw_items:
            # لو الاسم جاي، نحاول نلاقيه في قاعدة البيانات
            product_obj = Product.objects.filter(name=item.get('product_name') or item.get('name')).first()
            product_id = product_obj.id if product_obj else 1  # افتراضي لو مش موجود
            
            order_items.append({
                'product': product_id,
                'quantity': item.get('quantity', 1),
                'price': item.get('price', 0)
            })

    if not order_items or len(order_items) == 0:
        return Response({'error': 'No order items received'}, status=status.HTTP_400_BAD_REQUEST)

    total_amount = sum(float(item.get('price', 0)) * int(item.get('quantity', 1)) for item in order_items)

    order = Order.objects.create(
        user=user,
        city=data.get('city', 'Cairo'),
        zip_code=data.get('zip_code', '00000'),
        street=data.get('street', data.get('address', 'Cyber Street')),
        phone_number=data.get('phone_number', '0000000000'),
        country=data.get('country', 'Egypt'),
        total_amount=total_amount
    )

    for i in order_items:
        product_id = i.get('product')
        product = Product.objects.filter(id=product_id).first()
        
        # لو المنتج مش موجود بالآي دي، ناخده بأول منتج متاح كحل احتياطي
        if not product:
            product = Product.objects.first()

        if product:
            if hasattr(product, 'stock') and product.stock < int(i.get('quantity', 1)):
                order.delete()
                return Response(
                    {'error': f'Not enough stock for product: {product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                quantity=int(i.get('quantity', 1)),
                price=float(i.get('price', 0))
            )
            
            if hasattr(product, 'stock'):
                product.stock -= int(i.get('quantity', 1))
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_order(request):
    user = request.user
    data = request.data

    raw_items = data.get('order_items') or data.get('items') or []
    if not raw_items:
        return Response({'error': 'لا توجد منتجات في الطلب'}, status=status.HTTP_400_BAD_REQUEST)

    # تحقق من كل المنتجات والمخزون الأول، قبل ما نلمس الداتابيز
    resolved_items = []
    for item in raw_items:
        product_id = item.get('product')
        quantity = int(item.get('quantity', 1))
        if not product_id:
            return Response({'error': 'كل عنصر لازم يبعت product id'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'error': f'منتج غير موجود: {product_id}'}, status=status.HTTP_404_NOT_FOUND)
        if product.stock < quantity:
            return Response({'error': f'الكمية المطلوبة من {product.name} غير متوفرة'}, status=status.HTTP_400_BAD_REQUEST)

        resolved_items.append({'product': product, 'quantity': quantity, 'price': product.price})

    payment_method = data.get('payment_method', 'cash')
    total_amount = sum(i['price'] * i['quantity'] for i in resolved_items)

    order = Order.objects.create(
        user=user,
        city=data.get('city', 'Cairo'),
        zip_code=data.get('zip_code', '00000'),
        street=data.get('street', data.get('address', 'غير محدد')),
        phone_number=data.get('phone_number', ''),
        country=data.get('country', 'Egypt'),
        payment_method=payment_method,
        vodafone_number=data.get('vodafone_number') if payment_method == 'vodafone' else None,
        total_amount=total_amount,
    )

    for i in resolved_items:
        OrderItem.objects.create(
            product=i['product'], order=order, name=i['product'].name,
            quantity=i['quantity'], price=i['price'],
        )
        i['product'].stock -= i['quantity']
        i['product'].save()

    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)