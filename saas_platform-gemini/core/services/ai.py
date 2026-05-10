import httpx
import json
from openai import OpenAI

class AIService:
    def __init__(self, store):
        """
        دریافت آبجکت Store و راه‌اندازی کلاینت هوش مصنوعی با کلید API اختصاصی مستاجر
        """
        self.store = store
        
        http_client = httpx.Client(
            timeout=120.0,
            follow_redirects=True,
            verify=False,
            trust_env=False  
        )
        
        self.client = OpenAI(
            base_url="https://api.gapgpt.app/v1",
            api_key=self.store.openai_api_key, # خواندن کلید از دیتابیس مشتری
            http_client=http_client,
            max_retries=1
        )

        # لینک‌های داخلی می‌توانند در آینده داینامیک و از طریق ادمین جنگو برای هر فروشگاه تنظیم شوند
        # در حال حاضر مطابق ساختار شما به صورت عمومی قرار داده شده است
        self.internal_links_data = """
        - صفحه اصلی: /
        - فروشگاه: /shop/
        - تماس با ما: /contact-us/
        - وبلاگ: /blog/
        """

    def _send_request(self, system_msg, user_msg):
        if not self.store.openai_api_key:
            print(f"⚠️ No AI API Key found for store: {self.store.name}")
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.6
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            
            if isinstance(response, str):
                if "data: {" in response:
                    full_text = ""
                    for line in response.split('\n'):
                        line = line.strip()
                        if line.startswith('data: ') and line != 'data: [DONE]':
                            try:
                                json_str = line.replace('data: ', '')
                                data = json.loads(json_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_text += content
                            except:
                                pass 
                    return full_text.strip()
                return response.strip()

            return None

        except Exception as e:
            print(f"⚠️ AI Connection Error for Store {self.store.name}: {e}")
            return None

    def generate_slug(self, product_name):
        sys = "You are a specialized SEO URL generator."
        usr = f"Create a short, SEO-friendly English URL slug for: '{product_name}'. Use lowercase, hyphens only. Remove stop words."
        result = self._send_request(sys, usr)
        if result:
            return result.replace(" ", "-").lower()
        return None

    def generate_short_desc(self, product_name):
        sys = 'You are an expert SEO Copywriter. You MUST output in PERSIAN only.'
        usr = (
            f"Write a trustworthy, 2-line Persian product summary for: '{product_name}'.\n"
            "Focus on: Compatibility, Build Quality, and Reliable Performance.\n"
            "Keywords to include: [کیفیت ساخت بالا, سازگاری کامل].\n"
            "Strict Rules: NO emojis. NO price. Max 2 lines."
        )
        return self._send_request(sys, usr)

    def generate_long_desc(self, product_name):
        sys = 'You are a Senior Technical Writer & SEO Specialist. Output in PERSIAN only.'
        usr = (
            f"Act as a Senior SEO Content Specialist.\n"
            f"Write a comprehensive, HTML-formatted product page for: '{product_name}'.\n\n"
            "**CRITICAL RULE:** NEVER mention unrealistic claims or price fluctuations in the text.\n"
            "Focus ONLY on technical specifications, compatibility, material quality, durability, installation notes.\n\n"
            "Generate dynamic H3 headers and a dynamic FAQ section relevant to this product.\n"
            f"Use the following internal links strategically:\n{self.internal_links_data}\n\n"
            "Output strictly in raw HTML format (No <html>/<body> tags).\n"
            "Tone: Technical, Professional, Helpful."
        )
        return self._send_request(sys, usr)