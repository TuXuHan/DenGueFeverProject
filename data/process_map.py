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
geojson_path = os.path.join(os.path.dirname(__file__), "district_boundaries.geojson")
gdf = gpd.read_file(geojson_path)

if gdf.crs is None:
    gdf = gdf.set_crs(COORDINATE_SYSTEM["input_crs"])

if gdf.crs.to_string() != COORDINATE_SYSTEM["output_crs"]:
    gdf = gdf.to_crs(COORDINATE_SYSTEM["output_crs"])

# 動態計算地圖中心點
center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]
print(f"計算出的地圖中心點: {center}")

# 使用中西區作為中心點，並往左調整
zhongxi = gdf[gdf['name'] == '善化區'].iloc[0]
zhongxi_center = zhongxi.geometry.centroid
# 經度減0.05（往左），保持緯度不變
map_center = [zhongxi_center.y + 0.01, zhongxi_center.x + 0.15]
print(f"使用中西區中心點並往左調整（經度-0.05）: {map_center}")

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
# 將GeoDataFrame轉換為JSON字符串
geojson_data = gdf.to_json()
print(f"GeoJSON數據長度: {len(geojson_data)} 字符")
print(f"GeoJSON數據前100字符: {geojson_data[:100]}")

# 嘗試使用不同的方法創建GeoJSON圖層
import json
geojson_dict = json.loads(geojson_data)
print(f"GeoJSON字典類型: {type(geojson_dict)}")
print(f"Features數量: {len(geojson_dict.get('features', []))}")

geojson_layer = folium.GeoJson(
    geojson_dict,  # 使用字典而不是字符串
    name="行政區",
    style_function=style_function,
    # 移除 tooltip，因为我们用 JavaScript 添加了固定标签
    # tooltip=folium.GeoJsonTooltip(
    #     fields=fields,
    #     aliases=fields
    # )
)

# 添加圖層到地圖
geojson_layer.add_to(m)

# 為每個區域添加標籤（使用DivIcon創建自定義標籤）
from folium import Marker, DivIcon
import numpy as np

def add_district_labels(map_obj, gdf):
    """為每個行政區添加標籤"""
    print(f"開始為 {len(gdf)} 個區域添加標籤...")
    for idx, row in gdf.iterrows():
        # 使用 representative_point() 而不是 centroid，確保點在多邊形內
        try:
            label_point = row.geometry.representative_point()
        except:
            # 如果失敗則使用 centroid
            label_point = row.geometry.centroid
        
        # 獲取區域名稱
        district_name = row.get('name', f'區域{idx}')
        print(f"處理區域 {idx+1}: {district_name}")
        
        # 創建自定義HTML標籤
        label_html = f'''
        <div class="district-label" data-district-name="{district_name}">
            <span class="label-text">{district_name}</span>
        </div>
        '''
        
        # 創建標籤樣式
        label_css = '''
        .district-label {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #1f78b4;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 12px;
            font-weight: bold;
            color: #1f78b4;
            text-align: center;
            white-space: nowrap;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            pointer-events: none;
            user-select: none;
        }
        .district-label:hover {
            background: rgba(31, 120, 180, 0.1);
        }
        '''
        
        # 創建DivIcon
        div_icon = DivIcon(
            html=label_html,
            icon_size=(100, 18),
            icon_anchor=(40, 10)
        )
        
        # 添加標籤到地圖
        marker = Marker(
            location=[label_point.y, label_point.x],
            icon=div_icon,
            popup=f"<b>{district_name}</b><br>行政區標籤"
        )
        marker.add_to(map_obj)
        print(f"  已添加標籤到地圖: {district_name} at [{label_point.y}, {label_point.x}]")

# 不再使用 Folium 的 Marker 添加標籤，改用 JavaScript 在客戶端添加
# 這樣可以確保標籤順序與 GeoJSON 順序完全一致
print("準備標籤數據（將在 JavaScript 中添加標籤）...")

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

