# order/models.py
from django.db import models
from django.contrib.auth.models import User
from store.models import Product


class OrderStatus(models.TextChoices):
    PROCESSING = 'Processing', 'Processing'
    SHIPPED = 'Shipped', 'Shipped'
    DELIVERED = 'Delivered', 'Delivered'


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'الدفع عند الاستلام'
    CARD = 'card', 'فيزا / ماستركارد'
    VODAFONE = 'vodafone', 'فودافون كاش'


class Order(models.Model):
    # أضفنا related_name مميز هنا لمنع التضارب مع أي موديل آخر
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='order_app_user_orders')
    city = models.CharField(max_length=100, default='', blank=True)
    zip_code = models.CharField(max_length=20, default='', blank=True)
    street = models.CharField(max_length=250, default='', blank=True)
    phone_number = models.CharField(max_length=20, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    vodafone_number = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PROCESSING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email if self.user else 'Anonymous'}"


class OrderItem(models.Model):
    # أضفنا related_name مميز هنا أيضاً لمنع التضارب
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_app_product_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name='order_items')
    name = models.CharField(max_length=200, default='', blank=False)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} (x{self.quantity})"