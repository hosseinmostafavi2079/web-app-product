import requests
from woocommerce import API

class WooService:
    def __init__(self, store):
        """
        دریافت آبجکت Store و مقداردهی کلاینت ووکامرس بر اساس تنظیمات اختصاصی همان فروشگاه
        """
        self.store = store
        self.wcapi = API(
            url=self.store.woo_url,
            consumer_key=self.store.woo_consumer_key,
            consumer_secret=self.store.woo_consumer_secret,
            version="wc/v3",
            timeout=40
        )
        # استفاده از کلیدهای ووکامرس به عنوان Basic Auth برای آپلود مدیا
        self.auth = (self.store.woo_consumer_key, self.store.woo_consumer_secret)

    def search_products(self, query):
        try:
            products = self.wcapi.get("products", params={"search": query, "status": "publish"}).json()
            return products
        except Exception as e:
            print(f"Woo Search Error for Store {self.store.name}: {e}")
            return []

    def get_categories(self, parent=0):
        try:
            params = {"per_page": 50, "orderby": "count", "order": "desc", "parent": parent}
            cats = self.wcapi.get("products/categories", params=params).json()
            return cats
        except Exception as e:
            print(f"Get Categories Error for Store {self.store.name}: {e}")
            return []

    def upload_image_to_wp(self, image_data, filename="product.jpg"):
        # حذف اسلش اضافه از انتهای آدرس در صورت وجود
        base_url = self.store.woo_url.rstrip('/')
        url = f"{base_url}/wp-json/wp/v2/media"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "image/jpeg"
        }
        try:
            response = requests.post(url, data=image_data, headers=headers, auth=self.auth)
            if response.status_code == 201:
                return response.json().get('id')
            return None
        except Exception as e:
            print(f"Image Upload Error for Store {self.store.name}: {e}")
            return None

    def create_product(self, title, price, sku, category_id, slug, description, short_description, image_ids):
        meta_data = [{"key": "_yoast_wpseo_focuskw", "value": title}]
        images_data = [{"id": img_id} for img_id in image_ids]

        data = {
            "name": title,
            "type": "simple",
            "regular_price": str(price),
            "sku": sku,
            "slug": slug,
            "description": description,
            "short_description": short_description,
            "categories": [{"id": category_id}] if category_id else [],
            "images": images_data,
            "meta_data": meta_data
        }
        
        try:
            response = self.wcapi.post("products", data)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Create Product Error for Store {self.store.name}: {response.text}")
                return None
        except Exception as e:
            print(f"Create Exception for Store {self.store.name}: {e}")
            return None

    def get_product_by_sku(self, sku):
        try:
            products = self.wcapi.get("products", params={"sku": sku}).json()
            if products:
                return products[0]
            return None
        except Exception as e:
            print(f"Get SKU Error for Store {self.store.name}: {e}")
            return None

    def update_product(self, product_id, data):
        try:
            response = self.wcapi.put(f"products/{product_id}", data)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Update Error for Store {self.store.name}: {e}")
            return None