# 提取包含標籤的JavaScript代碼
script_start = html_content.find("<script>")
script_end = html_content.rfind("</script>") + len("</script>")
if script_start != -1 and script_end > script_start:
    script_content = html_content[script_start:script_end]
    # 提取純JavaScript代碼（移除<script>標籤）
    folium_script = script_content.replace("<script>", "").replace("</script>", "")
    
    # 清理錯誤的HTML標籤（Folium有時會在<script>裡面插入HTML標籤）
    import re
    
    # 1. 移除包含樣式定義的<style>...</style>區塊
    folium_script = re.sub(r'<style[^>]*>.*?</style>', '', folium_script, flags=re.DOTALL)
    
    # 2. 移除獨立的HTML標籤（<style>, </head>, <body>, </body>, <div>等）
    folium_script = re.sub(r'^\s*<(?:style|head|body|div|/style|/head|/body|/div)(?:\s[^>]*)?>\s*$', '', folium_script, flags=re.MULTILINE)
    
    # 3. 移除行內的<div>標籤（包含屬性）
    folium_script = re.sub(r'<div[^>]*>.*?</div>', '', folium_script, flags=re.DOTALL)
    folium_script = re.sub(r'<div[^>]*>', '', folium_script)
    
    # 4. 移除裸露的CSS代碼（以.開頭的選擇器）
    # 找出看起來像CSS的區塊（以.classname {開頭，以}結尾）
    folium_script = re.sub(r'^\s*\.[a-zA-Z][\w-]*\s*\{[^}]*\}\s*$', '', folium_script, flags=re.MULTILINE)
    # 移除多行CSS區塊
    folium_script = re.sub(r'^\s*\.[a-zA-Z][\w-]*\s*\{[\s\S]*?^\s*\}\s*$', '', folium_script, flags=re.MULTILINE)
    
    # 5. 移除多餘的空行
    folium_script = re.sub(r'\n\s*\n\s*\n+', '\n\n', folium_script)
    
    # 6. 修正JavaScript縮排（將多餘的縮排統一為4個空格）
    folium_script = re.sub(r'^\s*(L_NO_TOUCH\s*=)', r'    \1', folium_script, flags=re.MULTILINE)
    folium_script = re.sub(r'^\s*(L_DISABLE_3D\s*=)', r'    \1', folium_script, flags=re.MULTILINE)
    folium_script = re.sub(r'^\s*(var\s+map_[a-f0-9]+\s*=)', r'    \1', folium_script, flags=re.MULTILINE)
    
    # 7. 提取Folium生成的map ID
    map_id_match = re.search(r'var\s+(map_[a-f0-9]+)\s*=\s*L\.map', folium_script)
    if map_id_match:
        actual_map_id = map_id_match.group(1)
        print(f"提取到的地圖ID: {actual_map_id}")
    else:
        actual_map_id = "map_77ff566063aa1b38b36e2b840672f46d"
        print("警告: 無法提取地圖ID，使用默認值")
    
    print(f"成功提取並清理JavaScript代碼，長度: {len(folium_script)} 字符")
else:
    folium_script = "// 無法提取Folium生成的JavaScript"
    actual_map_id = "map_77ff566063aa1b38b36e2b840672f46d"
    print("警告: 無法找到JavaScript代碼")

# 檢查是否已存在 script.js，如果存在則保留（不覆蓋）
if not os.path.exists(SCRIPT_JS):
    # 只在 script.js 不存在時才創建新的
    with open(str(SCRIPT_JS), "w", encoding="utf-8") as f:
        script_only = folium_script
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
    <script src="https://cdn.jsdelivr.net/npm/@turf/turf@6.5.0/turf.min.js"></script>
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
                #MAP_ID_PLACEHOLDER {
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
                        
                        /* 區域標籤樣式 */
                        .district-label {
                            background: rgba(255, 255, 255, 0.95) !important;
                            border: 1px solid #1f78b4 !important;
                            border-radius: 4px !important;
                            padding: 2px 6px !important;
                            font-size: 12px !important;
                            font-weight: bold !important;
                            color: #1f78b4 !important;
                            text-align: center !important;
                            white-space: nowrap !important;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
                            pointer-events: none !important;
                            user-select: none !important;
                            font-family: Arial, sans-serif !important;
                        }
                        
                        .district-label:hover {
                            background: rgba(31, 120, 180, 0.1) !important;
                        }
                        
                        /* 標籤容器樣式 */
                        .district-label-container {
                            pointer-events: none !important;
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
            <p><strong>登革熱預測病例:</strong><span id="dengue-cases">-</span></p>
            <p><strong>每萬人病例率:</strong><span id="rate-per-10k">-</span></p>
            <p><strong>風險等級:</strong><span id="risk-level">-</span></p>
            <p><strong>更新時間:</strong><span id="last-update">-</span></p>
            <p id="detail-data" style="margin-top: 10px; border-top: 1px solid #e0e0e0; padding-top: 10px;"></p>
        </div>
    </div>

    <!-- 調整地圖位置，讓出導航欄空間 -->
    <div class="folium-map" id="MAP_ID_PLACEHOLDER" style="position: absolute; top: 0; left: 320px; right: 0; bottom: 0;"></div>

<script>
FOLIUM_SCRIPT_PLACEHOLDER
</script>

<script>
// 添加區域標籤到地圖
(function() {
    // 區域標籤數據（與 GeoJSON features 順序完全一致）
    var districtLabels = DISTRICT_LABELS_PLACEHOLDER;
    
    // 等待地圖載入完成
    setTimeout(function() {
        var mapId = 'MAP_ID_PLACEHOLDER';
        var map = window[mapId];
        
        if (!map) {
            console.error('找不到地圖對象:', mapId);
            return;
        }
        
        console.log('開始添加', districtLabels.length, '個區域標籤...');
        
        // 為每個區域添加標籤
        districtLabels.forEach(function(label, index) {
            var divIcon = L.divIcon({
                html: '<div class="district-label" style="background: rgba(255, 255, 255, 0.9); border: 1px solid #1f78b4; border-radius: 4px; padding: 2px 6px; font-size: 12px; font-weight: bold; color: #1f78b4; text-align: center; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.2); pointer-events: none; user-select: none;">' + label.name + '</div>',
                className: 'custom-div-icon',
                iconSize: [50, 18],
                iconAnchor: [25, 9]
            });
            
            var marker = L.marker([label.lat, label.lon], {
                icon: divIcon,
                zIndexOffset: 1000
            }).addTo(map);
            
            if (index < 5) {
                console.log('添加標籤', index + ':', label.name, 'at [' + label.lat + ', ' + label.lon + ']');
            }
        });
        
        console.log('區域標籤添加完成！');
    }, 500);  // 延遲 500ms 確保地圖完全初始化
})();
</script>

<script>
// 動態生成左側導航列的區域列表
// 確保 DOM 完全加載後再執行
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 已載入，開始生成區域列表...');
    
    // 從 GeoJSON 數據中獲取所有區域名稱（順序與 GeoJSON features 相同）
    var districtNames = DISTRICT_NAMES_PLACEHOLDER;
    
    var districtListDiv = document.getElementById('district-list');
    
    if (!districtListDiv) {
        console.error('找不到 district-list 元素！');
        return;
    }
    
    // 清空現有內容
    districtListDiv.innerHTML = '';
    
    // 為每個區域創建列表項
    districtNames.forEach(function(name, index) {
        var districtItem = document.createElement('div');
        districtItem.className = 'district-item';
        districtItem.textContent = name;
        districtItem.style.padding = '10px 15px';
        districtItem.style.cursor = 'pointer';
        districtItem.style.borderBottom = '1px solid #e0e0e0';
        districtItem.style.transition = 'background-color 0.2s';
        
        // 鼠標懸停效果
        districtItem.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f0f0f0';
        });
        
        districtItem.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
        
        // 點擊事件
        districtItem.addEventListener('click', function() {
            console.log('點擊了區域:', name);
            // 這裡可以添加顯示區域詳情的邏輯
            // 例如：打開資訊面板並顯示該區域的數據
        });
        
        districtListDiv.appendChild(districtItem);
    });
    
    console.log('區域列表生成完成，共', districtNames.length, '個區域');
});
</script>

