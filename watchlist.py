import json
import os
import smtplib
import datetime
from main import uq_crawl 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

WATCHLIST_FILE = "watchlist.json"
# ── Email 設定 ────────────────────────────────────────────────
GMAIL_USER     = "pre665539@gmail.com"
GMAIL_PASSWORD = "ybgn bbau fhxt kisq"
NOTIFY_TO      = "a34434258@gmail.com"  # 可以填自己

def send_email(subject, body_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = NOTIFY_TO

    msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, NOTIFY_TO, msg.as_string())

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return []
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_watchlist(data):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_to_watchlist(model, brand, name, url, current_price):
    watchlist = load_watchlist()
    # 同時比對 model + brand
    if any(item["model"] == model and item["brand"] == brand for item in watchlist):
        return False
    watchlist.append({
        "model": model,
        "brand": brand,
        "name": name,
        "url": url,
        "current_price": int(current_price)  # ← 新增，訂閱當下的價格
    })
    save_watchlist(watchlist)
    return True

def remove_from_watchlist(model, brand):
    watchlist = load_watchlist()
    # 同時比對 model + brand 才刪除
    new_list = [
        item for item in watchlist
        if not (item["model"] == model and item["brand"] == brand)
    ]
    save_watchlist(new_list)

def is_subscribed(model, brand):
    watchlist = load_watchlist()
    return any(item["model"] == model and item["brand"] == brand for item in watchlist)

def main():
    watchlist = load_watchlist()
    if not watchlist:
        print("訂閱清單是空的")
        return

    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    rows = ""
    updated = False
    for item in watchlist:
        result = uq_crawl(item["model"], item["brand"])
        if "error" in result:
            continue
        new_price = int(result['current_price'])
        saved_price = int(item.get("current_price", new_price))  # 讀取 JSON 記錄的價
        is_low = new_price  == int(result['low_price'])
        tag = "🔥 歷史低價！" if is_low else ""
        badge_color = "#27ae60" if is_low else "#888"

        price_drop = new_price < saved_price
        drop_tag = f"📉 降價！（{saved_price} → {new_price}）" if price_drop else ""
        rows += f"""
        <tr>
            <td><img src="{result['image']}" width="60"><br>{item['name']}</td>
            <td style="color:{badge_color}"><b>NT${new_price}</b><br>{tag}{drop_tag}</td>
            <td>NT${result['high_price']}</td>
            <td>NT${result['low_price']}</td>
            <td><a href="{item['url']}">前往</a></td>
        </tr>
        """

        # ── 若有降價，更新 JSON 並準備寄信 ───────────────
        if price_drop:
            item["current_price"] = new_price  # 更新 JSON 紀錄
            updated = True
            drop_html = f"""
            <h2>📉 {item['name']} 降價通知</h2>
            <p>型號：{item['model']} ({item['brand'].upper()})</p>
            <p>原紀錄價格：<b>NT${saved_price}</b></p>
            <p>目前價格：<b style="color:red">NT${new_price}</b></p>
            <p><a href="{item['url']}">立即前往商品頁</a></p>
            """
            send_email(
                subject=f"【降價通知】{item['name']} 現在 NT${new_price}",
                body_html=drop_html
            )
            print(f"✅ 寄出降價通知：{item['name']} {saved_price} → {new_price}")

    # ── 若有任何降價，更新 watchlist.json ─────────────
    if updated:
        save_watchlist(watchlist)

    # ── 每日總覽信件（原有邏輯）───────────────────────
    html = f"""..."""  # 你原有的 HTML 模板
    send_email(subject=f"【UQ Watch】每日價格報告 {now}", body_html=html)


if __name__ == "__main__":
    main()
