import mysql.connector
from mysql.connector import Error
from itemadapter import ItemAdapter

class MySQLPipeline:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD')
        )

    def open_spider(self, spider):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            self.cursor = self.connection.cursor()
            self.create_table()
        except Error as e:
            spider.logger.error(f"Connection error: {e}")

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id VARCHAR(100),
            name VARCHAR(500),
            brand VARCHAR(255),
            category VARCHAR(500),
            price VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_product (product_id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        self.cursor.execute(query)
        self.connection.commit()

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)
            
            query = """
            INSERT INTO products (product_id, name, brand, category, price)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                brand = VALUES(brand),
                category = VALUES(category),
                price = VALUES(price)
            """
            
            self.cursor.execute(query, (
                adapter.get('product_id'),
                adapter.get('name'),
                adapter.get('brand'),
                adapter.get('category'),
                adapter.get('price')
            ))
            
            self.connection.commit()
            
        except Error as e:
            spider.logger.error(f"Error saving: {e}")
            self.connection.rollback()
        
        return item

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()