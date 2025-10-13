# Question1 地圖展示系統

基於 FastAPI 和 Leaflet 的地圖展示系統，用於顯示 bucket.json 中的位置資料。

## 功能特色

- 🗺️ 互動式地圖展示
- 📍 自定義標記與圖標
- 🎨 類型分色顯示
- 📱 響應式設計
- 🔍 位置詳情面板
- 📋 側邊欄列表導航

## 安裝步驟

### 1. 安裝依賴套件

```bash
cd Question1
pip install -r requirements.txt
```

### 2. 準備資料

確保 `data/bucket.json` 檔案存在，格式如下：

```json
[
  {
    "id": 1,
    "name": "位置名稱",
    "address": "完整地址",
    "latitude": 22.9971,
    "longitude": 120.2127,
    "type": "類型",
    "description": "描述"
  }
]
```

## 啟動系統

### 方法一：使用 Python 直接執行

```bash
python main.py
```

### 方法二：使用 uvicorn 執行

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 訪問系統

啟動後，在瀏覽器中訪問：
- 主頁面：http://127.0.0.1:8000
- API 文檔：http://127.0.0.1:8000/docs

## API 端點

### 取得所有位置

```
GET /api/locations
```

返回：
```json
{
  "status": "success",
  "total": 8,
  "data": [...]
}
```

### 取得特定位置

```
GET /api/locations/{location_id}
```

### 根據類型取得位置

```
GET /api/locations/type/{location_type}
```

## 專案結構

```
Question1/
├── main.py              # FastAPI 主程式
├── requirements.txt     # Python 依賴套件
├── README.md           # 說明文件
├── data/
│   └── bucket.json     # 位置資料
└── template/
    └── map.html        # 地圖前端頁面
```

## 技術棧

- **後端**: FastAPI, Uvicorn
- **前端**: Leaflet.js, Bootstrap 5
- **地圖資料**: OpenStreetMap
- **圖標**: Font Awesome

## 自定義設定

### 修改地圖中心點

在 `template/map.html` 中修改：

```javascript
var map = L.map('map').setView([緯度, 經度], 縮放級別);
```

### 添加新的類型

1. 在 `template/map.html` 的 CSS 中添加類型顏色：
```css
.type-新類型 { background: #顏色代碼; }
```

2. 在 JavaScript 的 `getTypeColor` 和 `getTypeIcon` 函數中添加對應設定。

## 注意事項

- 確保經緯度資料準確
- 地圖需要網路連接載入圖磚
- 建議使用現代瀏覽器（Chrome, Firefox, Edge）

## 疑難排解

### 問題：地圖無法顯示

- 檢查網路連接
- 確認 Leaflet CDN 可以訪問
- 檢查瀏覽器控制台錯誤訊息

### 問題：標記位置不正確

- 確認 bucket.json 中的經緯度格式正確
- 經度範圍：-180 到 180
- 緯度範圍：-90 到 90

### 問題：資料無法載入

- 檢查 bucket.json 檔案路徑
- 確認 JSON 格式正確
- 查看終端機錯誤訊息

