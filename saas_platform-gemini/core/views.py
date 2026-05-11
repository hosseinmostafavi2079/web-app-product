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

# (ایمپورت‌ها دست نخورده باقی بمانند)
@login_required
def add_product(request):
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return redirect('dashboard')

    store = user_profile.store

    if not AccessControlService.can_add_product(store):
        messages.error(request, "سقف مجاز افزودن محصول در ماه جاری برای پلن شما به اتمام رسیده است.")
        return redirect('dashboard')
        
    # --- لود کردن سرویس ووکامرس و گرفتن دسته‌بندی‌ها ---
    woo_service = WooService(store)
    categories_data = woo_service.get_categories()

    if request.method == 'POST':
        # --- پاس دادن دسته‌بندی‌ها به فرم POST ---
        form = AddProductForm(request.POST, request.FILES, categories=categories_data)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            price = form.cleaned_data['price']
            sku = form.cleaned_data['sku']
            category_id = form.cleaned_data['category_id']
            
            # گرفتن لیست تمام تصاویر آپلود شده در فرم
            images = request.FILES.getlist('images')
            
            try:
                ai_service = AIService(store)
                woo_service = WooService(store)
                
                slug = ai_service.generate_slug(product_name)
                short_desc = ai_service.generate_short_desc(product_name)
                long_desc = ai_service.generate_long_desc(product_name)
                
                if not long_desc:
                    raise Exception("هوش مصنوعی نتوانست محتوای مناسبی تولید کند.")

                # پردازش و آپلود تمام تصاویر در وردپرس با یک حلقه (Loop)
                image_ids = []
                for img in images:
                    img_id = woo_service.upload_image_to_wp(img.read(), img.name)
                    if img_id:
                        image_ids.append(img_id)
                        
                # ثبت نهایی کالا در ووکامرس
                woo_product = woo_service.create_product(
                    title=product_name,
                    price=price,
                    sku=sku,
                    category_id=int(category_id) if category_id else None,
                    slug=slug,
                    description=long_desc,
                    short_description=short_desc,
                    image_ids=image_ids # این لیست حالا شامل چندین آیدی است
                )
                
                if woo_product:
                    ProductLog.objects.create(store=store, user=request.user, product_name=product_name, woo_product_id=woo_product.get('id'), status='success')
                    messages.success(request, f"محصول «{product_name}» با موفقیت منتشر شد.")
                else:
                    raise Exception("خطا در برقراری ارتباط با ووکامرس و ثبت نهایی محصول.")
                    
            except Exception as e:
                ProductLog.objects.create(store=store, user=request.user, product_name=product_name, status='failed', error_message=str(e))
                messages.error(request, f"خطا در ایجاد محصول: {str(e)}")
                
            return redirect('add_product')
    else:
        # --- پاس دادن دسته‌بندی‌ها به فرم GET ---
        form = AddProductForm(categories=categories_data)
        
    return render(request, 'add_product.html', {'form': form, 'store': store})