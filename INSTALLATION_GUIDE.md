# 登革熱疫情資料系統 - 完整安裝與使用指南

## 📋 目錄
- [系統概述](#系統概述)
- [環境需求](#環境需求)
- [安裝步驟](#安裝步驟)
- [設定檔配置](#設定檔配置)
- [啟動系統](#啟動系統)
- [使用教學](#使用教學)
- [客製化設定](#客製化設定)
- [故障排除](#故障排除)
- [常見問題](#常見問題)

## 🎯 系統概述

這是一個基於 FastAPI 和 Folium 的登革熱疫情資料視覺化系統,提供:
- 📊 互動式地圖顯示
- 📈 疫情資料統計
- 🎨 現代化UI介面
- ⚙️ 完全可客製化的設定

## 💻 環境需求

### 系統需求
- **作業系統**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **記憶體**: 最少 4GB RAM
- **硬碟空間**: 最少 1GB 可用空間

### 必要軟體
- Python 3.8+
- Google Chrome 瀏覽器
- Git (可選,用於版本控制)

## 🚀 安裝步驟

### 步驟 1: 下載專案
```bash
# 方法 1: 使用 Git (推薦)
git clone <repository-url>
cd DengueFeverProject

# 方法 2: 直接下載 ZIP 檔案
# 解壓縮到您想要的位置
```

### 步驟 2: 建立 Python 虛擬環境
```bash
# 建立虛擬環境
python -m venv dengue_env

# 啟動虛擬環境
# Windows:
dengue_env\Scripts\activate
# macOS/Linux:
source dengue_env/bin/activate
```

### 步驟 3: 安裝 Python 依賴套件
```bash
# 安裝基本套件
pip install fastapi uvicorn folium geopandas pandas selenium requests jinja2 python-multipart

# 安裝 WebDriver Manager
# this is a must
pip install webdriver-manager

# 安裝其他可能需要的套件
pip install shapely fiona pyproj
```

### 步驟 4: 下載 Chrome 驅動程式
系統會自動下載,但您也可以手動安裝:
```bash
# 檢查 Chrome 版本
# Windows: 在 Chrome 位址列輸入 chrome://version/
# macOS/Linux: 在終端機執行 google-chrome --version

# 下載對應版本的 ChromeDriver
# https://chromedriver.chromium.org/downloads
```

### 步驟 5: 準備資料檔案
確保以下檔案存在於 `data/` 目錄:
- `tainan_town.shp` - 台南市行政區地圖
- `tainan_town.shx` - 地圖索引檔案
- 其他相關資料檔案

## ⚙️ 設定檔配置

### 步驟 1: 複製範例設定檔
```bash
# 複製範例設定檔
cp config_example.py config.py
```

### 步驟 2: 基本設定
編輯 `config.py` 檔案:

```python
# 基本應用程式設定
APP_NAME = "台南市登革熱疫情資料系統"
APP_VERSION = "1.0.0"

# Web 伺服器設定
FASTAPI_CONFIG = {
    "title": APP_NAME,
    "version": APP_VERSION,
    "host": "0.0.0.0",  # 設為 "127.0.0.1" 僅本機訪問
    "port": 8000,       # 可修改端口
    "reload": True,     # 開發模式
}

# 地圖設定
MAP_CONFIG = {
    "use_dynamic_center": True,  # 使用動態中心點
    "zoom_start": 10.5,         # 初始縮放等級
}
```

### 步驟 3: 驗證設定
```bash
python config.py
```
如果設定正確,會顯示:
```
✅ 設定檔驗證通過
```

## 🎬 啟動系統

### 方法 1: 直接啟動
```bash
# 啟動 Web 伺服器
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 方法 2: 使用腳本啟動
創建 `start.bat` (Windows) 或 `start.sh` (macOS/Linux):

**Windows (start.bat):**
```batch
@echo off
echo 啟動登革熱疫情資料系統...
call dengue_env\Scripts\activate
python main.py
pause
```

**macOS/Linux (start.sh):**
```bash
#!/bin/bash
echo "啟動登革熱疫情資料系統..."
source dengue_env/bin/activate
python main.py
```

### 步驟 4: 開啟瀏覽器
在瀏覽器中開啟:
```
http://localhost:8000
```

## 📖 使用教學

### 主要功能

#### 1. 地圖視圖
- **縮放**: 使用滑鼠滾輪或地圖控制按鈕
- **拖拽**: 按住滑鼠左鍵拖拽地圖
- **點擊行政區**: 查看詳細資訊

#### 2. 側邊欄
- **行政區列表**: 顯示所有行政區及其資料
- **排序**: 點擊欄位標題進行排序
- **搜尋**: 使用瀏覽器搜尋功能 (Ctrl+F)

#### 3. 資訊面板
- **詳細資料**: 點擊行政區後顯示詳細資訊
- **風險等級**: 顯示該區域的風險評估
- **統計資料**: 人口,病例數等統計資訊

### 操作指南

#### 更新資料
```bash
# 手動更新資料
python UpdateData.py

# 或透過 Web 介面
# 訪問 http://localhost:8000/api/update-map
```

#### 重新生成地圖
```bash
# 重新處理地圖
cd data
python process_map.py
```

## 🎨 客製化設定

### 修改地圖外觀

#### 1. 地圖樣式
```python
# 在 config.py 中修改
DISTRICT_STYLE = {
    "default": {
        "color": "#1f78b4",     # 邊框顏色
        "weight": 2,            # 邊框粗細
        "fill_opacity": 0,      # 填充透明度
    },
    "highlighted": {
        "color": "#ff6b6b",     # 高亮顏色
        "weight": 3,
        "fill_opacity": 0.3,
    }
}
```

#### 2. 顏色主題
```python
COLOR_THEME = {
    "primary_color": "#667eea",    # 主要顏色
    "secondary_color": "#764ba2",  # 次要顏色
    "accent_color": "#1f78b4",     # 強調顏色
}
```

#### 3. 版面配置
```python
LAYOUT_CONFIG = {
    "sidebar": {
        "width": "300px",          # 側邊欄寬度
        "background": "rgba(255, 255, 255, 0.98)",
    },
    "info_panel": {
        "width": "300px",          # 資訊面板寬度
    }
}
```

### 為其他城市自訂

#### 1. 修改基本設定
```python
# 應用程式名稱
APP_NAME = "台南市登革熱疫情資料系統"

# 頁面標題
UI_TEXT = {
    "page_title": "台南市登革熱疫情資料",
}
```

#### 2. 更新地圖中心點
```python
MAP_CONFIG = {
    "center": [23.1267, 120.3700],  # 台南市座標
    "use_dynamic_center": True,      # 建議使用動態計算
}
```

#### 3. 修改資料來源
```python
DATA_SOURCES = {
    "tainan_data_url": "https://data.tainan.gov.tw/...",
    "data_titles": ["台南市相關資料"],
}
```

### 風險等級自訂
```python
RISK_THRESHOLDS = {
    "high": 15,      # 高風險閾值
    "medium": 8,     # 中風險閾值
    "low": 3,        # 低風險閾值
    "very_low": 0,   # 極低風險閾值
}
```

## 🔧 故障排除

### 常見錯誤及解決方案

#### 1. 模組導入錯誤
```
ModuleNotFoundError: No module named 'folium'
```
**解決方案:**
```bash
pip install folium
```

#### 2. Chrome 驅動程式錯誤
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```
**解決方案:**
```bash
pip install webdriver-manager
# 或手動下載 ChromeDriver
```

#### 3. 地圖不顯示
**檢查項目:**
- 網路連線是否正常
- 地圖圖磚URL是否可訪問
- 座標系統設定是否正確

#### 4. 資料更新失敗
**檢查項目:**
- 資料來源URL是否有效
- Selenium 設定是否正確
- Chrome 瀏覽器是否已安裝

### 日誌檢查
```bash
# 查看系統日誌
tail -f logs/system.log

# 或檢查 Python 錯誤輸出
python main.py 2>&1 | tee error.log
```

## ❓ 常見問題

### Q1: 如何更改端口號?
A: 在 `config.py` 中修改:
```python
FASTAPI_CONFIG = {
    "port": 8080,  # 改為您想要的端口
}
```

### Q2: 如何讓其他人訪問我的系統?
A: 修改設定:
```python
FASTAPI_CONFIG = {
    "host": "0.0.0.0",  # 允許外部訪問
    "port": 8000,
}
```

### Q3: 如何備份設定檔?
A: 複製 `config.py` 檔案:
```bash
cp config.py config_backup.py
```

### Q4: 如何更新系統?
A: 
```bash
# 更新 Python 套件
pip install --upgrade fastapi uvicorn folium

# 更新專案代碼
git pull origin main
```

### Q5: 如何停用自動更新?
A: 在 `config.py` 中修改:
```python
DATA_SOURCES = {
    "update_interval_hours": 0,  # 設為 0 停用自動更新
}
```

## 📞 技術支援

### 系統資訊
- **版本**: 1.0.0
- **Python**: 3.8+
- **框架**: FastAPI + Folium
- **資料格式**: GeoJSON, Shapefile

### 相關資源
- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [Folium 官方文件](https://python-visualization.github.io/folium/)
- [GeoPandas 官方文件](https://geopandas.org/)

