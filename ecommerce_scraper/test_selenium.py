from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

print("Starting Selenium test...")

# تنظیمات Chrome
options = Options()
options.add_argument("--headless")  # اجرای بدون پنجره
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

# راه‌اندازی driver
print("Installing Chrome driver...")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("Loading page...")
driver.get("https://goriilashop.com")
time.sleep(5)

print("Page loaded, searching for products...")

# پیدا کردن محصولات
products = driver.find_elements(By.CSS_SELECTOR, '.product')
print(f"Found {len(products)} products")

results = []
for i, product in enumerate(products[:10]):
    try:
        # اسم محصول
        name_elem = product.find_element(By.CSS_SELECTOR, '.woocommerce-loop-product__title')
        name = name_elem.text
        
        # قیمت
        try:
            price_elem = product.find_element(By.CSS_SELECTOR, '.price ins .amount bdi')
            price = price_elem.text
        except:
            try:
                price_elem = product.find_element(By.CSS_SELECTOR, '.price .amount bdi')
                price = price_elem.text
            except:
                price = "Price not found"
        
        results.append({
            'name': name,
            'price': price
        })
        print(f"{i+1}. {name}: {price}")
        
    except Exception as e:
        print(f"Error on product {i}: {e}")

# ذخیره نتایج
with open('selenium_test.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

driver.quit()
print(f"Done! {len(results)} products saved to selenium_test.json")