import scrapy
import re
import sys
import os

# اضافه کردن مسیر پروژه به PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ..items import ProductItem
except ImportError:
    # راه جایگزین
    from ecommerce_scraper.items import ProductItem

class GorillaSpider(scrapy.Spider):
    name = "gorilla"
    allowed_domains = ["goriilashop.com"]
    start_urls = ["https://goriilashop.com/"]

    def parse(self, response):
        # پیدا کردن تمام کارت‌های محصول
        products = response.css('div.product-card')
        
        self.logger.info(f"تعداد محصولات پیدا شده: {len(products)}")
        
        for product in products:
            item = ProductItem()
            
            # استخراج ID محصول از دکمه addToCart
            add_to_cart = product.xpath('.//button[contains(@onclick, "addToCart")]/@onclick').get()
            if add_to_cart:
                product_id = re.search(r'addToCart\((\d+)\)', add_to_cart)
                item['product_id'] = product_id.group(1) if product_id else None
            else:
                item['product_id'] = None
            
            # نام محصول
            item['name'] = product.css('h4.product-title a::text').get(default='').strip()
            
            # دسته‌بندی و برند
            categories = product.css('div.product-category::text').getall()
            if len(categories) >= 1:
                item['category'] = categories[0].strip()
            else:
                item['category'] = ''
                
            if len(categories) >= 2:
                item['brand'] = categories[1].strip()
            else:
                item['brand'] = ''
            
            # قیمت
            price_text = product.css('div.product-price.formatted-price::text').get()
            if price_text:
                item['price'] = int(re.sub(r'[^\d]', '', price_text))
            else:
                item['price'] = 0
            
            # فقط محصولاتی که اسم دارن و تبلیغ نیستن رو برگردون
            if item['name'] and not any(x in item['name'] for x in ['جدیدترین', 'پرفروش', 'موارد ویژه', 'مسعود', 'زینک']):
                yield item