from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.new_order, name='new_orders'),
    path('all/', views.get_orders, name='get_orders'),
    path('<int:pk>/', views.get_order, name='get_order'),
    path('<int:pk>/process/', views.process_order, name='process_order'),
    path('<int:pk>/delete/', views.delete_order, name='delete_order'),
]