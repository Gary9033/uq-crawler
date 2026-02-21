# uq-crawler (UQ Search 🛍)

UNIQLO / GU 商品價格查詢與監控工具，支援歷史高低價查詢、訂閱通知、每日 Email 報告。

---

## 功能

- 🔍 查詢 UNIQLO / GU 商品目前價格、歷史高低價
- 🖼 顯示商品名稱與圖片
- ➕ 訂閱 / 取消訂閱商品價格通知
- 📧 每日自動寄送 Email 價格報告
- 🔥 自動標記歷史低價商品

---

## 資料夾結構

```
uq-crawler/
├── app.py              # Flask 伺服器 + 路由
├── main.py             # 爬蟲核心邏輯 (uq_crawl)
├── watchlist.py        # 訂閱清單管理、每日 Email 通知
├── watchlist.json      # 訂閱資料（自動產生）
└── templates/
    └── index.html      # 網頁前端
```

---

## 安裝

```bash
pip install flask requests beautifulsoup4 selenium
```

---

## 使用方式

### 啟動網頁

```bash
python app.py
```

打開瀏覽器前往 `http://127.0.0.1:5000`

### 查詢商品

1. 選擇品牌（UNIQLO / GU）
2. 輸入商品型號，例如 `u0000000052200`
3. 點擊 **Search**

### 訂閱商品

查詢後點擊「＋ 訂閱價格通知」，商品會加入 `watchlist.json`。

### 手動執行 Email 通知

```bash
python watchlist.py
```

---

## Email 通知設定

在 `watchlist.py` 填入：

```python
GMAIL_USER     = "你的Gmail@gmail.com"
GMAIL_PASSWORD = "你的16碼應用程式密碼"  # Google 應用程式密碼
NOTIFY_TO      = "收件人@gmail.com"
```

> 取得應用程式密碼：Google 帳號 → 安全性 → 兩步驟驗證 → 應用程式密碼

---

## 設定每日自動通知（Windows）

在 PowerShell 執行：

```powershell
$action = New-ScheduledTaskAction `
    -Execute "D:\otherthing\anaconda3\python.exe" `
    -Argument "D:\otherthing\school\雜物\other\uq-crawler\watchlist.py"

$trigger = New-ScheduledTaskTrigger -Daily -At "09:00"

Register-ScheduledTask `
    -TaskName "UQ每日價格通知" `
    -Action $action `
    -Trigger $trigger `
    -RunLevel Highest
```

---

## 實體商品編號查詢說明(目前不支援)

GU、Uniqlo 商品型號格式（例如 `358337`）和網路編號不同，系統會自動使用 Selenium 搜尋對應的完整型號，需要安裝 ChromeDriver：

```bash
pip install selenium
```

並確認 ChromeDriver 版本與本機 Chrome 版本相符。

---

## watchlist.json 格式

```json
[
  {
    "model": "u0000000052200",
    "brand": "uniqlo",
    "name": "男裝 BLOCKTECH防風雨連帽外套",
    "url": "https://uq.goodjack.tw/hmall-products/u0000000052200"
  }
]
```

---

## 技術架構

| 元件 | 說明 |
|------|------|
| Flask | 網頁伺服器與路由 |
| BeautifulSoup | HTML 解析 |
| Selenium | GU 型號查詢（動態頁面） |
| schema.org JSON-LD | 高低價、商品資訊來源 |
| smtplib | Email 通知 |
| Windows 工作排程器 | 每日自動執行 |

---

## 資料來源

商品資料來自 [uq.goodjack.tw](https://uq.goodjack.tw)，本工具僅供個人學習使用。
