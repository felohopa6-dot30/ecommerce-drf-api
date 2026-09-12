from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserCreateSerializer
from account.models import UserProfile


@api_view(['POST'])
def create_user(request):
    data = request.data
    serializer = UserCreateSerializer(data=data)
    
    if serializer.is_valid():
        email = data.get('email')
        
        if User.objects.filter(username=email).exists():
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            username=email,
            email=email,
            password=make_password(data.get('password'))
        )
        return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserCreateSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data

    email = data.get('email')
    if email and email != user.email:
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return Response({'error': 'Email is already in use by another account'}, status=status.HTTP_400_BAD_REQUEST)
        user.email = email
        user.username = email

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)

    if data.get('password'):
        user.password = make_password(data.get('password'))

    user.save()
    serializer = UserCreateSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
def forget_password(request):
    data = request.data
    email = data.get('email')

    if not email:
        return Response({'error': 'Please provide an email'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, email=email)
    profile, created = UserProfile.objects.get_or_create(user=user)

    token = get_random_string(40)
    expire_date = timezone.now() + timedelta(minutes=30)

    profile.reset_password_token = token
    profile.reset_password_expire = expire_date
    profile.save()

    link = f"http://127.0.0.1:8000/api/account/resetpassword/{token}/"

    send_mail(
        "Password Reset Request",
        f"Click the link to reset your password: {link}",
        "noreply@store.com",
        [email],
        fail_silently=False,
    )

    return Response({'detail': f'Password reset email sent to {email}'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    profile = get_object_or_404(UserProfile, reset_password_token=token)

    if profile.reset_password_expire and profile.reset_password_expire < timezone.now():
        return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)

    if data.get('password') != data.get('confirmPassword'):
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    user = profile.user
    user.password = make_password(data.get('password'))
    user.save()

    profile.reset_password_token = ""
    profile.reset_password_expire = None
    profile.save()

    return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)