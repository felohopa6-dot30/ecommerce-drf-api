from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_products
         , name='products'),
    path('newproduct/', views.create_product, name='create_product'),
    path('<int:pk>/', views.get_product_detail, name='product_detail'),
    path('<int:pk>/update/', views.update_product, name='update_product'),
    path('<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('<int:pk>/review/', views.create_review, name='create_review'),
    path('<int:pk>/review/delete/', views.delete_review, name='delete_review'),
]