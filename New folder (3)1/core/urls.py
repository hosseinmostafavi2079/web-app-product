from django.urls import path
from . import views

urlpatterns = [
    # در صورتی که کاربر وارد روت سیستم شود، به داشبورد منتقل می‌شود
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/manager/', views.product_manager, name='product_manager'),
    path('export/excel/', views.export_logs_excel, name='export_logs_excel'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('cache/clear/', views.clear_store_cache_view, name='clear_store_cache'),
]