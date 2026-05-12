from django.utils import timezone
from core.models import ProductLog

class AccessControlService:
    @staticmethod
    def has_feature(store, feature_code):
        """
        بررسی می‌کند که آیا پلن فعلی فروشگاه به یک ویژگی خاص دسترسی دارد یا خیر
        """
        if not store.is_active or not store.plan or not store.plan.is_active:
            return False
        
        # جستجو در ویژگی‌های فعال پلن اختصاص یافته به فروشگاه
        return store.plan.features.filter(code=feature_code, is_active=True).exists()

    @staticmethod
    def can_add_product(store):
        """
        بررسی می‌کند که آیا فروشگاه از سقف مجاز افزودن محصول در ماه جاری عبور کرده است یا خیر
        """
        if not store.is_active or not store.plan or not store.plan.is_active:
            return False

        now = timezone.now()
        
        # شمارش محصولات موفق ثبت شده در ماه جاری برای این فروشگاه
        current_month_count = ProductLog.objects.filter(
            store=store,
            created_at__year=now.year,
            created_at__month=now.month,
            status='success'
        ).count()

        return current_month_count < store.plan.max_products_per_month

    @staticmethod
    def get_remaining_quota(store):
        """
        دریافت تعداد باقی‌مانده از سهمیه ماهانه فروشگاه
        """
        if not store.plan:
            return 0
            
        now = timezone.now()
        current_month_count = ProductLog.objects.filter(
            store=store,
            created_at__year=now.year,
            created_at__month=now.month,
            status='success'
        ).count()
        
        remaining = store.plan.max_products_per_month - current_month_count
        return max(0, remaining)