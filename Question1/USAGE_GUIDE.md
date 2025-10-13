# Question1 地圖展示系統 - 使用指南

## 📋 目錄
1. [快速開始](#快速開始)
2. [系統架構](#系統架構)
3. [資料格式](#資料格式)
4. [API 使用](#api-使用)
5. [自定義配置](#自定義配置)
6. [常見問題](#常見問題)

## 🚀 快速開始

### 步驟 1：安裝依賴

```bash
cd Question1
pip install -r requirements.txt
```

### 步驟 2：啟動系統

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

**或直接使用 Python:**
```bash
python main.py
```

### 步驟 3：訪問系統

在瀏覽器中打開：http://127.0.0.1:8000

## 🏗️ 系統架構

```
Question1/
├── main.py                 # FastAPI 後端伺服器
├── requirements.txt        # Python 依賴套件
├── README.md              # 專案說明
├── USAGE_GUIDE.md         # 使用指南（本檔案）
├── start.sh               # Linux/macOS 啟動腳本
├── start.bat              # Windows 啟動腳本
├── test_api.py            # API 測試腳本
├── data/
│   └── bucket.json        # 位置資料（JSON 格式）
└── template/
    └── map.html           # 前端地圖頁面
```

### 技術棧

**後端:**
- FastAPI - 現代化的 Python Web 框架
- Uvicorn - ASGI 伺服器
- Jinja2 - 模板引擎

**前端:**
- Leaflet.js - 開源地圖庫
- OpenStreetMap - 地圖資料來源
- Bootstrap 5 - UI 框架
- Font Awesome - 圖標庫

## 📊 資料格式

### bucket.json 格式

```json
[
  {
    "id": 1,                          // 唯一識別碼（必填）
    "name": "位置名稱",                // 位置名稱（必填）
    "address": "完整地址",             // 地址（必填）
    "latitude": 22.9971,              // 緯度（必填，-90 到 90）
    "longitude": 120.2127,            // 經度（必填，-180 到 180）
    "type": "類型",                   // 類型（必填）
    "description": "位置描述"          // 描述（必填）
  }
]
```

### 支援的類型

系統預設支援以下類型（可自行擴充）：

| 類型 | 顏色代碼 | 圖標 |
|------|---------|------|
| 交通 | `#4CAF50` (綠色) | 🚆 火車 |
| 景點 | `#2196F3` (藍色) | 🏛️ 地標 |
| 美食 | `#FF9800` (橙色) | 🍴 餐具 |
| 學校 | `#9C27B0` (紫色) | 🎓 畢業帽 |
| 文創 | `#E91E63` (粉紅) | 🎨 調色盤 |

### 添加自定義類型

#### 1. 在 `map.html` CSS 中添加類型顏色：

```css
.type-新類型 { 
    background: #顏色代碼; 
}
```

#### 2. 在 JavaScript 中添加配置：

```javascript
// 顏色配置
function getTypeColor(type) {
    const colors = {
        // ... 現有類型 ...
        '新類型': '#顏色代碼'
    };
    return colors[type] || '#2196F3';
}

// 圖標配置
function getTypeIcon(type) {
    const icons = {
        // ... 現有類型 ...
        '新類型': 'fa-icon-name'  // Font Awesome 圖標類名
    };
    return icons[type] || 'fa-map-marker-alt';
}
```

#### 3. 在圖例中添加：

```html
<div class="legend-item">
    <div class="legend-color" style="background: #顏色代碼;"></div>
    <div class="legend-text">新類型</div>
</div>
```

## 🔌 API 使用

### 1. 取得所有位置

**端點:** `GET /api/locations`

**回應:**
```json
{
  "status": "success",
  "total": 8,
  "data": [
    {
      "id": 1,
      "name": "台南火車站",
      "address": "台南市東區北門路二段4號",
      "latitude": 22.9971,
      "longitude": 120.2127,
      "type": "交通",
      "description": "台南市主要火車站"
    },
    // ... 更多位置
  ]
}
```

**cURL 範例:**
```bash
curl http://127.0.0.1:8000/api/locations
```

**Python 範例:**
```python
import requests

response = requests.get('http://127.0.0.1:8000/api/locations')
data = response.json()
print(f"共有 {data['total']} 個位置")
```

### 2. 取得特定位置

**端點:** `GET /api/locations/{location_id}`

**範例:** `GET /api/locations/1`

**回應:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "台南火車站",
    "address": "台南市東區北門路二段4號",
    "latitude": 22.9971,
    "longitude": 120.2127,
    "type": "交通",
    "description": "台南市主要火車站"
  }
}
```

**cURL 範例:**
```bash
curl http://127.0.0.1:8000/api/locations/1
```

### 3. 根據類型取得位置

**端點:** `GET /api/locations/type/{location_type}`

**範例:** `GET /api/locations/type/景點`

**回應:**
```json
{
  "status": "success",
  "type": "景點",
  "total": 4,
  "data": [
    {
      "id": 2,
      "name": "赤崁樓",
      // ...
    },
    // ... 更多景點
  ]
}
```

**cURL 範例:**
```bash
curl http://127.0.0.1:8000/api/locations/type/景點
```

### API 文檔

啟動伺服器後，可以訪問自動生成的 API 文檔：

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## ⚙️ 自定義配置

### 修改伺服器端口

在 `main.py` 中修改：

```python
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)  # 修改這裡的端口號
```

### 修改地圖中心點和縮放級別

在 `template/map.html` 中修改：

```javascript
var map = L.map('map').setView([緯度, 經度], 縮放級別);
// 例如：
var map = L.map('map').setView([22.9908, 120.2133], 12);
```

縮放級別說明：
- 1-3：世界級視圖
- 4-6：國家級視圖
- 7-10：區域級視圖
- 11-13：城市級視圖
- 14-18：街道級視圖

### 修改地圖圖磚樣式

在 `template/map.html` 中可以更換不同的地圖風格：

```javascript
// OpenStreetMap（預設）
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// 或使用其他風格，例如 CartoDB Positron（淺色）
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CartoDB'
}).addTo(map);

// CartoDB Dark Matter（深色）
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CartoDB'
}).addTo(map);
```

## ❓ 常見問題

### Q1: 如何取得地點的經緯度？

**方法 1：使用 Google Maps**
1. 在 Google Maps 中搜尋地點
2. 右鍵點擊位置
3. 點擊經緯度數字即可複製

**方法 2：使用 OpenStreetMap**
1. 訪問 https://www.openstreetmap.org
2. 搜尋並找到地點
3. 右鍵點擊「顯示地址」

**方法 3：使用 Geocoding API**
```python
import requests

