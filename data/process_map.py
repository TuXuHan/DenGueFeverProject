import geopandas as gpd
import folium
import sys
import os

# 添加專案根目錄到路徑，以便導入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TAINAN_TOWN_SHP, MAP_CONFIG, DISTRICT_STYLE, COORDINATE_SYSTEM,
    MAP_TEMP_HTML, MAP_HTML, SCRIPT_JS, TEMPLATE_DIR
)

# 使用包含區域名稱的 GeoJSON 檔案
geojson_path = "district_boundaries.geojson"
gdf = gpd.read_file(geojson_path)

if gdf.crs is None:
    gdf = gdf.set_crs(COORDINATE_SYSTEM["input_crs"])

if gdf.crs.to_string() != COORDINATE_SYSTEM["output_crs"]:
    gdf = gdf.to_crs(COORDINATE_SYSTEM["output_crs"])

# 動態計算地圖中心點
center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]
print(f"計算出的地圖中心點: {center}")

# 根據設定檔決定使用動態計算的中心點還是預設中心點
if MAP_CONFIG["use_dynamic_center"]:
    map_center = center
    print(f"使用動態計算的中心點: {map_center}")
else:
    map_center = MAP_CONFIG["center"]
    print(f"使用設定檔中的中心點: {map_center}")

m = folium.Map(
    location=map_center, 
    zoom_start=MAP_CONFIG["zoom_start"],
    zoom_control=MAP_CONFIG["zoom_control"],
    prefer_canvas=MAP_CONFIG["prefer_canvas"]
)

fields = [col for col in gdf.columns if col != gdf.geometry.name]

# 調試：打印欄位資訊
print(f"GeoDataFrame 欄位: {list(gdf.columns)}")
print(f"非幾何欄位: {fields}")
if len(gdf) > 0:
    print(f"第一筆資料的屬性: {gdf.iloc[0].to_dict()}")

# 定義行政區樣式函數（所有區域預設透明，不填充）
def style_function(feature):
    return {
        'color': DISTRICT_STYLE["default"]["color"],
        'weight': DISTRICT_STYLE["default"]["weight"],
        'fillOpacity': DISTRICT_STYLE["default"]["fill_opacity"],
        'opacity': DISTRICT_STYLE["default"]["opacity"]
    }

# 確保 GeoDataFrame 有正確的屬性
print("處理前的 GeoDataFrame:")
print(gdf.head(2))
print("Fields:", fields)

# 創建 GeoJSON 圖層
geojson_layer = folium.GeoJson(
    gdf,
    name="行政區",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=fields,
        aliases=fields
    )
)

# 添加圖層到地圖
geojson_layer.add_to(m)

# 調試：檢查生成的 GeoJSON 資料
import json
geojson_data = json.loads(gdf.to_json())
print("GeoJSON 資料範例:")
if geojson_data['features']:
    print("第一個 feature 的 properties:", geojson_data['features'][0]['properties'])
    print("第一個 feature 的 name:", geojson_data['features'][0]['properties'].get('name', 'No name'))

# 保存基礎地圖
m.save(str(MAP_TEMP_HTML))

# 讀取生成的HTML並提取script部分
with open(str(MAP_TEMP_HTML), "r", encoding="utf-8") as f:
    html_content = f.read()

# 檢查是否已存在 script.js，如果存在則保留（不覆蓋）
if not os.path.exists(SCRIPT_JS):
    # 只在 script.js 不存在時才創建新的
    script_start = html_content.find("<script>")
    script_end = html_content.find("</script>") + len("</script>")
    if script_start != -1 and script_end > script_start:
        script_content = html_content[script_start:script_end]
        # 保存script.js（移除<script>標籤）
        with open(str(SCRIPT_JS), "w", encoding="utf-8") as f:
            script_only = script_content.replace("<script>", "").replace("</script>", "")
            # 添加緩存破壞機制到數據加載
            script_only = script_only.replace(
                "return fetch('data/dengue_data.json')",
                "var timestamp = new Date().getTime(); return fetch('data/dengue_data.json?t=' + timestamp, {cache: 'no-store'})"
            )
            f.write(script_only)
else:
    print("script.js 已存在，保留現有版本以維持自定義功能")

