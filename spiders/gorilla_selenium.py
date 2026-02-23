import scrapy
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class GorillaSeleniumSpider(scrapy.Spider):
    name = "gorilla_selenium"
    allowed_domains = ["goriilashop.com"]
    start_urls = ["https://goriilashop.com"]

    def __init__(self):
        # تنظیمات Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # اجرای بدون پنجره
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.implicitly_wait(10)

    def parse(self, response):
        self.logger.info(f"Loading page with Selenium: {response.url}")
        
        # لود صفحه با Selenium
        self.driver.get(response.url)
        
        # صبر برای لود محتوا
        time.sleep(3)
        
        # اسکرول به پایین برای لود همه محصولات
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # پیدا کردن محصولات
        product_elements = self.driver.find_elements(By.CSS_SELECTOR, '.product')
        self.logger.info(f"Found {len(product_elements)} products with Selenium")
        
        for product in product_elements[:5]:  # فقط 5 تا برای تست
            try:
                item = {}
                
                # اسم محصول
                name_elem = product.find_element(By.CSS_SELECTOR, '.woocommerce-loop-product__title')
                item['name'] = name_elem.text.strip() if name_elem else ''
                
                # قیمت
                try:
                    price_elem = product.find_element(By.CSS_SELECTOR, '.price ins .amount bdi')
                    if not price_elem:
                        price_elem = product.find_element(By.CSS_SELECTOR, '.price .amount bdi')
                    price_text = price_elem.text
                    item['price'] = re.sub(r'[^\d]', '', price_text)
                except:
                    item['price'] = ''
                
                # برند
                if 'بایوتک' in item['name']:
                    item['brand'] = 'Biotech USA'
                elif 'سایتک' in item['name']:
                    item['brand'] = 'Scitec Nutrition'
                else:
                    item['brand'] = ''
                
                # دسته‌بندی
                item['category'] = ''
                
                # product_id از لینک
                try:
                    link_elem = product.find_element(By.CSS_SELECTOR, 'a')
                    link = link_elem.get_attribute('href')
                    if link and '/product/' in link:
                        item['product_id'] = link.rstrip('/').split('/')[-1]
                    else:
                        item['product_id'] = ''
                except:
                    item['product_id'] = ''
                
                self.logger.info(f"Product: {item['name']} - {item['price']} تومان")
                yield item
                
            except Exception as e:
                self.logger.error(f"Error parsing product: {e}")
        
        # پیدا کردن لینک صفحه بعد
        try:
            next_page = self.driver.find_element(By.CSS_SELECTOR, 'a.next')
            if next_page:
                next_url = next_page.get_attribute('href')
                if next_url:
                    yield scrapy.Request(next_url, callback=self.parse)
        except:
            pass

    def closed(self, reason):
        self.driver.quit()