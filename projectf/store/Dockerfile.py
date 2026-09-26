# استخدام صورة بايثون الرسمية
FROM python:3.12-slim

# تحديد مجلد العمل جوه الحاوية
WORKDIR /app

# تثبيت المكتبات النظامية الضرورية
RUN apt-get update && apt-get install -y libpq-dev gcc

# نسخ متطلبات المشروع وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# أمر تشغيل السيرفر
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]