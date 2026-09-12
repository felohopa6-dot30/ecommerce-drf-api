from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.create_user, name='register'),
    path('userinfo/', views.current_user, name='user_info'),
    path('updateuser/', views.update_user, name='update_user'),
    path('forgetpassword/', views.forget_password, name='forgetpassword'),
    path('resetpassword/<str:token>/', views.reset_password, name='resetpassword'),
]


