from django.contrib import admin
from .models import Feature, Plan, Store, UserProfile, ProductLog, InternalLink

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)} # در صورت انگلیسی بودن نام، کد را خودکار می‌سازد

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'max_products_per_month', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    # این خط ویجت حرفه‌ای دو ستونه را برای انتخاب Featureها فعال می‌کند
    filter_horizontal = ('features',)

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'is_active', 'created_at')
    list_filter = ('is_active', 'plan')
    search_fields = ('name', 'woo_url')
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'plan', 'is_active')
        }),
        ('تنظیمات یکپارچه‌سازی ووکامرس', {
            'fields': ('woo_url', 'woo_consumer_key', 'woo_consumer_secret')
        }),
        ('تنظیمات آپلود رسانه (وردپرس)', { 
            'fields': ('wp_username', 'wp_app_password'),
            'description': 'برای آپلود تصاویر، باید در بخش کاربران وردپرس یک "رمز عبور برنامه" بسازید و اینجا وارد کنید.'
        }),
        ('تنظیمات هوش مصنوعی و ربات', {
            'fields': ('openai_api_key', 'bot_token')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'role')
    list_filter = ('role', 'store')
    search_fields = ('user__username', 'store__name')

@admin.register(ProductLog)
class ProductLogAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'store', 'user', 'status', 'created_at')
    list_filter = ('status', 'store', 'created_at')
    search_fields = ('product_name', 'woo_product_id', 'error_message')
    readonly_fields = ('created_at',)
    
    # غیرفعال کردن قابلیت افزودن لاگ دستی توسط ادمین (لاگ فقط توسط سیستم باید ساخته شود)
    def has_add_permission(self, request):
        return False

@admin.register(InternalLink)
class InternalLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'store', 'url')
    list_filter = ('store',)
    search_fields = ('title', 'url')