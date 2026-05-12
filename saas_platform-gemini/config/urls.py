from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # پنل مدیریت جنگو (مخصوص شما به عنوان مدیر کل پلتفرم)
    path('admin/', admin.site.urls),
    
    # فایل‌های urls اپلیکیشن core
    path('', include('core.urls')),
]

# اضافه کردن مسیر فایل‌های استاتیک و مدیا در محیط توسعه
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)