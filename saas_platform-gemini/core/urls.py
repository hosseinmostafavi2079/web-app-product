from django.urls import path
from . import views

urlpatterns = [
    # در صورتی که کاربر وارد روت سیستم شود، به داشبورد منتقل می‌شود
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/add/', views.add_product, name='add_product'),
]