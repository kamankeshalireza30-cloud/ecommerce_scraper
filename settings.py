# جایگزین کردن MySQL Pipeline با SQL Server Pipeline
ITEM_PIPELINES = {
    'ecommerce_scraper.pipelines.SQLServerPipeline': 300,
}

# تنظیمات SQL Server (با اطلاعات خودت)
SQL_SERVER = 'localhost'  # یا localhost
SQL_DATABASE = 'shop_products'  # اسم دیتابیس
SQL_USER = 'sa'  # همونی که تو عکس هست
SQL_PASSWORD = 'Password'  # رمز عبورت