# تنظیمات مخصوص گوریلا شاپ
BOT_NAME = 'ecommerce_scraper'

SPIDER_MODULES = ['ecommerce_scraper.spiders']
NEWSPIDER_MODULE = 'ecommerce_scraper.spiders'

# احترام به robots.txt
ROBOTSTXT_OBEY = True

# تاخیر بین درخواست‌ها
DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True

# User-Agent مناسب
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# ذخیره‌سازی خروجی
FEEDS = {
    'gorilla_products.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 4,
        'overwrite': True,
    },
    'gorilla_products.csv': {
        'format': 'csv',
        'encoding': 'utf-8-sig',  # برای نمایش صحیح فارسی در اکسل
        'overwrite': True,
    }
}

# فعال‌سازی کش برای سرعت بیشتر در تست
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 ساعت
HTTPCACHE_DIR = 'httpcache'