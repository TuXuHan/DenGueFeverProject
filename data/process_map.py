import geopandas as gpd
import folium
import sys
import os
import json
import re

# 添加專案根目錄到路徑，以便導入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TAINAN_TOWN_SHP, MAP_CONFIG, DISTRICT_STYLE, COORDINATE_SYSTEM,
    MAP_TEMP_HTML, MAP_HTML, SCRIPT_JS, TEMPLATE_DIR
)

print("載入地圖數據...")

# 使用包含區域名稱的 GeoJSON 檔案
geojson_path = os.path.join(os.path.dirname(__file__), "district_boundaries.geojson")
gdf = gpd.read_file(geojson_path)

# 設定坐標系統
if gdf.crs is None:
    gdf = gdf.set_crs(COORDINATE_SYSTEM["input_crs"])

if gdf.crs.to_string() != COORDINATE_SYSTEM["output_crs"]:
    gdf = gdf.to_crs(COORDINATE_SYSTEM["output_crs"])

# 計算地圖中心點（使用善化區並調整位置）
zhongxi = gdf[gdf['name'] == '善化區'].iloc[0]
zhongxi_center = zhongxi.geometry.centroid
map_center = [zhongxi_center.y + 0.01, zhongxi_center.x + 0.15]

# 創建基礎地圖
m = folium.Map(
    location=map_center, 
    zoom_start=MAP_CONFIG["zoom_start"],
    zoom_control=MAP_CONFIG["zoom_control"],
    prefer_canvas=MAP_CONFIG["prefer_canvas"]
)

# 定義行政區樣式函數（所有區域預設透明，不填充）
def style_function(feature):
    return {
        'color': DISTRICT_STYLE["default"]["color"],
        'weight': DISTRICT_STYLE["default"]["weight"],
        'fillOpacity': DISTRICT_STYLE["default"]["fill_opacity"],
        'opacity': DISTRICT_STYLE["default"]["opacity"]
    }

# 將 GeoDataFrame 轉換為字典（只轉換一次）
geojson_dict = json.loads(gdf.to_json())
print(f"已載入 {len(geojson_dict.get('features', []))} 個行政區")

# 創建 GeoJSON 圖層
geojson_layer = folium.GeoJson(
    geojson_dict,
    name="行政區",
    style_function=style_function
)

# 添加圖層到地圖
geojson_layer.add_to(m)

print("生成地圖HTML...")

# 保存基礎地圖
m.save(str(MAP_TEMP_HTML))

# 讀取生成的HTML並提取script部分
with open(str(MAP_TEMP_HTML), "r", encoding="utf-8") as f:
    html_content = f.read()

# 提取JavaScript代碼
script_start = html_content.find("<script>")
script_end = html_content.rfind("</script>") + len("</script>")
if script_start != -1 and script_end > script_start:
    script_content = html_content[script_start:script_end]
    folium_script = script_content.replace("<script>", "").replace("</script>", "")
    
    # 清理HTML標籤和CSS代碼
    folium_script = re.sub(r'<style[^>]*>.*?</style>', '', folium_script, flags=re.DOTALL)
    folium_script = re.sub(r'^\s*<(?:style|head|body|div|/style|/head|/body|/div)(?:\s[^>]*)?>\s*$', '', folium_script, flags=re.MULTILINE)
    folium_script = re.sub(r'<div[^>]*>.*?</div>', '', folium_script, flags=re.DOTALL)
    folium_script = re.sub(r'<div[^>]*>', '', folium_script)
    folium_script = re.sub(r'^\s*\.[a-zA-Z][\w-]*\s*\{[^}]*\}\s*$', '', folium_script, flags=re.MULTILINE)
    folium_script = re.sub(r'^\s*\.[a-zA-Z][\w-]*\s*\{[\s\S]*?^\s*\}\s*$', '', folium_script, flags=re.MULTILINE)
    folium_script = re.sub(r'\n\s*\n\s*\n+', '\n\n', folium_script)
    
    # 提取地圖ID
    map_id_match = re.search(r'var\s+(map_[a-f0-9]+)\s*=\s*L\.map', folium_script)
    actual_map_id = map_id_match.group(1) if map_id_match else "map_77ff566063aa1b38b36e2b840672f46d"
else:
    folium_script = "// 無法提取Folium生成的JavaScript"
    actual_map_id = "map_77ff566063aa1b38b36e2b840672f46d"

