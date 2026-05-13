from django import forms

# 🔴 ۱. ویجت اختصاصی برای دریافت چند فایل
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

# 🔴 ۲. فیلد اختصاصی که به جنگو یاد می‌دهد چطور لیست فایل‌ها را اعتبارسنجی کند
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            # اگر لیست بود، تک تک فایل‌ها را بررسی کن
            result = [single_file_clean(d, initial) for d in data if d]
        else:
            result = single_file_clean(data, initial)
        return result

class AddProductForm(forms.Form):
    product_name = forms.CharField(
        max_length=200, 
        label="نام محصول",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: پمپ تخلیه لباسشویی ال جی'})
    )
    price = forms.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        label="قیمت (تومان)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 500000'})
    )
    sku = forms.CharField(
        max_length=50, 
        label="شناسه محصول (SKU)", 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شناسه یکتا کالا (اختیاری)'})
    )
    
    category_id = forms.ChoiceField(
        label="دسته‌بندی ووکامرس", 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 🔴 ۳. استفاده از فیلد جدیدی که بالا ساختیم
    images = MultipleFileField(
        label="تصاویر محصول (اولین عکس شاخص می‌شود)", 
        required=False
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        super(AddProductForm, self).__init__(*args, **kwargs)
        
        cat_dict = {cat['id']: cat for cat in categories if isinstance(cat, dict)}
        
        def get_full_name(cat_id, visited=None):
            if visited is None:
                visited = set()
                
            if cat_id in visited:
                return ""
            visited.add(cat_id)
            
            cat = cat_dict.get(cat_id)
            if not cat:
                return ""
                
            parent_id = cat.get('parent', 0)
            
            if parent_id == 0:
                return cat.get('name', '')
            else:
                parent_name = get_full_name(parent_id, visited)
                return f"{parent_name} > {cat.get('name', '')}" if parent_name else cat.get('name', '')

        formatted_choices = []
        for cat in categories:
            if isinstance(cat, dict) and 'id' in cat:
                full_name = get_full_name(cat['id'])
                formatted_choices.append((str(cat['id']), full_name))
                
        formatted_choices.sort(key=lambda x: x[1])
        formatted_choices.insert(0, ('', '--- انتخاب دسته‌بندی از سایت ---'))
        
        self.fields['category_id'].choices = formatted_choices