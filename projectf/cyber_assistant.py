import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectf.settings')
django.setup()

from store.models import Product
from order.models import Order  # تم التعديل هنا ليتم استيراده من تطبيق order الصح

def analyze_store_performance():
    print("🤖 جاري تشغيل مساعد الذكاء الاصطناعي لتحليل المتجر السيبراني...\n")
    
    try:
        products = Product.objects.all()
        total_products = products.count()
    except Exception as e:
        total_products = 0
        print(f"⚠️ ملاحظة بخصوص المنتجات: {e}")

    try:
        orders = Order.objects.all()
        total_orders = orders.count()
        total_revenue = sum(getattr(order, 'total_price', 0) for order in orders)
    except Exception as e:
        total_orders = 0
        total_revenue = 0
        print(f"⚠️ ملاحظة بخصوص الطلبات: {e}")
    
    print(f"📊 --- تقرير الأداء السيبراني ---")
    print(f"• إجمالي عدد المنتجات في الترسانة: {total_products}")
    print(f"• إجمالي عدد الطلبات الواردة: {total_orders}")
    print(f"• إجمالي الأرباح المتوقعة: {total_revenue} ج.م")
    print(f"-----------------------------------\n")
    
    if total_orders == 0:
        print("💡 نصيحة ذكية: لا توجد طلبات مسجلة حالياً. جرب إرسال طلب تجريبي من واجهة المتجر!")
    else:
        print("💡 تحليل ذكي: حركة المبيعات ممتازة، استمر في التطوير يا بطل.")

if __name__ == "__main__":
    analyze_store_performance()