# 創建包含側邊欄的完整HTML
full_html = """<!DOCTYPE html>
<html>
<head>
    
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"/>
    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap-glyphicons.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css"/>
    
            <meta name="viewport" content="width=device-width,
                initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
            <style>
                #map_77ff566063aa1b38b36e2b840672f46d {
                    position: relative;
                    width: 100.0%;
                    height: 100.0%;
                    left: 0.0%;
                    top: 0.0%;
                }
                .leaflet-container { font-size: 1rem; }
            </style>

            <style>html, body {
                width: 100%;
                height: 100%;
                margin: 0;
                padding: 0;
            }
            </style>

            <style>#map {
                position:absolute;
                top:0;
                bottom:0;
                right:0;
                left:0;
                }
            </style>

            <script>
                L_NO_TOUCH = false;
                L_DISABLE_3D = false;
            </script>

        
    
                    <style>
                        .foliumtooltip {
                            display: inline-block;
                        }
                       .foliumtooltip table{
                            margin: auto;
                        }
                        .foliumtooltip tr{
                            text-align: left;
                        }
                        .foliumtooltip th{
                            padding: 2px; padding-right: 8px;
                        }
                    </style>

                    <!-- 自定義樣式 -->
                    <style>
                        /* 側邊欄滾動條美化 */
                        #sidebar::-webkit-scrollbar {
                            width: 8px;
                        }
                        #sidebar::-webkit-scrollbar-track {
                            background: #f1f1f1;
                            border-radius: 10px;
                        }
                        #sidebar::-webkit-scrollbar-thumb {
                            background: #888;
                            border-radius: 10px;
                        }
                        #sidebar::-webkit-scrollbar-thumb:hover {
                            background: #555;
                        }

                        /* 導航標題樣式 */
                        .sidebar-title {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white !important;
                            margin: -20px -20px 20px -20px;
                            padding: 20px;
                            border-radius: 8px 8px 0 0;
                            text-align: center;
                            font-weight: bold;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }

                        /* 區域項目樣式增強 */
                        .district-item {
                            position: relative;
                            overflow: hidden;
                        }
                        .district-item::before {
                            content: '';
                            position: absolute;
                            left: 0;
                            top: 0;
                            height: 100%;
                            width: 4px;
                            transition: width 0.3s ease;
                        }
                        .district-item:hover::before {
                            width: 100%;
                            opacity: 0.1;
                        }

                        /* 區域名稱樣式 */
                        .district-name {
                            font-weight: 600;
                            color: #333;
                        }

                        /* 區域數值樣式 */
                        .district-value {
                            font-weight: bold;
                            padding: 2px 10px;
                            border-radius: 12px;
                            background: rgba(0,0,0,0.05);
                            font-size: 13px;
                        }

                        /* 排名徽章 */
                        .rank-badge {
                            position: absolute;
                            left: -5px;
                            top: 50%;
                            transform: translateY(-50%);
                            width: 24px;
                            height: 24px;
                            border-radius: 50%;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 11px;
                            font-weight: bold;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        }

                        /* 標題頭部美化 */
                        #header {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                            border: none !important;
                        }
                        #header h2 {
                            color: white !important;
                            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }

                        /* 資訊面板美化 */
                        #info-panel {
                            backdrop-filter: blur(10px);
                            border: 1px solid rgba(255,255,255,0.3);
                        }
                        #info-panel p {
                            margin: 8px 0;
                            padding: 8px;
                            background: #f8f9fa;
                            border-radius: 6px;
                            transition: all 0.2s ease;
                        }
                        #info-panel p:hover {
                            background: #e9ecef;
                            transform: translateX(2px);
                        }
                        #info-panel strong {
                            color: #667eea;
                            font-weight: 600;
                        }
                    </style>
            
</head>
<body>
    
    
    <!-- 上方標題和中控區 -->
    <div id="header" style="position: absolute; top: 10px; left: 10px; z-index: 1000; background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
        <h2 style="margin: 0; font-size: 24px; color: #1f78b4; font-weight: bold;">台南市登革熱疫情資料</h2>
    </div>

    <!-- 左側導航欄 -->
    <div id="sidebar" style="position: absolute; left: 10px; top: 80px; bottom: 10px; width: 300px; background: rgba(255, 255, 255, 0.98); padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); overflow-y: auto; border-radius: 12px; z-index: 1000; border: 1px solid rgba(102, 126, 234, 0.1);">
        <h3 class="sidebar-title" style="font-size: 20px;">
            <i class="fas fa-map-marked-alt" style="margin-right: 8px;"></i>
            行政區列表
        </h3>
        
        <div id="district-list" style="font-size: 14px;">
            <!-- 動態生成區域列表 -->
        </div>
    </div>

    <!-- 詳細資料顯示區域 -->
    <div id="info-panel" style="position: absolute; top: 10px; right: 10px; width: 300px; background: rgba(255, 255, 255, 0.95); padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); border-radius: 8px; z-index: 1000; display: none;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 id="district-title" style="margin: 0; color: #1f78b4;"></h4>
            <button id="close-panel" style="background: none; border: none; font-size: 20px; color: #999; cursor: pointer; padding: 0; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; border-radius: 50%; transition: all 0.2s ease;" onmouseover="this.style.backgroundColor='#f0f0f0'; this.style.color='#666';" onmouseout="this.style.backgroundColor='transparent'; this.style.color='#999';">&times;</button>
        </div>
        <div id="district-info" style="font-size: 14px;">
            <p><strong>人口數據:</strong><span id="population">-</span></p>
            <p><strong>登革熱病例:</strong><span id="dengue-cases">-</span></p>
            <p><strong>每萬人病例率:</strong><span id="rate-per-10k">-</span></p>
            <p><strong>風險等級:</strong><span id="risk-level">-</span></p>
            <p><strong>更新時間:</strong><span id="last-update">-</span></p>
            <p id="detail-data" style="margin-top: 10px; border-top: 1px solid #e0e0e0; padding-top: 10px;"></p>
        </div>
    </div>

    <!-- 調整地圖位置，讓出導航欄空間 -->
    <div class="folium-map" id="map_77ff566063aa1b38b36e2b840672f46d" style="position: absolute; top: 0; left: 320px; right: 0; bottom: 0;"></div>
        
</body>
<script src="/template/script.js"></script>
</html>
"""

# 保存完整的HTML文件
with open(str(MAP_HTML), "w", encoding="utf-8") as f:
    f.write(full_html)

print("地圖HTML和JavaScript已成功生成！")
m
