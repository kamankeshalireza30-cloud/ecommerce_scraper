import scrapy
import re

class GorillaSpider(scrapy.Spider):
    name = "gorilla"
    allowed_domains = ["goriilashop.com"]
    start_urls = ["https://goriilashop.com/"]

    def parse(self, response):
        # پیدا کردن تمام کارت‌های محصول
        products = response.css('div.product-card')
        
        self.logger.info(f"تعداد محصولات پیدا شده: {len(products)}")
        
        for product in products:
            # استخراج ID محصول از دکمه addToCart
            add_to_cart = product.xpath('.//button[contains(@onclick, "addToCart")]/@onclick').get()
            product_id = None
            if add_to_cart:
                product_id_match = re.search(r'addToCart\((\d+)\)', add_to_cart)
                product_id = product_id_match.group(1) if product_id_match else None
            
            # نام محصول
            name = product.css('h4.product-title a::text').get(default='').strip()
            
            # دسته‌بندی و برند
            categories = product.css('div.product-category::text').getall()
            category = categories[0].strip() if len(categories) >= 1 else ''
            brand = categories[1].strip() if len(categories) >= 2 else ''
            
            # قیمت
            price_text = product.css('div.product-price.formatted-price::text').get()
            price = 0
            if price_text:
                price = int(re.sub(r'[^\d]', '', price_text))
            
            # فیلتر کردن موارد غیرمحصول
            if name and not any(x in name for x in ['جدیدترین', 'پرفروش', 'موارد ویژه', 'مسعود', 'زینک']):
                yield {
                    'product_id': product_id,
                    'name': name,
                    'brand': brand,
                    'category': category,
                    'price': price
                }