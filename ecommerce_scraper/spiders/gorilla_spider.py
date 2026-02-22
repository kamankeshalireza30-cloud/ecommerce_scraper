import scrapy
import re

class GorillaSpider(scrapy.Spider):
    name = "gorilla"
    allowed_domains = ["goriilashop.com"]
    start_urls = ["https://goriilashop.com"]

    def parse(self, response):
        self.logger.info(f"Parsing {response.url}")
        
        # سلکتورهای مختلف برای محصولات
        products = response.css('.product')
        if not products:
            products = response.css('li.product')
        if not products:
            products = response.css('.products > div')
        if not products:
            products = response.css('[class*="product"]')
        
        self.logger.info(f"Found {len(products)} products")
        
        for product in products:
            item = {}
            
            # اسم محصول - روش‌های مختلف
            name = (
                product.css('.woocommerce-loop-product__title::text').get() or
                product.css('h2::text').get() or
                product.css('.product-title::text').get() or
                product.css('[class*="title"]::text').get()
            )
            
            if name:
                item['name'] = name.strip()
            else:
                continue
            
            # قیمت - روش‌های مختلف
            price = (
                product.css('.price ins .amount bdi::text').get() or
                product.css('.price .amount bdi::text').get() or
                product.css('.price ins::text').get() or
                product.css('.price::text').get() or
                product.css('[class*="price"]::text').get()
            )
            
            if price:
                # پاکسازی قیمت (حذف تومان، کاما و ...)
                clean_price = re.sub(r'[^\d,]', '', price).strip()
                item['price'] = clean_price
            else:
                item['price'] = ''
            
            # برند از روی اسم
            name_lower = item['name'].lower()
            if 'بایوتک' in name_lower or 'biotech' in name_lower:
                item['brand'] = 'Biotech USA'
            elif 'سایتک' in name_lower or 'scitec' in name_lower:
                item['brand'] = 'Scitec Nutrition'
            else:
                item['brand'] = ''
            
            # دسته‌بندی - از روی breadcrumb یا متن
            item['category'] = ''
            
            # product_id از لینک
            link = product.css('a::attr(href)').get()
            if link:
                # استخراج ID از لینک
                match = re.search(r'/product/([^/]+)', link)
                if match:
                    item['product_id'] = match.group(1)
                else:
                    item['product_id'] = link.split('/')[-2] if link.count('/') > 1 else ''
            else:
                item['product_id'] = ''
            
            self.logger.info(f"Yielding item: {item.get('name')} - {item.get('price')}")
            yield item
        
        # صفحه بعد
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)