# 🦟 臺南市登革熱監測與預測系統

一個針對臺南市設計的綜合性登革熱監測與預測系統，包含兩個主要模組：基礎地圖展示系統（Question1）和進階預測分析系統（Question2）。

## 📋 專案概述

本專案是一個先進的登革熱監測系統，結合網頁爬蟲、機器學習預測和互動式地圖技術，為臺南市提供即時登革熱風險評估。系統分為兩個主要部分：

### 🗺️ Question1 - 基礎地圖展示系統
- **功能**：誘卵桶位置和統計數據的互動式地圖展示
- **特色**：雙數據源切換、即時loading動畫、響應式設計
- **技術**：FastAPI + Leaflet.js + 自定義UI組件

### 📊 Question2 - 進階預測分析系統  
- **功能**：機器學習預測、風險評估、多層級數據分析
- **特色**：行政區/村里級預測、氣象數據整合、自動資料更新
- **技術**：FastAPI + Folium + Selenium + 機器學習模型

## 🚀 快速開始

### 系統需求
- Python 3.8 或更高版本
- Chrome 瀏覽器（用於Question2的網頁爬蟲功能）
- 網路連接（用於地圖圖磚載入）

### 安裝步驟

1. **複製專案**
   ```bash
   git clone <repository-url>
   cd DengueFeverProject
   ```

2. **安裝依賴套件**
   ```bash
   # 安裝Question1依賴
   cd Question1
   pip install -r requirements.txt
   
   # 安裝Question2依賴
   cd ../Question2
   pip install -r requirements.txt
   ```

## 🗺️ Question1 - 基礎地圖展示系統

### 功能特色
- 🗺️ **互動式地圖展示**：基於Leaflet.js的現代化地圖界面
- 📍 **雙數據源切換**：桶子位置 vs 統計數據
- 🎨 **智能顏色編碼**：根據卵數等級自動分色顯示
- 📱 **響應式設計**：適配各種設備和螢幕尺寸
- 🔄 **Loading動畫**：切換數據時顯示動態載入效果
- 📊 **數據聚合**：統計數據使用聚類顯示，提升性能

### 啟動方式

```bash
cd Question1
python main.py
```

訪問地址：http://127.0.0.1:8000

### 數據源說明
- **桶子位置數據**：3,252個誘卵桶的固定位置（藍色標記）
- **統計數據**：449,292條監測記錄，按卵數分色顯示（綠/黃/橙/紅）

### 主要檔案結構
```
Question1/
├── main.py                    # FastAPI主程式
├── config.py                  # 系統配置
├── data/
│   ├── bucket_converted.json      # 桶子位置數據
│   ├── bucket_stat_converted.json # 統計監測數據
│   └── coordinate_convert.py      # 座標轉換工具
├── template/
│   └── map.html              # 地圖前端頁面
└── requirements.txt          # Python依賴套件
```

## 📊 Question2 - 進階預測分析系統

### 功能特色
- 🤖 **機器學習預測**：基於歷史數據的登革熱病例預測
- 🏘️ **多層級分析**：行政區級別和村里級別預測
- 🌦️ **氣象數據整合**：結合天氣因素進行風險評估
- 📈 **即時資料更新**：自動從政府API收集最新數據
- 🗺️ **進階地圖視覺化**：Folium互動式地圖，包含行政區邊界
- 📋 **完整數據管理**：資料處理、轉換和儲存功能

### 啟動方式

```bash
cd Question2
python main.py
```

訪問地址：http://127.0.0.1:8000

### 數據處理流程

1. **資料準備階段**
   ```bash
   # 轉換村里Shapefile為GeoJSON
   python data/convert_village_data.py
   
   # 處理預測資料，整合村里和行政區數據
   python data/prepare_forecast_data.py
   ```

2. **地圖生成階段**
   ```bash
   # 生成互動式地圖HTML
   python data/process_map.py
   ```

3. **系統啟動階段**
   ```bash
   # 啟動FastAPI服務器（自動更新資料）
   python main.py
   ```

### 主要檔案結構
```
Question2/
├── main.py                           # FastAPI主應用程式
├── UpdateData.py                     # 資料收集腳本
├── config.py                         # 系統配置
├── data/                            # 資料處理
│   ├── process_map.py               # 地圖生成
│   ├── prepare_forecast_data.py     # 預測資料處理
│   ├── convert_village_data.py      # 村里資料轉換
│   ├── dengue_data.json             # 登革熱病例資料
│   ├── weather_data.json            # 氣象資訊
│   ├── population.json              # 人口統計資料
│   ├── district_boundaries.geojson  # 行政區邊界
│   ├── village.geojson              # 村里邊界資料
│   └── result/                      # 預測結果資料
│       ├── forecast_T2_wide.csv     # 村里級預測資料（寬格式）
│       ├── forecast_T2_long.csv     # 村里級預測資料（長格式）
│       ├── forecast_T2_wide_district.csv # 行政區預測資料
│       ├── forecast_T2_long_district.csv # 行政區預測資料
│       └── village_ids_tainan.csv   # 村里ID對照表
├── template/
│   ├── map.html                     # 主地圖介面
│   └── script.js                    # 前端JavaScript
└── web/
    └── style.css                   # CSS樣式
```

