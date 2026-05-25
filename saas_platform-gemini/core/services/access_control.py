from django.utils import timezone
from core.models import ProductLog
import jdatetime

class AccessControlService:
    @staticmethod
    def has_feature(store, feature_code):
        if not store.is_active or not store.plan or not store.plan.is_active:
            return False
        return store.plan.features.filter(code=feature_code, is_active=True).exists()

    @staticmethod
    def _get_current_jalali_month_range():
        """محاسبه دقیق ابتدا و انتهای ماه شمسی جاری (بسیار بهینه برای دیتابیس)"""
        now = timezone.localtime(timezone.now())
        j_now = jdatetime.datetime.fromgregorian(datetime=now)
        
        j_start = jdatetime.datetime(j_now.year, j_now.month, 1, 0, 0, 0)
        
        if j_now.month <= 6:
            days_in_month = 31
        elif j_now.month <= 11:
            days_in_month = 30
        else:
            days_in_month = 30 if j_now.isleap() else 29
            
        j_end = jdatetime.datetime(j_now.year, j_now.month, days_in_month, 23, 59, 59)
        
        g_start = timezone.make_aware(j_start.togregorian())
        g_end = timezone.make_aware(j_end.togregorian())
        
        return g_start, g_end

    @staticmethod
    def can_add_product(store):
        if not store.is_active or not store.plan or not store.plan.is_active:
            return False

        g_start, g_end = AccessControlService._get_current_jalali_month_range()
        
        current_month_count = ProductLog.objects.filter(
            store=store,
            created_at__gte=g_start,
            created_at__lte=g_end,
            status='success',
            action_type='add' # 🔴 فقط محصولات جدید را می‌شمارد
        ).count()

        return current_month_count < store.plan.max_products_per_month

    @staticmethod
    def get_remaining_quota(store):
        if not store.plan:
            return 0
            
        g_start, g_end = AccessControlService._get_current_jalali_month_range()
        
        current_month_count = ProductLog.objects.filter(
            store=store,
            created_at__gte=g_start,
            created_at__lte=g_end,
            status='success',
            action_type='add' # 🔴 فقط محصولات جدید را می‌شمارد
        ).count()
        
        remaining = store.plan.max_products_per_month - current_month_count
        return max(0, remaining)