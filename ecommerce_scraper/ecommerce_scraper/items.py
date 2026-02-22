import scrapy

class ProductItem(scrapy.Item):
    product_id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    price = scrapy.Field()