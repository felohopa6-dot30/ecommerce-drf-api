
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from .filters import ProductsFilter


@api_view(['GET'])
def get_all_products(request):
    filterset = ProductsFilter(request.GET, queryset=Product.objects.all().order_by('id'))
    count = filterset.qs.count()
    
    # Pagination
    resPerPage = 10
    paginator = PageNumberPagination()
    paginator.page_size = resPerPage
    
    queryset = paginator.paginate_queryset(filterset.qs, request)
    serializer = ProductSerializer(queryset, many=True)
    
    return Response({
        "count": count,
        "resPerPage": resPerPage,
        "products": serializer.data
    })


@api_view(['GET'])
def get_product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response({"product": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_product(request):
    data = request.data
    serializer = ProductSerializer(data=data)
    
    if serializer.is_valid():
        product = serializer.save(user=request.user)
        res_serializer = ProductSerializer(product, many=False)
        return Response({"product": res_serializer.data}, status=status.HTTP_201_CREATED)
    
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
        new_review = {'rating': data['rating'], 'comment': data.get('comment', '')}
        review.update(**new_review)

        rating_dict = product.reviews.aggregate(avg_rating=Avg('rating'))
        product.ratings = rating_dict['avg_rating'] or 0
        product.save()

        return Response({'detail': 'Product review updated'})
    else:
        Review.objects.create(
            user=user,
            product=product,
            rating=data['rating'],
            comment=data.get('comment', '')
        )

        rating_dict = product.reviews.aggregate(avg_rating=Avg('rating'))
        product.ratings = rating_dict['avg_rating'] or 0
        product.save()

        return Response({'detail': 'Product review created'}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    product = get_object_or_404(Product, id=pk)

    review = product.reviews.filter(user=user)

    if review.exists():
        review.delete()

        rating_dict = product.reviews.aggregate(avg_rating=Avg('rating'))
        product.ratings = rating_dict['avg_rating'] or 0
        product.save()

        return Response({'detail': 'Product review deleted'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)