from django.db import models
from django.contrib.auth.models import User
import jdatetime
from django.utils.timezone import localtime
from django_cryptography.fields import encrypt

class Feature(models.Model):
    """مدیریت قابلیت‌های سیستم که می‌توانند به پلن‌ها اختصاص یابند"""
    name = models.CharField(max_length=100, verbose_name="نام ویژگی")
    code = models.SlugField(max_length=100, unique=True, verbose_name="کد ویژگی (انگلیسی)")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"

    def __str__(self):
        return self.name

class Plan(models.Model):
    """پلن‌های اشتراکی برای فروشگاه‌ها"""
    name = models.CharField(max_length=100, verbose_name="نام پلن")
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت (تومان)")
    features = models.ManyToManyField(Feature, blank=True, verbose_name="ویژگی‌های فعال")
    max_products_per_month = models.IntegerField(default=10, verbose_name="حداکثر محصول در ماه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "اشتراک"
        verbose_name_plural = "اشتراک‌ها"

    def __str__(self):
        return self.name

class Store(models.Model):
    """مستاجر اصلی سیستم: هر فروشگاه تنظیمات و کلیدهای اختصاصی خودش را دارد"""
    name = models.CharField(max_length=200, verbose_name="نام فروشگاه")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="پلن اشتراک")
    
    woo_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="آدرس سایت ووکامرس")
    woo_consumer_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="کلید مشتری ووکامرس (Consumer Key)")
    woo_consumer_secret = encrypt(models.CharField(max_length=255, blank=True, null=True, verbose_name="رمز مشتری ووکامرس (Consumer Secret)"))
    
    # -------- این دو فیلد برای حل مشکل آپلود عکس اضافه شدند --------
    wp_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="نام کاربری ادمین وردپرس")
    wp_app_password = encrypt(models.CharField(max_length=255, blank=True, null=True, verbose_name="رمز عبور برنامه (Application Password)"))
    # ---------------------------------------------------------------

    openai_api_key = encrypt(models.CharField(max_length=255, blank=True, null=True, verbose_name="کلید API هوش مصنوعی"))
    bot_token = encrypt(models.CharField(max_length=255, blank=True, null=True, verbose_name="توکن ربات پیام‌رسان"))
    
    is_active = models.BooleanField(default=True, verbose_name="وضعیت دسترسی فروشگاه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "فروشگاه (مستاجر)"
        verbose_name_plural = "فروشگاه‌ها"

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """اتصال کاربران جنگو به فروشگاه‌ها با سطح دسترسی مشخص"""
    ROLE_CHOICES = (
        ('admin', 'مدیر فروشگاه'),
        ('operator', 'اپراتور'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="کاربر")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='users', verbose_name="فروشگاه")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='operator', verbose_name="نقش کاربری")

    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل کاربران"

    def __str__(self):
        return f"{self.user.username} ({self.store.name})"

class ProductLog(models.Model):
    """سیستم لاگ‌گیری و گزارش‌گیری اختصاصی برای هر فروشگاه با تفکیک عملیات"""
    STATUS_CHOICES = (
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
    )
    ACTION_CHOICES = (
        ('add', 'افزودن محصول'),
        ('update', 'ویرایش محصول'),
    )
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='product_logs', verbose_name="فروشگاه")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="کاربر ایجاد کننده")
    product_name = models.CharField(max_length=255, verbose_name="نام محصول")
    woo_product_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="آیدی محصول در ووکامرس")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success', verbose_name="وضعیت")
    
    # -------- دو فیلد جدید برای تفکیک تب‌ها و ثبت جزییات دقیق تغییرات --------
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, default='add', verbose_name="نوع عملیات")
    details = models.TextField(blank=True, null=True, verbose_name="جزئیات تغییرات قیمت و موجودی")
    # ----------------------------------------------------------------------
    
    error_message = models.TextField(blank=True, null=True, verbose_name="پیام خطا (در صورت وجود)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "لاگ محصول"
        verbose_name_plural = "لاگ محصولات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product_name} - {self.get_action_type_display()} - {self.get_status_display()}"

    @property
    def jalali_date(self):
        local_dt = localtime(self.created_at)
        jd = jdatetime.datetime.fromgregorian(datetime=local_dt)
        return jd.strftime("%Y/%m/%d - %H:%M")

class InternalLink(models.Model):
    """مدل ذخیره لینک‌های داخلی هر فروشگاه برای استفاده در هوش مصنوعی"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='internal_links', verbose_name="فروشگاه")
    title = models.CharField(max_length=255, verbose_name="عنوان صفحه (مثلا: قطعات یخچال)")
    url = models.URLField(max_length=500, verbose_name="لینک کامل (همراه با https)")

    class Meta:
        verbose_name = "لینک داخلی"
        verbose_name_plural = "لینک‌های داخلی"

    def __str__(self):
        return f"{self.title} - {self.store.name}"