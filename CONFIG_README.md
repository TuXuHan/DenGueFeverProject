# 登革熱疫情資料系統 - 設定檔說明

## 概述

本系統現在使用統一的設定檔來管理所有的UI設定,系統參數和配置選項.這使得系統更容易客製化和共享.

## 設定檔結構

### 主要設定檔
- `config.py` - 主要設定檔,包含所有系統參數
- `config_example.py` - 範例設定檔,展示如何自訂各種參數

## 重要設定說明

### 地圖中心點設定

系統現在支援兩種地圖中心點設定方式:

#### 1. 動態計算中心點 (推薦)
```python
MAP_CONFIG = {
    "use_dynamic_center": True,  # 從實際地理資料計算中心點
    "center": [23.126724381730643, 120.37003378640675],  # 備用中心點
}
```

**優點:**
- 自動適應不同的地理資料
- 確保地圖總是正確居中
- 適合不同城市或地區的資料

#### 2. 固定中心點
```python
MAP_CONFIG = {
    "use_dynamic_center": False,  # 使用預設中心點
    "center": [23.126724381730643, 120.37003378640675],  # 固定中心點
}
```

**適用情況:**
- 需要精確控制地圖位置
- 使用已知的城市座標

### 地圖設定

```python
MAP_CONFIG = {
    "center": [緯度, 經度],           # 地圖中心點
    "use_dynamic_center": True,       # 是否使用動態中心點
    "zoom_start": 10.5,              # 初始縮放等級
    "tile_url": "https://...",       # 地圖圖磚URL
    "tile_opacity": 1,               # 圖磚透明度
}
```

### UI 主題設定

```python
COLOR_THEME = {
    "primary_color": "#667eea",      # 主要顏色
    "secondary_color": "#764ba2",    # 次要顏色
    "accent_color": "#1f78b4",       # 強調顏色
    "success_color": "#4ecdc4",      # 成功顏色
    "warning_color": "#ff6b6b",      # 警告顏色
    "danger_color": "#ff4757",       # 危險顏色
}
```

### 版面配置

```python
LAYOUT_CONFIG = {
    "sidebar": {
        "width": "300px",            # 側邊欄寬度
        "position": "absolute",      # 位置類型
        "left": "10px",             # 左邊距
        "top": "80px",              # 頂邊距
    },
    "info_panel": {
        "width": "300px",            # 資訊面板寬度
        "position": "absolute",      # 位置類型
        "right": "10px",            # 右邊距
    }
}
```

### 風險等級設定

```python
RISK_THRESHOLDS = {
    "high": 10,      # 高風險:每萬人10例以上
    "medium": 5,     # 中風險:每萬人5-10例
    "low": 1,        # 低風險:每萬人1-5例
    "very_low": 0,   # 極低風險:每萬人1例以下
}

RISK_COLORS = {
    "high": "#ff4757",      # 高風險顏色
    "medium": "#ffa502",    # 中風險顏色
    "low": "#2ed573",       # 低風險顏色
    "very_low": "#3742fa",  # 極低風險顏色
}
```

## 如何使用

### 1. 基本使用
直接使用預設的 `config.py` 檔案,系統會自動從地理資料計算地圖中心點.

### 2. 自訂設定
1. 複製 `config_example.py` 為 `config.py`
2. 根據需要修改各種參數
3. 重新啟動系統

### 3. 為其他城市自訂

如果您要將此系統用於其他城市,請修改以下設定:

```python
# 1. 修改應用程式名稱
APP_NAME = "台南市登革熱疫情資料系統"

# 2. 修改地圖中心點
MAP_CONFIG = {
    "center": [23.1267, 120.3700],  # 台南市座標
    "use_dynamic_center": True,      # 建議使用動態計算
}

# 3. 修改資料來源
DATA_SOURCES = {
    "tainan_data_url": "https://data.tainan.gov.tw/...",  # 台南市資料URL
    "data_titles": ["台南市相關資料"],
}

# 4. 修改UI文字
UI_TEXT = {
    "page_title": "台南市登革熱疫情資料",
}
```

### 4. 驗證設定

執行以下命令來驗證設定檔:

```bash
python config.py
```

如果設定正確,會顯示:
```
✅ 設定檔驗證通過
```

## 設定檔工具函數

### get_config_value(key_path, default=None)
取得設定值

```python
from config import get_config_value

# 取得地圖縮放等級
zoom_level = get_config_value('MAP_CONFIG.zoom_start', 10.5)

# 取得風險閾值
high_risk_threshold = get_config_value('RISK_THRESHOLDS.high', 10)
```

### update_config(key_path, new_value)
更新設定值

```python
from config import update_config

# 更新地圖中心點
update_config('MAP_CONFIG.center', [22.6273, 120.3014])

# 更新風險閾值
update_config('RISK_THRESHOLDS.high', 15)
```

## 注意事項

1. **地圖中心點**:建議使用 `use_dynamic_center: True` 以確保地圖正確居中
2. **路徑設定**:確保所有檔案路徑正確指向實際檔案位置
3. **權限設定**:確保系統有足夠權限讀寫所需的目錄和檔案
4. **網路設定**:確保可以訪問外部API和地圖服務
5. **瀏覽器設定**:Selenium 需要 Chrome 瀏覽器和對應的驅動程式

## 故障排除

### 常見問題

1. **地圖不顯示**
   - 檢查網路連線
   - 確認地圖圖磚URL正確
   - 檢查座標系統設定

2. **資料更新失敗**
   - 檢查資料來源URL是否有效
   - 確認Selenium設定正確
   - 檢查Chrome瀏覽器安裝

3. **UI樣式異常**
   - 檢查顏色設定是否為有效CSS顏色值
   - 確認版面配置參數正確
   - 檢查字體設定

### 日誌檢查

系統會產生日誌檔案,位置在 `logs/system.log`,可以查看詳細的錯誤資訊.

## 支援

如果您在設定過程中遇到問題,請檢查:
1. Python 版本是否相容
2. 所有依賴套件是否已安裝
3. 設定檔語法是否正確
4. 檔案路徑是否存在

---

*最後更新:2025年1月*
