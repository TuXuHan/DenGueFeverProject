# 🚀 快速開始指南

## 5分鐘快速啟動

### 1. 安裝依賴
```bash
pip install fastapi uvicorn folium geopandas pandas selenium requests jinja2 webdriver-manager
```

### 2. 複製設定檔
```bash
cp config_example.py config.py
```

### 3. 啟動系統
```bash
python main.py
```

### 4. 開啟瀏覽器
訪問:http://localhost:8000

## 🎯 基本使用

1. **查看地圖** - 系統會自動顯示台南市行政區地圖
2. **點擊行政區** - 查看詳細疫情資料
3. **使用側邊欄** - 瀏覽所有行政區列表
4. **更新資料** - 點擊更新按鈕或訪問 `/api/update-map`

## ⚙️ 快速客製化

### 更改城市
編輯 `config.py`:
```python
APP_NAME = "您的城市登革熱疫情資料系統"
UI_TEXT = {
    "page_title": "您的城市登革熱疫情資料",
}
```

### 更改顏色主題
```python
COLOR_THEME = {
    "primary_color": "#您的顏色",
    "accent_color": "#您的強調色",
}
```

### 更改風險閾值
```python
RISK_THRESHOLDS = {
    "high": 10,    # 高風險閾值
    "medium": 5,   # 中風險閾值
    "low": 1,      # 低風險閾值
}
```

## 🔧 常見問題

**Q: 地圖不顯示?**
A: 檢查網路連線和瀏覽器控制台

**Q: 資料更新失敗?**
A: 確認 Chrome 瀏覽器已安裝

**Q: 如何更改端口?**
A: 修改 `config.py` 中的 `FASTAPI_CONFIG["port"]`

## 📚 詳細教學

查看 `INSTALLATION_GUIDE.md` 獲取完整安裝和使用說明.

---
*需要幫助?請查看完整文件或檢查系統日誌*
