from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.TextChoices):
    PHONES = 'Phones', 'هواتف'
    COMPUTERS = 'Computers', 'كمبيوتر'
    GLASSES = 'Glasses', 'نظارات'
    ACCESSORIES = 'Accessories', 'إكسسوارات'

class Product(models.Model):
    name = models.CharField(max_length=200, default='', blank=False)
    description = models.TextField(max_length=1000, default='', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    brand = models.CharField(max_length=200, default='', blank=False)
    category = models.CharField(max_length=40, choices=Category.choices)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviews')
    rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000, default='', blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.name if self.product else 'No Product'}"


class Order(models.Model):
    PAYMENT_CHOICES = (
        ('cash', 'الدفع عند الاستلام'),
        ('card', 'فيزا / ماستركارد'),
        ('vodafone', 'فودافون كاش'),
    )
    STATUS_CHOICES = (
        ('Pending', 'قيد الانتظار'),
        ('Paid', 'مدفوع'),
        ('Shipped', 'تم الشحن'),
        ('Completed', 'مكتمل'),
        ('Cancelled', 'ملغي'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')
    vodafone_number = models.CharField(max_length=20, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name if self.product else 'محذوف'} x{self.quantity} (Order #{self.order.id})"