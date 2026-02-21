import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ecommerce_scraper.items import ProductItem
import re

class GorillaSpider(CrawlSpider):
    name = "gorilla"
    allowed_domains = ["goriilashop.com"]
    start_urls = ["https://goriilashop.com"]

    rules = (
        # Follow category links
        Rule(LinkExtractor(allow=r'/product-category/.*'), follow=True),
        # Follow pagination
        Rule(LinkExtractor(allow=r'/page/\d+'), follow=True),
        # Extract product links
        Rule(LinkExtractor(allow=r'/product/.*'), callback='parse_product'),
    )

    def parse_product(self, response):
        item = ProductItem()
        
        # Extract product_id from URL (last part of URL)
        product_slug = response.url.split('/')[-2]  # Gets the product slug
        item['product_id'] = product_slug
        
        # Extract name - from h1 or product title
        name_selectors = [
            '//h1[@class="product_title"]/text()',
            '//h1/text()',
            '//meta[@property="og:title"]/@content'
        ]
        for selector in name_selectors:
            name = response.xpath(selector).get()
            if name:
                item['name'] = name.strip()
                break
        
        # Extract brand - from breadcrumbs or product meta
        brand_selectors = [
            '//nav[@class="woocommerce-breadcrumb"]//a[position()>1]/text()',  # Usually second breadcrumb is brand/category
            '//*[contains(@class, "brand")]/text()',
            '//*[contains(@class, "product-brand")]/text()'
        ]
        for selector in brand_selectors:
            brands = response.xpath(selector).getall()
            if brands:
                # Try to find a brand name (usually second breadcrumb)
                if len(brands) >= 2:
                    item['brand'] = brands[1].strip()
                else:
                    item['brand'] = brands[0].strip()
                break
        else:
            # Default brand based on product name
            if 'بایوتک' in item.get('name', ''):
                item['brand'] = 'Biotech USA'
            elif 'سایتک' in item.get('name', ''):
                item['brand'] = 'Scitec Nutrition'
            else:
                item['brand'] = ''
        
        # Extract category from breadcrumbs
        category_selectors = [
            '//nav[@class="woocommerce-breadcrumb"]//a/text()',
            '//*[contains(@class, "breadcrumb")]//a/text()'
        ]
        for selector in category_selectors:
            categories = response.xpath(selector).getall()
            if categories:
                # Remove "خانه" (home) and join
                categories = [c.strip() for c in categories if c.strip() and 'خانه' not in c]
                item['category'] = ' > '.join(categories)
                break
        else:
            item['category'] = ''
        
        # Extract price - main product price
        price_selectors = [
            '//p[@class="price"]//bdi/text()',
            '//span[@class="woocommerce-Price-amount amount"]//bdi/text()',
            '//ins//span[@class="woocommerce-Price-amount amount"]//bdi/text()',  # Sale price
            '//*[@itemprop="price"]/@content'
        ]
        for selector in price_selectors:
            price_text = response.xpath(selector).get()
            if price_text:
                # Clean price (remove commas and "تومان")
                clean_price = re.sub(r'[^\d,]', '', price_text).strip()
                item['price'] = clean_price
                break
        else:
            # Try to find price in page text
            page_text = response.text
            price_match = re.search(r'([\d,]+)\s*تومان', page_text)
            if price_match:
                item['price'] = price_match.group(1).replace(',', '')
            else:
                item['price'] = ''
        
        # Only yield if we have essential fields
        if item.get('name') and item.get('price'):
            yield item

    def parse_start_url(self, response):
        """Parse the homepage to extract products"""
        # Homepage also has products in sections
        product_containers = response.css('.product')
        
        for product in product_containers:
            item = ProductItem()
            
            # Extract product link and ID
            product_link = product.css('a::attr(href)').get()
            if product_link:
                item['product_id'] = product_link.split('/')[-2] if '/product/' in product_link else ''
                item['url'] = product_link
            
            # Extract name
            item['name'] = product.css('.woocommerce-loop-product__title::text').get()
            if not item['name']:
                item['name'] = product.css('h2::text').get()
            
            # Extract price
            price_text = product.css('.price ins .amount bdi::text').get()  # Sale price first
            if not price_text:
                price_text = product.css('.price .amount bdi::text').get()  # Regular price
            
            if price_text:
                item['price'] = re.sub(r'[^\d,]', '', price_text).strip()
            else:
                item['price'] = ''
            
            # Extract brand from name
            name = item.get('name', '')
            if 'بایوتک' in name:
                item['brand'] = 'Biotech USA'
            elif 'سایتک' in name:
                item['brand'] = 'Scitec Nutrition'
            else:
                item['brand'] = ''
            
            # Extract category based on section
            section = product.xpath('ancestor::section//h2/text()').get()
            if section:
                if 'پرفروش' in section:
                    item['category'] = 'پرفروش‌ترینها'
                elif 'جدید' in section:
                    item['category'] = 'جدیدترین محصولات'
                elif 'ویژه' in section:
                    item['category'] = 'محصولات ویژه'
                else:
                    item['category'] = section.strip()
            else:
                item['category'] = ''
            
            if item.get('name') and item.get('price'):
                yield item