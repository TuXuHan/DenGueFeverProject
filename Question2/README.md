# 🦟 臺南市登革熱監測系統（Question 2）

臺南市登革熱監測系統結合資料管線、互動式地圖與多語介面，協助即時檢視行政區與村里層級的疫情風險與預測結果。本專案為 Question 2 的最新版實作說明。

## 📋 概覽

- **即時資料流程**：訪問首頁時即自動觸發 `prepare_forecast_data.py` 與 `process_map.py`，同步更新預測資料與 Folium 地圖。
- **多語介面**：支援繁體中文與英文顯示，可透過 `?lang=zh`／`?lang=en` 參數或 UI 切換。
- ** 752 村里層級視覺化**：除了 37 個行政區界線，也整合村里層級資料與翻譯字典。
- **FastAPI + Jinja2**：後端使用 FastAPI 與 Jinja2 範本，前端以 Leaflet、Bootstrap 與客製 `script.js` 呈現。
- **可擴充設定**：所有地圖樣式、資料來源與風險閾值皆集中於 `config.py` 管理。

## 🚀 快速開始

### 1. 取得原始碼
```bash
git clone <repository-url>
cd DengueFeverProject/Question2
```

### 2. 建立虛擬環境（建議）
```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows PowerShell
```

### 3. 安裝依賴
- 推薦執行一鍵安裝腳本：
  ```bash
  python install.py
  ```
- 或手動安裝：
  ```bash
  pip install -r requirements.txt
  ```

### 4. 初始化設定
```bash
cp config_example.py config.py
# 依需要編輯 config.py，自訂地圖樣式、資料來源等參數
```

### 5. 啟動服務
- 自動檢查環境並啟動：
  ```bash
  python start_system.py
  ```
- 或直接啟動 FastAPI：
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```
- 也可使用提供的批次／腳本：
  - macOS / Linux：`./start.sh`
  - Windows：雙擊 `start.bat`

瀏覽器開啟 `http://localhost:8000`，即可看到最新資料與互動地圖。

## 🔄 資料流程與腳本

| 階段 | 腳本 | 功能 |
| ---- | ---- | ---- |
| 地理資料轉換（必要時） | `data/convert_village_data.py` | 將村里 Shapefile 轉為 GeoJSON，並做欄位清理。 |
| 預測資料整備 | `data/prepare_forecast_data.py` | 整合 `data/result/` 內的 CSV、人口與天氣資料，輸出 `forecast_data_processed.json`。 |
| 地圖與前端產出 | `data/process_map.py` | 讀取 GeoJSON、預測資料與樣式設定，更新 `template/map.html` 與 `template/script.js`。 |
| 多語字典 | `village_translation.py` | 清理並產生村里名稱翻譯，供地圖切換語系使用。 |

> ✅ `main.py` 在接獲請求時會先呼叫 `prepare_forecast_data.py`（資料更新）再呼叫 `process_map.py`（地圖更新），確保頁面每次載入都是最新成果。

## ⚙️ 設定重點（`config.py`）

- `FASTAPI_CONFIG`：服務名稱、版本、說明與預設主機／埠號。
- `STATIC_MOUNTS`：FastAPI 掛載的靜態路徑，例如 `/data`、`/template`。
- `MAP_CONFIG`、`DISTRICT_STYLE`：地圖中心、縮放層級與行政區樣式。
- `COORDINATE_SYSTEM`：資料投影（預設從 EPSG:3826 轉換到 WGS84）。
- `DATA_SOURCES`、`RISK_THRESHOLDS`：資料更新頻率、外部 API 來源與風險分級閾值。
- `CACHE_CONFIG`、`LOG_CONFIG`：快取與日誌設定，可視需求調整。

詳細字段說明可參考 `CONFIG_README.md`。

## 🗂️ 目錄結構

```
Question2/
├── main.py                 # FastAPI 入口，處理頁面與 API 請求
├── config.py               # 主設定檔（由 config_example.py 拷貝而來）
├── config_example.py
├── install.py              # 一鍵安裝依賴腳本
├── start_system.py         # 啟動器（檢查環境並啟動 uvicorn）
├── start.sh / start.bat    # 平台啟動腳本
├── data/
│   ├── prepare_forecast_data.py
│   ├── process_map.py
│   ├── convert_village_data.py
│   ├── forecast_data_processed.json
│   ├── district_boundaries.geojson
│   ├── village.geojson
│   ├── population.json
│   ├── weather_data.json
│   ├── village_list.csv
│   ├── tainan_town.shp / .shx
│   └── result/
│       ├── forecast_T2_long.csv
│       ├── forecast_T2_wide.csv
│       ├── forecast_T2_long_district.csv
│       ├── forecast_T2_wide_district.csv
│       └── village_ids_tainan.csv
├── template/
│   ├── map.html
│   ├── map_with_language_switch.html
│   └── script.js
├── web/
│   └── style.css
├── village_translation.py
├── requirements.txt
└── QUICK_START.md、INSTALLATION_GUIDE.md 等文件
```

## 🔌 FastAPI 端點

| 方法 | 路徑 | 描述 |
| ---- | ---- | ---- |
| GET | `/` | 產生並回傳最新地圖頁面，支援 `?lang=zh`／`?lang=en`。 |
| GET | `/api/update-map` | 手動觸發資料與地圖更新，可帶 `lang` 參數。 |
| GET | `/api/forecast-data` | 回傳 `forecast_data_processed.json` 的內容與摘要。 |
| GET | `/api/villages` | 提供全部村里 GeoJSON。 |
| GET | `/api/villages/{district_name}` | 以行政區名稱取得該區的所有村里資料。 |

所有成功回應皆包含 `status: "success"`，失敗時會回傳錯誤訊息字串。

## 🧪 開發與測試建議

- 目前尚未納入自動化測試，可使用 `curl` 或 Postman 驗證 API，也可手動檢查地圖載入。
- 若修改資料處理腳本，建議先在 `data/` 目錄單獨執行：
  ```bash
  python data/prepare_forecast_data.py
  python data/process_map.py
  ```
- 地圖渲染依賴 GeoPandas／Folium，若遇到缺少驅動或影像庫，可重新執行 `install.py` 以補齊依賴。

## 🌐 瀏覽介面使用技巧

- 左側側欄列出行政區摘要，點擊可高亮地圖並顯示詳細資訊。
- 右上角語言切換按鈕可即時切換繁體中文／英文標籤。
- 若需直接透過網址切換語言，可於連結後加上 `?lang=en`。

## 🆘 疑難排解

1. **無法啟動**：確認 Python ≥ 3.8、已安裝 requirements、並於專案根目錄執行命令。
2. **地圖沒有更新**：檢查 `data/forecast_data_processed.json` 是否生成，或手動執行資料腳本。
3. **Chrome 相依問題**：部分資料抓取功能仰賴 Chrome，若未安裝會跳出提醒。
4. **語言切換未生效**：清除瀏覽器快取，並確認 `template/script.js` 已被更新。

更多設定、部署、翻譯細節可參考專案內附的 `INSTALLATION_GUIDE.md`、`QUICK_START.md` 與 `MULTILINGUAL_IMPROVEMENTS.md`。

## 📄 授權與致謝

本專案為臺南市登革熱監測與預測研究計畫的一部分。若需使用資料或程式碼於學術／研究用途，請保留來源並遵循專案授權規範。
