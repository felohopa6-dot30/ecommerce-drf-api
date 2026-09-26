from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Avg
from django.db import transaction
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status, generics, viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from .models import Product, Review, Order, OrderItem
from .serializers import ProductSerializer, ReviewSerializer, OrderSerializer
from .filters import ProductFilter


# ---------------- Auth ----------------

@api_view(['POST'])
def register_user(request):
    data = request.data
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return Response({'error': 'لازم تكتب البريد الإلكتروني والباسورد!'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=email).exists():
        return Response({'error': 'الحساب ده موجود بالفعل، جرب تسجل دخول!'}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(
        username=email, email=email, password=password,
        first_name=first_name, last_name=last_name,
    )
    return Response({'message': 'تم تسجيل المستخدم بنجاح! 🚀'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def google_login(request):
    token = request.data.get('id_token')
    if not token:
        return Response({'error': 'مفيش id_token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        idinfo = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        return Response({'error': 'التوكن غير صالح'}, status=status.HTTP_400_BAD_REQUEST)

    email = idinfo.get('email')
    user, _ = User.objects.get_or_create(
        username=email,
        defaults={
            'email': email,
            'first_name': idinfo.get('given_name', ''),
            'last_name': idinfo.get('family_name', ''),
        },
    )
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'email': email})


# ---------------- Products ----------------

@api_view(['GET'])
def get_all_products(request):
    filterset = ProductFilter(request.GET, queryset=Product.objects.all().order_by('id'))
    count = filterset.qs.count()

    resPerPage = 10
    paginator = PageNumberPagination()
    paginator.page_size = resPerPage

    queryset = paginator.paginate_queryset(filterset.qs, request)
    serializer = ProductSerializer(queryset, many=True)

    return Response({"count": count, "resPerPage": resPerPage, "products": serializer.data})


@api_view(['GET'])
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response({"product": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save(user=request.user)
        return Response({"product": ProductSerializer(product).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(instance=product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"product": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    product.delete()
    return Response({"detail": "Product successfully deleted!"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    product = get_object_or_404(Product, id=pk)
    data = request.data
    review = product.reviews.filter(user=user)

    if data.get('rating', 0) <= 0 or data.get('rating', 0) > 5:
        return Response({'error': 'Please select a valid rating between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

    if review.exists():
        review.update(rating=data['rating'], comment=data.get('comment', ''))
    else:
        Review.objects.create(user=user, product=product, rating=data['rating'], comment=data.get('comment', ''))

    rating_dict = product.reviews.aggregate(avg_rating=Avg('rating'))
    product.ratings = rating_dict['avg_rating'] or 0
    product.save()
    return Response({'detail': 'تم حفظ التقييم'}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    product = get_object_or_404(Product, id=pk)
    review = product.reviews.filter(user=user)

    if not review.exists():
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    rating_dict = product.reviews.aggregate(avg_rating=Avg('rating'))
    product.ratings = rating_dict['avg_rating'] or 0
    product.save()
    return Response({'detail': 'Product review deleted'}, status=status.HTTP_200_OK)


# ---------------- Orders ----------------

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        items_data = data.get('items', [])
        payment_method = data.get('payment_method', 'cash')
        vodafone_number = data.get('vodafone_number', '')

        if not items_data:
            return Response({'error': 'لا توجد منتجات في الطلب'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    status='Pending',
                    payment_method=payment_method,
                    vodafone_number=vodafone_number if payment_method == 'vodafone' else None,
                )
                total_price = 0

                for item_data in items_data:
                    product_id = item_data.get('product')
                    quantity = int(item_data.get('quantity', 1))
                    product = Product.objects.get(id=product_id)

                    if product.stock < quantity:
                        raise ValueError(f'المنتج {product.name} غير متوفر بالمخزون بالكمية المطلوبة')

                    product.stock -= quantity
                    product.save()

                    item_price = product.price
                    total_price += item_price * quantity

                    OrderItem.objects.create(order=order, product=product, quantity=quantity, price=item_price)

                order.total_price = total_price
                order.save()
                return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({'error': 'المنتج غير موجود'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)