# 只在 script.js 不存在時才創建新的
if not os.path.exists(SCRIPT_JS):
    with open(str(SCRIPT_JS), "w", encoding="utf-8") as f:
        f.write(folium_script)

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
        
        // 點擊地圖事件監聽
        districtItem.addEventListener('click', function() {
            console.log('點擊了側邊欄區域:', name);
            
        });
        
        districtListDiv.appendChild(districtItem);
    });
    
    console.log('區域列表生成完成，共', districtNames.length, '個區域');
});
</script>

<script>
// 為地圖上的區域添加點擊事件監聽器
(function() {
    console.log('初始化地圖區域點擊事件監聽器...');
    
    // 等待地圖完全載入
    setTimeout(function() {
        var mapId = 'MAP_ID_PLACEHOLDER';
        var map = window[mapId];
        
        if (!map) {
            console.error('找不到地圖對象:', mapId);
            return;
        }
        
        console.log('地圖對象已找到，設置點擊事件監聽器');
        
        // 監聽所有圖層的點擊事件
        map.eachLayer(function(layer) {
            // 檢查是否為 GeoJSON 圖層
            if (layer.feature && layer.feature.properties) {
                layer.on('click', function(e) {
                    var districtName = e.target.feature.properties.name || '未知區域';
                    console.log('========================================');
                    console.log('點擊了地圖區域:', districtName);
                    console.log('點擊位置 (經緯度):', e.latlng);
                    console.log('區域屬性資料:', e.target.feature.properties);
                    console.log('========================================');
                    
                    // 視覺反饋：改變區域顏色
                    var originalStyle = {
                        fillOpacity: e.target.options.fillOpacity,
                        color: e.target.options.color
                    };
                    
                    // 高亮顯示
                    e.target.setStyle({
                        fillOpacity: 0.3,
                        color: '#ff0000',
                        weight: 3
                    });
                    
                    // 0.5秒後恢復原樣
                    setTimeout(function() {
                        e.target.setStyle(originalStyle);
                    }, 500);
                });
                
                // 添加滑鼠懸停效果
                layer.on('mouseover', function(e) {
                    var districtName = e.target.feature.properties.name || '未知區域';
                    console.log('滑鼠懸停於:', districtName);
                    e.target.setStyle({
                        fillOpacity: 0.2,
                        weight: 3
                    });
                });
                
                layer.on('mouseout', function(e) {
                    e.target.setStyle({
                        fillOpacity: 0,
                        weight: 2
                    });
                });
            }
        });
        
        console.log('地圖區域點擊事件監聽器設置完成！');
    }, 1000);  // 延遲 1 秒確保地圖完全初始化
})();
</script>

<script src="/template/script.js"></script>
</body>
</html>
"""

print("準備數據...")

# 從 GeoJSON 中提取所有區域名稱（按順序）
district_names = [feature['properties']['name'] for feature in geojson_dict['features']]
district_names_json = json.dumps(district_names, ensure_ascii=False)

# 讀取人口資料
population_data = {}
try:
    with open(os.path.join(os.path.dirname(__file__), "population.json"), "r", encoding="utf-8") as f:
        population_json = json.load(f)
        for item in population_json['data']:
            if item['區域別'] != '臺南市':
                population_data[item['區域別']] = {
                    'population': int(item['人口數總計']),
                    'households': int(item['戶數']),
                    'villages': int(item['里數現有門牌'])
                }
except Exception as e:
    print(f"警告: 讀取人口資料失敗: {e}")

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
geojson_json = json.dumps(geojson_dict, ensure_ascii=False)

print("組裝最終HTML...")

# 替換HTML中的placeholder
fixed_html = full_html.replace("FOLIUM_SCRIPT_PLACEHOLDER", folium_script)
fixed_html = fixed_html.replace("DISTRICT_NAMES_PLACEHOLDER", district_names_json)
fixed_html = fixed_html.replace("DISTRICT_LABELS_PLACEHOLDER", district_labels_json)
fixed_html = fixed_html.replace("MAP_ID_PLACEHOLDER", actual_map_id)
fixed_html = fixed_html.replace("L.geoJson(null,", f"L.geoJson({geojson_json},")
fixed_html = fixed_html.replace(
    "document.addEventListener('DOMContentLoaded', function() {",
    f"// 人口資料\nvar populationData = {population_data_json};\n\ndocument.addEventListener('DOMContentLoaded', function() {{"
)

# 保存完整的HTML文件
with open(str(MAP_HTML), "w", encoding="utf-8") as f:
    f.write(fixed_html)

print(f"✓ 地圖生成完成！包含 {len(district_names)} 個行政區")
print(f"✓ 輸出文件: {MAP_HTML}")
