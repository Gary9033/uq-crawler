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
    updated = False

    for item in watchlist:
        result = uq_crawl(item["model"], item["brand"])
        if "error" in result:
            continue

        new_price = int(result['current_price'])
        saved_price = int(item.get("current_price", new_price))
        is_low = new_price == int(result['low_price'])
        tag = "🔥 歷史低價！" if is_low else ""
        badge_color = "#27ae60" if is_low else "#888"

        # ── 有降價才寄信 ──────────────────────────────────────
        if new_price < saved_price:
            item["current_price"] = new_price
            updated = True

            html = f"""
            <div style="font-family:sans-serif;max-width:600px;margin:auto">
              <h2 style="color:#2c3e50">🛍 UQ Watch 每日價格報告</h2>
              <p style="color:#888">{now}</p>
              <table width="100%" border="0" cellspacing="0" cellpadding="0"
                     style="border-collapse:collapse;font-size:14px">
                <thead>
                  <tr style="background:#f5f5f5">
                    <th style="padding:8px">商品</th>
                    <th style="padding:8px">目前價格</th>
                    <th style="padding:8px">歷史高價</th>
                    <th style="padding:8px">歷史低價</th>
                    <th style="padding:8px">連結</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding:8px;text-align:center">
                      <img src="{result['image']}" width="72" style="border-radius:6px"><br>
                      <span style="font-size:13px">{item['name']}</span>
                    </td>
                    <td style="padding:8px;text-align:center;color:{badge_color}">
                      <b>NT${new_price}</b><br>
                      <span style="font-size:12px">{tag}</span>
                    </td>
                    <td style="padding:8px;text-align:center">NT${result['high_price']}</td>
                    <td style="padding:8px;text-align:center">NT${result['low_price']}</td>
                    <td style="padding:8px;text-align:center">
                      <a href="{item['url']}">前往</a>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p style="color:#aaa;font-size:12px;margin-top:20px">
                UQ Search · 自動每日通知
              </p>
            </div>
            """
            send_email(
                subject=f"【UQ Watch 降價通知】{item['name']} 現在 NT${new_price}",
                body_html=html
            )
            print(f"✅ 寄出降價通知：{item['name']} NT${saved_price} → NT${new_price}")
        else:
            print(f"⏭ 無降價，略過：{item['name']} NT${new_price}")

    if updated:
        save_watchlist(watchlist)


if __name__ == "__main__":
    main()
