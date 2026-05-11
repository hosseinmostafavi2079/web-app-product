from .base import *
import os

DEBUG = False
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
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# در صورت داشتن SSL روی سرور (Nginx/Traefik) این موارد را فعال کنید:
# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')