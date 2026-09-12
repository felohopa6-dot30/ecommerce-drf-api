from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.TextChoices):
    COMPUTERS = 'Computers'
    FOOD = 'Food'
    KIDS = 'Kids'
    HOME = 'Home'
    CLOTHES = 'Clothes'


class Product(models.Model):
    name = models.CharField(max_length=200, default='', blank=False)
    description = models.TextField(max_length=1000, default='', blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    brand = models.CharField(max_length=200, default='', blank=False)
    category = models.CharField(max_length=40, choices=Category.choices)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviews')
    rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000, default='', blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.name if self.product else 'No Product'}"