from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product, Order

class ECommerceTests(APITestCase):
    def setUp(self):
        # إنشاء مستخدمين للتجربة (أدمن ومستخدم عادي)
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin = User.objects.create_superuser(username='adminuser', password='password123')
        
        # إنشاء منتج تجريبي
        self.product = Product.objects.create(
            name='Laptop',
            price=1000.00,
            stock=5,
            brand='Dell',
            category='Computers'
        )
        self.orders_url = '/api/store/orders/' # عدلها حسب الـ router عندك

    def test_create_order_success(self):
        # اختبار نجاح إنشاء طلب وخصم المخزون
        self.client.force_authenticate(user=self.user)
        data = {
            "items": [
                {"product": self.product.id, "quantity": 2}
            ]
        }
        response = self.client.post(self.orders_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # التأكد إن المخزون قل من 5 إلى 3
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_create_order_out_of_stock(self):
        # اختبار فشل الطلب لو الكمية أكبر من المخزون
        self.client.force_authenticate(user=self.user)
        data = {
            "items": [
                {"product": self.product.id, "quantity": 10}
            ]
        }
        response = self.client.post(self.orders_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)