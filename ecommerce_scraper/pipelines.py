import pyodbc

class SQLServerPipeline:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        # ساخت connection string از اطلاعاتی که داری
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={crawler.settings.get('SQL_SERVER')};"
            f"DATABASE={crawler.settings.get('SQL_DATABASE')};"
            f"UID={crawler.settings.get('SQL_USER')};"
            f"PWD={crawler.settings.get('SQL_PASSWORD')};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=yes"
        )
        return cls(conn_str)

    def open_spider(self, spider):
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            self.create_table()
        except Exception as e:
            spider.logger.error(f"Connection error: {e}")

    def create_table(self):
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='products' AND xtype='U')
        CREATE TABLE products (
            id INT IDENTITY(1,1) PRIMARY KEY,
            product_id NVARCHAR(100),
            name NVARCHAR(500),
            brand NVARCHAR(255),
            category NVARCHAR(500),
            price NVARCHAR(100),
            created_at DATETIME DEFAULT GETDATE(),
            CONSTRAINT unique_product UNIQUE (product_id)
        )
        """
        self.cursor.execute(query)
        self.connection.commit()

    def process_item(self, item, spider):
        try:
            query = """
            MERGE products AS target
            USING (SELECT ? AS product_id) AS source
            ON target.product_id = source.product_id
            WHEN MATCHED THEN
                UPDATE SET name = ?, brand = ?, category = ?, price = ?
            WHEN NOT MATCHED THEN
                INSERT (product_id, name, brand, category, price)
                VALUES (?, ?, ?, ?, ?);
            """
            
            self.cursor.execute(query, (
                item.get('product_id'),
                item.get('name'), item.get('brand'), item.get('category'), item.get('price'),
                item.get('product_id'), item.get('name'), item.get('brand'), 
                item.get('category'), item.get('price')
            ))
            
            self.connection.commit()
            
        except Exception as e:
            spider.logger.error(f"Error saving: {e}")
        
        return item

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()