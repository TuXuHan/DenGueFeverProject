# 🦟 臺南市登革熱監測系統

一個針對臺南市設計的綜合性登革熱監測與預測系統，具備互動式地圖、機器學習預測和即時資料視覺化功能。

## 📋 專案描述

本專案是一個先進的登革熱監測系統，結合網頁爬蟲、機器學習和互動式地圖技術，為臺南市提供即時登革熱風險評估。系統特色包括：

- **互動式網頁介面**：基於FastAPI的現代化網頁應用程式
- **機器學習預測**：深度學習模型進行登革熱風險預測
- **即時資料更新**：從政府API自動收集資料
- **互動式地圖**：基於Folium的地圖視覺化，包含行政區邊界
- **風險評估**：多層級風險分類（低、中、高風險）
- **資料管理**：完整的資料處理和儲存功能

系統處理誘卵桶資料、氣象資訊和歷史登革熱病例，以預測臺南市各行政區的疫情爆發風險。

## 🚀 如何執行

### 系統需求
- Python 3.8 或更高版本
- Chrome 瀏覽器（用於網頁爬蟲功能）
- 所需依賴套件（請參考 requirements.txt）

### 安裝步驟

1. **複製專案**
   ```bash
   git clone <repository-url>
   cd DengueFeverProject
   ```

2. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定系統**
   - 複製範例設定檔：
     ```bash
     cp config_example.py config.py
     ```
   - 編輯 `config.py` 以符合您的系統需求

4. **執行主應用程式**
   ```bash
   python main.py
   ```

5. **存取網頁介面**
   - 開啟瀏覽器並導航至：`http://localhost:8000`
   - 系統啟動時會自動更新地圖資料

### 其他啟動方式

**舊版 Node.js 系統：**
```bash
cd 臺南市校園登革熱預警系統
node server.js
```

**僅更新資料：**
```bash
python UpdateData.py
```

### 系統元件

- **main.py**：FastAPI 網頁伺服器和主應用程式
- **UpdateData.py**：資料收集和更新腳本
- **臺南市校園登革熱預警系統/**：包含機器學習模型的舊版 Node.js 系統
- **data/**：資料處理和地圖生成腳本

## 🧪 如何測試

### 執行測試

由於目前專案結構中沒有 `test_main.py` 檔案，以下是建議的測試方法：

1. **手動測試**
   ```bash
   # 啟動主應用程式
   python main.py
   
   # 在另一個終端機中測試 API 端點
   curl http://localhost:8000/
   curl http://localhost:8000/api/update-map
   ```

2. **資料驗證測試**
   ```bash
   # 測試資料更新功能
   python test.py
   ```

3. **建立測試檔案**（建議）：
   ```bash
   # 建立簡單的測試檔案
   cat > test_main.py << 'EOF'
   import requests
   import time
   
   def test_main_app():
       """測試主 FastAPI 應用程式"""
       base_url = "http://localhost:8000"
       
       # 測試主頁面
       response = requests.get(base_url)
       assert response.status_code == 200, "主頁面應該可以存取"
       
       # 測試 API 端點
       api_response = requests.get(f"{base_url}/api/update-map")
       assert api_response.status_code == 200, "API 應該成功回應"
       
       print("所有測試通過！")
   
   if __name__ == "__main__":
       test_main_app()
   EOF
   
   # 執行測試
   python test_main.py
   ```

4. **機器學習模型測試**
   ```bash
   cd 臺南市校園登革熱預警系統
   python model_pred.py
   ```

### 測試檢查清單

- [ ] 網頁介面正確載入
- [ ] 地圖正常顯示
- [ ] 資料更新功能正常運作
- [ ] API 端點正確回應
- [ ] 機器學習預測執行成功
- [ ] 檔案上傳功能（如適用）

## 📁 Project Structure

```
DengueFeverProject/
├── main.py                          # FastAPI main application
├── test.py                          # Basic data update test
├── UpdateData.py                    # Data collection script
├── requirements.txt                 # Python dependencies
├── config.py                        # Configuration file
├── data/                           # Data processing
│   ├── process_map.py              # Map generation
│   ├── dengue_data.json            # Dengue case data
│   ├── weather_data.json           # Weather information
│   └── district_boundaries.geojson # Geographic boundaries
├── template/                       # Web templates
│   ├── map.html                    # Main map interface
│   └── map_temp.html               # Template file
├── web/                           # Static web assets
│   └── style.css                  # CSS styles
└── 臺南市校園登革熱預警系統/        # Legacy ML system
    ├── server.js                  # Node.js server
    ├── model_pred.py              # ML prediction script
    ├── model_train_const.py       # Model training
    └── data/                      # ML data and models
```

## 🔧 Configuration

Key configuration options in `config.py`:

- **FASTAPI_CONFIG**: Web server settings (host, port, etc.)
- **MAP_CONFIG**: Map display settings (center coordinates, zoom level)
- **DATA_SOURCES**: API endpoints and data sources
- **ML_MODELS**: Machine learning model paths and settings

## 📊 Data Sources

- **Government APIs**: Tainan City dengue case data
- **Weather Data**: Meteorological information for risk assessment
- **Geographic Data**: District boundaries and administrative regions
- **Mosquito Trap Data**: Ovitrap monitoring results

## 🛠️ Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Mapping**: Folium, Leaflet, GeoJSON
- **Data Processing**: Pandas, NumPy, GeoPandas
- **Machine Learning**: Keras, TensorFlow, scikit-learn
- **Web Scraping**: Selenium, Requests

## 📞 Support

For issues or questions:
1. Check the existing Chinese documentation
2. Review the configuration files
3. Verify all dependencies are installed
4. Check system logs for error messages

## 📄 License

This project is part of an academic research initiative for dengue fever monitoring and prediction in Tainan City, Taiwan.# DenGueFeverProject
