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
    ویوی افزودن محصول هوشمند با قابلیت آپلود گالری تصاویر
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return redirect('dashboard')

    store = user_profile.store

    if not AccessControlService.can_add_product(store):
        messages.error(request, "سقف مجاز افزودن محصول در ماه جاری برای پلن شما به اتمام رسیده است.")
        return redirect('dashboard')
        
    # لود کردن سرویس ووکامرس و گرفتن دسته‌بندی‌ها برای نمایش در فرم
    woo_service = WooService(store)
    categories_data = woo_service.get_categories()

    if request.method == 'POST':
        # پاس دادن دسته‌بندی‌ها به فرم برای اعتبارسنجی
        form = AddProductForm(request.POST, request.FILES, categories=categories_data)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            price = form.cleaned_data['price']
            sku = form.cleaned_data['sku']
            category_id = form.cleaned_data['category_id']
            
            # گرفتن لیست تمام تصاویر آپلود شده (Gallery)
            images = request.FILES.getlist('images')
            
            try:
                ai_service = AIService(store)
                
                # ۱. تولید محتوا با هوش مصنوعی
                slug = ai_service.generate_slug(product_name)
                short_desc = ai_service.generate_short_desc(product_name)
                long_desc = ai_service.generate_long_desc(product_name)
                
                if not long_desc:
                    raise Exception("هوش مصنوعی نتوانست محتوای مناسبی تولید کند.")

                # ۲. پردازش و آپلود تمام تصاویر در وردپرس
                image_ids = []
                for img in images:
                    img_id = woo_service.upload_image_to_wp(img.read(), img.name)
                    if img_id:
                        image_ids.append(img_id)
                        
                # ۳. ثبت نهایی کالا در ووکامرس
                woo_product = woo_service.create_product(
                    title=product_name,
                    price=price,
                    sku=sku,
                    category_id=int(category_id) if category_id else None,
                    slug=slug,
                    description=long_desc,
                    short_description=short_desc,
                    image_ids=image_ids
                )
                
                if woo_product:
                    # ثبت لاگ موفقیت
                    ProductLog.objects.create(
                        store=store, 
                        user=request.user, 
                        product_name=product_name, 
                        woo_product_id=woo_product.get('id'), 
                        status='success'
                    )
                    messages.success(request, f"محصول «{product_name}» با موفقیت ساخته و در سایت منتشر شد.")
                else:
                    raise Exception("خطا در برقراری ارتباط با ووکامرس و ثبت نهایی محصول.")
                    
            except Exception as e:
                # ثبت لاگ خطا
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
        form = AddProductForm(categories=categories_data)
        
    return render(request, 'add_product.html', {'form': form, 'store': store})


@login_required
def product_manager(request):
    """
    ویوی مدیریت محصولات: فیلتر، جستجو، تغییر قیمت گروهی و ویرایش تکی
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return redirect('dashboard')

    store = user_profile.store

    # بررسی دسترسی کاربر به این قابلیت از طریق پلن
    if not AccessControlService.has_feature(store, 'price_manager'):
        messages.error(request, "پلن اشتراکی شما به بخش مدیریت قیمت و موجودی دسترسی ندارد.")
        return redirect('dashboard')

    woo_service = WooService(store)
    categories_data = woo_service.get_categories()

    # --- ۱. هندل کردن تغییر قیمت گروهی (Bulk Update) ---
    if request.method == 'POST' and 'bulk_update' in request.POST:
        bulk_category = request.POST.get('bulk_category')
        action = request.POST.get('action') # increase یا decrease
        percent = float(request.POST.get('percent', 0))
        
        if bulk_category and percent > 0:
            updated_count = woo_service.batch_update_prices(bulk_category, percent, action)
            if updated_count > 0:
                messages.success(request, f"قیمت {updated_count} محصول با موفقیت {action == 'increase' and 'افزایش' or 'کاهش'} یافت.")
            elif updated_count == 0:
                messages.warning(request, "محصولی برای تغییر قیمت در این دسته پیدا نشد.")
            else:
                messages.error(request, "خطا در عملیات بروزرسانی گروهی.")
        return redirect('product_manager')

    # --- ۲. هندل کردن ویرایش تکی محصول (Single Update) ---
    if request.method == 'POST' and 'single_update' in request.POST:
        product_id = request.POST.get('product_id')
        payload = {
            "regular_price": str(request.POST.get('regular_price', '')),
            "sale_price": str(request.POST.get('sale_price', '')),
            "stock_status": request.POST.get('stock_status')
        }
        
        result = woo_service.update_product(product_id, payload)
        if result:
            messages.success(request, f"بروزرسانی تکی «{result.get('name')}» انجام شد.")
        else:
            messages.error(request, "خطا در بروزرسانی محصول.")
        return redirect('product_manager')

    # --- ۳. هندل کردن نمایش لیست و فیلترها (GET) ---
    search_q = request.GET.get('search', '')
    sku_q = request.GET.get('sku', '')
    cat_q = request.GET.get('category', '')
    stock_q = request.GET.get('stock_status', '')
    page = int(request.GET.get('page', 1))

    # دریافت محصولات فیلتر شده از سرویس ووکامرس
    products, total_pages = woo_service.get_products_filtered(
        page=page, per_page=20, search=search_q, category=cat_q, stock_status=stock_q, sku=sku_q
    )

    context = {
        'store': store,
        'products': products,
        'categories': categories_data,
        'current_page': page,
        'total_pages': total_pages,
        'page_range': range(1, total_pages + 1),
        'search_q': search_q,
        'sku_q': sku_q,
        'cat_q': cat_q,
        'stock_q': stock_q,
    }
    return render(request, 'product_manager.html', context)