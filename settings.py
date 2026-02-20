BOT_NAME = 'ecommerce_scraper'
SPIDER_MODULES = ['ecommerce_scraper.spiders']
NEWSPIDER_MODULE = 'ecommerce_scraper.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

ITEM_PIPELINES = {
    'ecommerce_scraper.pipelines.MySQLPipeline': 300,
}

# MySQL Settings - CHANGE THESE
MYSQL_HOST = 'localhost'
MYSQL_DATABASE = 'shop_products'
MYSQL_USER = 'admin'
MYSQL_PASSWORD = '12345678910'

LOG_LEVEL = 'INFO'