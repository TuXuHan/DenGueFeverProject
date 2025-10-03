# Shapefile 轉 GeoJSON 轉換工具

這個工具可以將 Shapefile (.shp/.shx) 轉換成能夠給 HTML 讀寫的 GeoJSON 檔案。

## 使用方法

### 基本用法
```bash
# 轉換 .shp 檔案
python process_map.py input.shp output.geojson

# 轉換 .shx 檔案
python process_map.py input.shx output.geojson
```

## 輸出資訊

轉換過程中會顯示：
- 讀取的要素數量
- 欄位資訊
- 前3筆資料的屬性
- 座標系統轉換資訊
- 資料邊界框和中心點
- 輸出檔案大小和驗證結果

## 常見座標系統

- **EPSG:4326** - WGS84 (經緯度，適合網頁地圖)
- **EPSG:3826** - TWD97/TM2 zone 121 (台灣常用)
- **EPSG:3857** - Web Mercator (Google Maps 使用)

## 注意事項

1. 確保輸入檔案存在且可讀取
2. 輸出目錄會自動創建
3. 建議輸出檔案使用 .geojson 副檔名
4. 大型檔案轉換可能需要較長時間

## 如何開啟檔案並測試

由於瀏覽器的安全限制，無法直接開啟本地 HTML 檔案來載入 GeoJSON。請使用以下方法：

### 使用 Python HTTP 伺服器

1. **啟動本地伺服器**：
   ```bash
   python -m http.server 8080
   ```

2. **在瀏覽器中訪問**：
   ```
   http://localhost:8080/test_geojson.html
   ```

3. **測試 GeoJSON 檔案**：
   - 選擇要測試的 GeoJSON 檔案（如 `test_output.geojson` 或 `test_output_wgs84.geojson`）
   - 查看地圖顯示和 GeoJSON 資料結構

## 錯誤處理

如果轉換失敗，工具會顯示詳細的錯誤訊息和堆疊追蹤，幫助您診斷問題。

## 在 HTML 中使用

轉換後的 GeoJSON 檔案可以直接在 HTML 中使用：

```javascript
// 使用 fetch 載入 GeoJSON
fetch('output.geojson')
    .then(response => response.json())
    .then(data => {
        // 處理 GeoJSON 資料
        console.log(data);
    });
```

```html
<!-- 在 Leaflet 地圖中使用 -->
<script>
    fetch('output.geojson')
        .then(response => response.json())
        .then(data => {
            L.geoJSON(data).addTo(map);
        });
</script>
```

