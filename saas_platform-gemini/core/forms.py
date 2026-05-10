from django import forms

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
    category_id = forms.IntegerField(
        label="آیدی دسته‌بندی ووکامرس", 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 15'})
    )
    image = forms.ImageField(
        label="تصویر محصول", 
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )