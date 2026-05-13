from .base import *
import os
from django.core.exceptions import ImproperlyConfigured

DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# اتصال به دیتابیس PostgreSQL داخل شبکه داکر
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'saas_db'),
        'USER': os.getenv('POSTGRES_USER', 'saas_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'saas_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'), # پورت داخلی داکر
    }
}

# تنظیمات امنیتی پروداکشن
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY or SECRET_KEY == 'fallback-secret-key-for-dev':
    raise ImproperlyConfigured("خطای امنیتی: کلید DJANGO_SECRET_KEY در فایل .env تنظیم نشده است!")