import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def uq_crawl(model_suffix, brand="uniqlo"):
    if brand == "gu":
        url = f"https://uq.goodjack.tw/gu-products/{model_suffix}"  # GU 的網址格式
    else:
        url = f"https://uq.goodjack.tw/hmall-products/{model_suffix}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 目前價格
    price_tag = soup.select_one('.grid .four.wide.column h2')
    current_price = price_tag.text.strip().replace('$', '') if price_tag else "N/A"

    high_price = "N/A"
    low_price = "N/A"
    product_name = "N/A"
    product_image = "N/A"

    jsonld_tag = soup.find('script', type='application/ld+json')
    if jsonld_tag and jsonld_tag.string:
        try:
            data = json.loads(jsonld_tag.string)
            offers = data.get('offers', {})
            low_price  = int(float(offers.get('lowPrice', 0)))
            high_price = int(float(offers.get('highPrice', 0)))

            # 商品名稱
            h1_tag = soup.select_one('h1.ts.dividing.big.header')
            if h1_tag:
                sub = h1_tag.find('div', class_='sub header')
                if sub:
                    sub.decompose()
                product_name = h1_tag.get_text(strip=True)

            # 商品圖片
            raw_image = data.get('image', 'N/A')
            if isinstance(raw_image, list):
                product_image = raw_image[0] if raw_image else 'N/A'
            else:
                product_image = raw_image

        except Exception as e:
            return {"error": str(e)}

    return {
        "model": model_suffix,
        "brand": brand, 
        "name": product_name,
        "image": product_image,
        "current_price": current_price,
        "high_price": high_price,
        "low_price": low_price,
        "url": url
    }




if __name__ == "__main__":  #如果沒有網路編號就查詢
    model_suffix = "358337"
    url = f"https://uq.goodjack.tw/gu-products/{model_suffix}" 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # ── 目前價格 ──────────────────────────────────────────────────
    price_tag = soup.select_one('.grid .four.wide.column h2')
    current_price = price_tag.text.strip() if price_tag else "N/A"

    if current_price == "N/A":
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get("https://uq.goodjack.tw/")

            # 等搜尋框出現
            search_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "query"))
            )
            search_input.send_keys(model_suffix)
            search_input.send_keys(Keys.ENTER)

            # 等結果出現
            br_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div[1]/div[3]/div/p/br[3]"))
            )

            target_text = driver.execute_script("return arguments[0].nextSibling.textContent;", br_element)
            target_text = target_text.split('：')[1].strip() if target_text else None
            print(f"抓取到的型號：{target_text}")

        finally:
            driver.quit()

        # ── 用 target_text 重新爬 ────────────────────────────────
        if target_text:
            model_suffix = target_text
            url = f"https://uq.goodjack.tw/gu-products/{model_suffix}"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            price_tag = soup.select_one('.grid .four.wide.column h2')
            current_price = price_tag.text.strip() if price_tag else "N/A"
        else:
            print("找不到對應型號")

    # ── 高低價：從 JSON-LD 抓 ─────────────────────────────────────
    high_price = "N/A"
    low_price = "N/A"
    product_name = "N/A"
    product_image = "N/A"

    jsonld_tag = soup.find('script', type='application/ld+json')
    if jsonld_tag and jsonld_tag.string:
        try:
            data = json.loads(jsonld_tag.string)
            offers = data.get('offers', {})
            low_price  = f"NT${int(float(offers.get('lowPrice', 0)))}"
            high_price = f"NT${int(float(offers.get('highPrice', 0)))}"

            h1_tag = soup.select_one('h1.ts.dividing.big.header')
            if h1_tag:
                sub = h1_tag.find('div', class_='sub header')
                if sub:
                    sub.decompose()
                product_name = h1_tag.get_text(strip=True)
            else:
                product_name = "N/A"

            raw_image = data.get('image', 'N/A')
            product_image = raw_image[0] if isinstance(raw_image, list) else raw_image

        except Exception as e:
            print(f"JSON-LD parse 失敗: {e}")

    # ── 輸出 ──────────────────────────────────────────────────────
    print(f"商品名稱: {product_name}")
    print(f"商品圖片: {product_image}")
    print(f"目前價格: NT${current_price}")
    print(f"歷史高價: {high_price}")
    print(f"歷史低價: {low_price}")
