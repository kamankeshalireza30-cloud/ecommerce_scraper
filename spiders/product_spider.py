import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ecommerce_scraper.items import ProductItem
import re

class ProductSpider(CrawlSpider):
    name = "products"
    allowed_domains = ["example.com"]  # Change this
    start_urls = ["https://example.com/products"]  # Change this

    rules = (
        Rule(LinkExtractor(allow=r'category/\w+'), follow=True),
        Rule(LinkExtractor(allow=r'page=\d+'), follow=True),
        Rule(LinkExtractor(allow=r'product/\w+'), callback='parse_product'),
    )

    def parse_product(self, response):
        item = ProductItem()
        
        # Extract product ID from URL
        product_id = re.search(r'product/(\d+)', response.url)
        item['product_id'] = product_id.group(1) if product_id else ''
        
        # Extract name
        name_selectors = [
            '//h1/text()',
            '//h1[@class="product-title"]/text()',
            '//meta[@property="og:title"]/@content',
            '//title/text()'
        ]
        for selector in name_selectors:
            name = response.xpath(selector).get()
            if name:
                item['name'] = name.strip()
                break
        
        # Extract brand
        brand_selectors = [
            '//*[@class="brand"]/text()',
            '//*[@itemprop="brand"]/text()',
            '//*[@class="product-brand"]/text()'
        ]
        for selector in brand_selectors:
            brand = response.xpath(selector).get()
            if brand:
                item['brand'] = brand.strip()
                break
        
        # Extract category from breadcrumbs
        category = response.xpath('//*[@class="breadcrumb"]//a/text()').getall()
        if category:
            item['category'] = ' > '.join([c.strip() for c in category if c.strip()])
        else:
            item['category'] = ''
        
        # Extract price
        price_text = response.xpath('//*[@class="price"]/text()').get()
        if not price_text:
            price_text = response.xpath('//*[@itemprop="price"]/@content').get()
        if not price_text:
            price_text = response.xpath('//span[contains(@class, "price")]/text()').get()
        
        if price_text:
            # Clean price text (remove "تومان" and commas)
            item['price'] = re.sub(r'[^\d,]', '', price_text).strip()
        else:
            item['price'] = ''
        
        # Only yield if we have at least name and price
        if item.get('name') and item.get('price'):
            yield item