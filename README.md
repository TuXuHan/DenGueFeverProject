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

## 📁 專案結構

```
DengueFeverProject/
├── main.py                          # FastAPI 主應用程式
├── test.py                          # 基本資料更新測試
├── UpdateData.py                    # 資料收集腳本
├── requirements.txt                 # Python 依賴套件
├── config.py                        # 設定檔
├── data/                           # 資料處理
│   ├── process_map.py              # 地圖生成
│   ├── dengue_data.json            # 登革熱病例資料
│   ├── weather_data.json           # 氣象資訊
│   └── district_boundaries.geojson # 地理邊界
├── template/                       # 網頁模板
│   ├── map.html                    # 主地圖介面
│   └── map_temp.html               # 模板檔案
├── web/                           # 靜態網頁資源
│   └── style.css                  # CSS 樣式
└── 臺南市校園登革熱預警系統/        # 舊版機器學習系統
    ├── server.js                  # Node.js 伺服器
    ├── model_pred.py              # 機器學習預測腳本
    ├── model_train_const.py       # 模型訓練
    └── data/                      # 機器學習資料和模型
```

## 🔧 設定

`config.py` 中的主要設定選項：

- **FASTAPI_CONFIG**：網頁伺服器設定（主機、埠號等）
- **MAP_CONFIG**：地圖顯示設定（中心座標、縮放等級）
- **DATA_SOURCES**：API 端點和資料來源
- **ML_MODELS**：機器學習模型路徑和設定

## 📊 資料來源

- **政府 API**：臺南市登革熱病例資料
- **氣象資料**：用於風險評估的氣象資訊
- **地理資料**：行政區邊界和管理區域
- **誘卵桶資料**：誘卵桶監測結果

## 🛠️ 使用技術

- **後端**：FastAPI、Python
- **前端**：HTML5、CSS3、JavaScript、Bootstrap
- **地圖**：Folium、Leaflet、GeoJSON
- **資料處理**：Pandas、NumPy、GeoPandas
- **機器學習**：Keras、TensorFlow、scikit-learn
- **網頁爬蟲**：Selenium、Requests

## 📞 技術支援

如有問題或疑問：
1. 查看現有的中文文件
2. 檢查設定檔
3. 確認所有依賴套件已安裝
4. 檢查系統日誌中的錯誤訊息

## 📄 授權

本專案是臺南市登革熱監測和預測學術研究計畫的一部分。