address = "台南市東區北門路二段4號"
url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
response = requests.get(url)
data = response.json()
if data:
    print(f"緯度: {data[0]['lat']}, 經度: {data[0]['lon']}")
```

### Q2: 地圖顯示空白怎麼辦？

**檢查項目：**
1. 確認網路連接正常
2. 檢查瀏覽器控制台是否有錯誤訊息（F12）
3. 確認 bucket.json 中的經緯度格式正確
4. 嘗試清除瀏覽器快取

### Q3: 標記顯示在錯誤位置？

**可能原因：**
1. 經緯度順序錯誤（應該是 latitude, longitude）
2. 經緯度數值超出範圍
   - 緯度：-90 到 90
   - 經度：-180 到 180
3. 座標系統不匹配（確保使用 WGS84）

### Q4: 如何批量添加位置資料？

**範例 Python 腳本：**

```python
import json

# 準備資料
locations = []
for i, (name, addr, lat, lng, type_) in enumerate([
    ("地點1", "地址1", 22.99, 120.21, "景點"),
    ("地點2", "地址2", 23.00, 120.22, "美食"),
    # ... 更多資料
], start=1):
    locations.append({
        "id": i,
        "name": name,
        "address": addr,
        "latitude": lat,
        "longitude": lng,
        "type": type_,
        "description": f"{name}的描述"
    })

# 寫入 JSON
with open('data/bucket.json', 'w', encoding='utf-8') as f:
    json.dump(locations, f, ensure_ascii=False, indent=2)
```

### Q5: 如何整合其他資料來源？

**範例：從 CSV 匯入**

```python
import csv
import json

def csv_to_bucket_json(csv_file, json_file):
    locations = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            locations.append({
                "id": i,
                "name": row['name'],
                "address": row['address'],
                "latitude": float(row['latitude']),
                "longitude": float(row['longitude']),
                "type": row['type'],
                "description": row['description']
            })
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

# 使用範例
csv_to_bucket_json('locations.csv', 'data/bucket.json')
```

### Q6: 如何在生產環境部署？

**使用 Gunicorn（推薦）：**

```bash
# 安裝 Gunicorn
pip install gunicorn

# 啟動（4 個工作進程）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**使用 Docker：**

創建 `Dockerfile`：
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

構建和運行：
```bash
docker build -t question1-map .
docker run -p 8000:8000 question1-map
```

## 📞 技術支援

如有問題或建議，請參考：
1. FastAPI 文檔：https://fastapi.tiangolo.com/
2. Leaflet 文檔：https://leafletjs.com/
3. 專案 README.md

## 📝 更新日誌

### v1.0.0 (初始版本)
- ✅ FastAPI 後端伺服器
- ✅ Leaflet 地圖展示
- ✅ 互動式位置標記
- ✅ 類型分類和顏色編碼
- ✅ 響應式側邊欄
- ✅ 詳細資訊面板
- ✅ RESTful API
- ✅ 跨平台啟動腳本

