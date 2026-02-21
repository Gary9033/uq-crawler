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

def add_to_watchlist(model, brand, name, url):
    watchlist = load_watchlist()
    # 同時比對 model + brand
    if any(item["model"] == model and item["brand"] == brand for item in watchlist):
        return False
    watchlist.append({
        "model": model,
        "brand": brand,
        "name": name,
        "url": url
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

    for item in watchlist:
        result = uq_crawl(item["model"])
        is_low = int(result['current_price']) == int(result['low_price'])
        tag = "🔥 歷史低價！" if is_low else ""
        badge_color = "#27ae60" if is_low else "#888"

        rows += f"""
        <tr>
            <td style="padding:16px; border-bottom:1px solid #f0ebe3;">
                <strong>{result['name']}</strong><br>
                <span style="color:#aaa; font-size:0.85rem;">{result['model']}</span>
            </td>
            <td style="padding:16px; border-bottom:1px solid #f0ebe3; color:#c0392b; font-size:1.2rem;">
                NT${result['current_price']}
            </td>
            <td style="padding:16px; border-bottom:1px solid #f0ebe3; color:#888;">
                NT${result['high_price']}
            </td>
            <td style="padding:16px; border-bottom:1px solid #f0ebe3; color:{badge_color};">
                NT${result['low_price']} {tag}
            </td>
            <td style="padding:16px; border-bottom:1px solid #f0ebe3;">
                <a href="{result['url']}" style="color:#2c2c2c; font-size:0.8rem;">前往頁面 →</a>
            </td>
        </tr>
        """

    body_html = f"""
    <div style="font-family:Georgia,serif; background:#f5f0eb; padding:40px 20px;">
        <div style="max-width:700px; margin:0 auto; background:#fff; border:1px solid #e0d6c8;">

            <!-- Header -->
            <div style="background:#2c2c2c; padding:28px 36px;">
                <h1 style="color:#f5f0eb; margin:0; font-size:1.5rem; letter-spacing:0.15em;">
                    UQ PRICE REPORT
                </h1>
                <p style="color:#888; margin:6px 0 0; font-size:0.8rem; letter-spacing:0.2em;">
                    {now}
                </p>
            </div>

            <!-- Table -->
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#f5f0eb;">
                        <th style="padding:12px 16px; text-align:left; font-size:0.7rem; letter-spacing:0.15em; color:#aaa; font-weight:normal;">商品</th>
                        <th style="padding:12px 16px; text-align:left; font-size:0.7rem; letter-spacing:0.15em; color:#aaa; font-weight:normal;">目前價格</th>
                        <th style="padding:12px 16px; text-align:left; font-size:0.7rem; letter-spacing:0.15em; color:#aaa; font-weight:normal;">歷史高價</th>
                        <th style="padding:12px 16px; text-align:left; font-size:0.7rem; letter-spacing:0.15em; color:#aaa; font-weight:normal;">歷史低價</th>
                        <th style="padding:12px 16px; text-align:left; font-size:0.7rem; letter-spacing:0.15em; color:#aaa; font-weight:normal;">連結</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <!-- Footer -->
            <div style="padding:20px 36px; border-top:1px solid #e0d6c8;">
                <p style="color:#aaa; font-size:0.75rem; letter-spacing:0.1em;">
                    UQ Search · 自動每日通知
                </p>
            </div>
        </div>
    </div>
    """

    send_email(f"🛍 UQ 每日價格更新 {now}", body_html)
    print(f"Email 已寄出：{now}")

if __name__ == "__main__":
    main()
