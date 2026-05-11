from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProductLog
from .forms import AddProductForm
from .services.access_control import AccessControlService
from .services.ai import AIService
from .services.woo import WooService

@login_required
def dashboard(request):
    """
    ویوی داشبورد اختصاصی هر مستاجر
    """
    # دریافت فروشگاه اختصاصی کاربر
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        messages.error(request, "حساب کاربری شما به هیچ فروشگاهی متصل نیست.")
        return render(request, 'dashboard.html', {'error': True})

    store = user_profile.store
    
    # دریافت آمار و ارقام
    remaining_quota = AccessControlService.get_remaining_quota(store)
    recent_logs = ProductLog.objects.filter(store=store).order_by('-created_at')[:10]
    
    context = {
        'store': store,
        'remaining_quota': remaining_quota,
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_product(request):
    """
    ویوی افزودن محصول با بررسی سهمیه پلن و اجرای سرویس‌های AI و WooCommerce
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return redirect('dashboard')

    store = user_profile.store

    # 1. بررسی محدودیت سهمیه ماهانه قبل از انجام هر کاری
    if not AccessControlService.can_add_product(store):
        messages.error(request, "سقف مجاز افزودن محصول در ماه جاری برای پلن شما به اتمام رسیده است.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            price = form.cleaned_data['price']
            sku = form.cleaned_data['sku']
            category_id = form.cleaned_data['category_id']
            image = form.cleaned_data['image']
            
            try:
                # 2. مقداردهی سرویس‌ها با استفاده از تنظیمات فروشگاه همین کاربر
                ai_service = AIService(store)
                woo_service = WooService(store)
                
                # 3. تولید محتوا با هوش مصنوعی
                slug = ai_service.generate_slug(product_name)
                short_desc = ai_service.generate_short_desc(product_name)
                long_desc = ai_service.generate_long_desc(product_name)
                
                if not long_desc:
                    raise Exception("هوش مصنوعی نتوانست محتوای مناسبی تولید کند. لطفاً مجدداً تلاش کنید.")

                # 4. آپلود تصویر در وردپرس (در صورت وجود)
                image_ids = []
                if image:
                    img_id = woo_service.upload_image_to_wp(image.read(), image.name)
                    if img_id:
                        image_ids.append(img_id)
                        
                # 5. ثبت نهایی کالا در ووکامرس
                woo_product = woo_service.create_product(
                    title=product_name,
                    price=price,
                    sku=sku,
                    category_id=category_id,
                    slug=slug,
                    description=long_desc,
                    short_description=short_desc,
                    image_ids=image_ids
                )
                
                if woo_product:
                    # لاگ موفقیت
                    ProductLog.objects.create(
                        store=store,
                        user=request.user,
                        product_name=product_name,
                        woo_product_id=woo_product.get('id'),
                        status='success'
                    )
                    messages.success(request, f"محصول «{product_name}» با موفقیت توسط هوش مصنوعی ساخته و در سایت شما منتشر شد.")
                else:
                    raise Exception("خطا در برقراری ارتباط با ووکامرس و ثبت نهایی محصول.")
                    
            except Exception as e:
                # لاگ شکست
                ProductLog.objects.create(
                    store=store,
                    user=request.user,
                    product_name=product_name,
                    status='failed',
                    error_message=str(e)
                )
                messages.error(request, f"خطا در ایجاد محصول: {str(e)}")
                
            return redirect('add_product')
    else:
        form = AddProductForm()
        
    return render(request, 'add_product.html', {'form': form, 'store': store})