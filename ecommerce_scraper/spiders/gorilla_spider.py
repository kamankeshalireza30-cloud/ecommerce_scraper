import scrapy
import re

class GorillaSpider(scrapy.Spider):
    name = "gorilla"
    allowed_domains = ["goriilashop.com"]
    start_urls = ["https://goriilashop.com"]

    def parse(self, response):
        # استخراج محصولات از صفحه اصلی
        products = response.css('.product')
        
        for product in products:
            item = {}
            
            # اسم محصول
            name = product.css('.woocommerce-loop-product__title::text').get()
            if name:
                item['name'] = name.strip()
            else:
                continue
            
            # قیمت
            price = product.css('.price ins .amount bdi::text').get()
            if not price:
                price = product.css('.price .amount bdi::text').get()
            
            if price:
                item['price'] = re.sub(r'[^\d,]', '', price).strip()
            else:
                item['price'] = ''
            
            # برند از روی اسم
            if 'بایوتک' in item['name']:
                item['brand'] = 'Biotech USA'
            elif 'سایتک' in item['name']:
                item['brand'] = 'Scitec Nutrition'
            else:
                item['brand'] = ''
            
            # دسته‌بندی
            item['category'] = ''
            
            # product_id از لینک
            link = product.css('a::attr(href)').get()
            if link:
                item['product_id'] = link.split('/')[-2] if '/product/' in link else ''
            else:
                item['product_id'] = ''
            
            yield item
        
        # پیدا کردن لینک صفحه بعد
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)