## 🔧 系統配置

### Question1 配置
在 `Question1/config.py` 中設定：
- 地圖中心座標和縮放級別
- 數據檔案路徑
- 伺服器設定

### Question2 配置
在 `Question2/config.py` 中設定：
- API端點和資料來源
- 地圖顯示設定
- 爬蟲相關設定

## 🔌 API 端點

### Question1 API
- **GET /**：主頁面，顯示互動式地圖
- **GET /api/locations?data_type=bucket**：獲取桶子位置數據
- **GET /api/locations?data_type=stat**：獲取統計監測數據
- **GET /api/cache-info**：獲取緩存資訊

### Question2 API
- **GET /**：主頁面，顯示預測地圖
- **GET /api/update-map**：手動更新資料和地圖
- **GET /api/forecast-data**：獲取預測資料
- **GET /api/villages**：獲取所有村里資料
- **GET /api/villages/{district_name}**：獲取指定區域的村里資料

## 📊 數據來源與結構

### 數據來源
- **政府API**：臺南市登革熱病例資料
- **誘卵桶監測**：誘卵桶位置和卵數統計
- **氣象資料**：用於風險評估的氣象資訊
- **地理資料**：行政區和村里邊界
- **預測模型**：機器學習預測結果

### 核心數據檔案

#### Question1 數據
- **bucket_converted.json**：桶子位置數據（3,252條記錄）
- **bucket_stat_converted.json**：統計監測數據（449,292條記錄）

#### Question2 數據
- **forecast_T2_wide.csv**：村里級預測資料（寬格式）
- **forecast_T2_long.csv**：村里級預測資料（長格式）
- **district_boundaries.geojson**：37個行政區邊界
- **village.geojson**：752個村里邊界
- **dengue_data.json**：歷史登革熱病例資料
- **weather_data.json**：氣象監測資料

## 🛠️ 技術棧

### 共同技術
- **後端**：FastAPI, Uvicorn
- **前端**：HTML5, CSS3, JavaScript
- **地圖**：Leaflet.js, OpenStreetMap

### Question1 專用
- **UI框架**：Bootstrap 5
- **圖標**：Font Awesome
- **地圖聚類**：Leaflet MarkerCluster

### Question2 專用
- **地圖視覺化**：Folium
- **資料處理**：Pandas, NumPy, GeoPandas
- **網頁爬蟲**：Selenium, Requests
- **機器學習**：Scikit-learn

## 🧪 測試

### Question1 測試
```bash
cd Question1
# 測試API端點
curl http://127.0.0.1:8000/api/locations?data_type=bucket
curl http://127.0.0.1:8000/api/locations?data_type=stat
```

### Question2 測試
```bash
cd Question2
# 測試資料更新功能
python test.py
# 測試API端點
curl http://localhost:8000/api/update-map
```

## 🔍 疑難排解

### 常見問題

#### 地圖無法顯示
- 檢查網路連接
- 確認Leaflet CDN可以訪問
- 檢查瀏覽器控制台錯誤訊息

#### 數據無法載入
- 檢查JSON檔案路徑和格式
- 確認座標資料正確（經度：-180到180，緯度：-90到90）
- 查看終端機錯誤訊息

#### 統計數據載入緩慢
- 這是正常現象，數據量大（44萬+條記錄）
- 系統已實現聚類顯示優化性能
- 載入時會顯示loading動畫

#### Question2爬蟲問題
- 確保Chrome瀏覽器已安裝
- 檢查網路連接
- 確認API端點可訪問

## 📞 技術支援

如有問題或疑問：
1. 查看對應模組的詳細README文件
2. 檢查設定檔和依賴套件
3. 確認所有數據檔案存在且格式正確
4. 檢查系統日誌中的錯誤訊息

## 📄 授權

本專案是臺南市登革熱監測和預測學術研究計畫的一部分。

---

## 🎯 使用建議

### 選擇合適的系統
- **需要簡單的地圖展示**：使用Question1
- **需要預測分析和風險評估**：使用Question2
- **需要完整功能**：兩個系統可以並行使用

### 性能優化
- Question1：統計數據使用聚類顯示，適合大量數據
- Question2：定期更新數據，避免頻繁重新載入

### 數據更新
- Question1：數據相對穩定，可手動更新
- Question2：建議定期執行資料更新腳本
