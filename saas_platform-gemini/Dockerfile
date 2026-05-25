FROM python:3.12-slim
# تنظیم متغیرهای محیطی برای عملکرد بهتر پایتون
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تنظیم مسیر کاری
WORKDIR /app

# نصب پیش‌نیازهای سیستمی برای بیلد شدن کتابخانه‌هایی مثل psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌های پایتون
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# کپی کردن سورس پروژه به داخل کانتینر
COPY . /app/