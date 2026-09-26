"""
URL configuration for projectf project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('api/store/', include('store.urls')),
    path('api/', include('account.urls')),
    
    # مسار الطلبات
    path('api/orders/', include('order.urls')),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # type: ignore
    path('api/token/refresh/', TokenObtainPairView.as_view(), name='token_refresh'), # type: ignore
]

# دعم عرض الملفات والوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "utels.error_view.handler404"
handler500 = "utels.error_view.handler500"