<script src="/template/script.js"></script>
</body>
</html>
"""

# 修復GeoJSON數據 - 將null替換為實際的GeoJSON數據
print("修復GeoJSON數據...")
geojson_json = json.dumps(geojson_dict, ensure_ascii=False)
print(f"修復後的GeoJSON數據長度: {len(geojson_json)} 字符")

# 從 GeoJSON 中提取所有區域名稱（按順序）
district_names = [feature['properties']['name'] for feature in geojson_dict['features']]
district_names_json = json.dumps(district_names, ensure_ascii=False)
print(f"提取到 {len(district_names)} 個區域名稱")
print(f"區域名稱列表（前5個）: {district_names[:5]}")

# 讀取人口資料
population_data = {}
try:
    with open(os.path.join(os.path.dirname(__file__), "population.json"), "r", encoding="utf-8") as f:
        population_json = json.load(f)
        for item in population_json['data']:
            if item['區域別'] != '臺南市':  # 跳過總計資料
                population_data[item['區域別']] = {
                    'population': int(item['人口數總計']),
                    'households': int(item['戶數']),
                    'villages': int(item['里數現有門牌'])
                }
    print(f"成功讀取 {len(population_data)} 個區域的人口資料")
except Exception as e:
    print(f"讀取人口資料失敗: {e}")
    population_data = {}

population_data_json = json.dumps(population_data, ensure_ascii=False)

# 準備標籤數據（名稱和位置）
district_labels = []
for idx, row in gdf.iterrows():
    try:
        label_point = row.geometry.representative_point()
    except:
        label_point = row.geometry.centroid
    
    district_labels.append({
        'name': row['name'],
        'lat': label_point.y,
        'lon': label_point.x
    })

district_labels_json = json.dumps(district_labels, ensure_ascii=False)
print(f"準備了 {len(district_labels)} 個標籤數據")
print(f"前3個標籤: {district_labels[:3]}")

# 替換HTML中的null為實際GeoJSON數據
fixed_html = full_html.replace("FOLIUM_SCRIPT_PLACEHOLDER", folium_script)
fixed_html = fixed_html.replace("DISTRICT_NAMES_PLACEHOLDER", district_names_json)
fixed_html = fixed_html.replace("DISTRICT_LABELS_PLACEHOLDER", district_labels_json)
# 替換所有的 MAP_ID_PLACEHOLDER (包括 JavaScript 中的)
fixed_html = fixed_html.replace("MAP_ID_PLACEHOLDER", actual_map_id)
fixed_html = fixed_html.replace("L.geoJson(null,", f"L.geoJson({geojson_json},")

# 將人口資料加入到 JavaScript 中
fixed_html = fixed_html.replace(
    "document.addEventListener('DOMContentLoaded', function() {",
    f"// 人口資料\nvar populationData = {population_data_json};\n\ndocument.addEventListener('DOMContentLoaded', function() {{"
)

# 保存完整的HTML文件
with open(str(MAP_HTML), "w", encoding="utf-8") as f:
    f.write(fixed_html)
print("GeoJSON數據修復完成！")

print("地圖HTML和JavaScript已成功生成！")
m
