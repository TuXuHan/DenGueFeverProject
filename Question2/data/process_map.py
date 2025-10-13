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

# 載入登革熱預測數據
forecast_data_path = os.path.join(os.path.dirname(__file__), "forecast_data_processed.json")
forecast_data = {}
try:
    with open(forecast_data_path, 'r', encoding='utf-8') as f:
        forecast_data = json.load(f)
    print(f"✓ 已載入預測數據（{forecast_data['summary']['total_districts']} 個區域）")
except Exception as e:
    print(f"⚠️ 無法載入預測數據: {e}")

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
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
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
    
    
        <!-- 左側統一容器 -->
        <div id="left-container" style="position: absolute; left: 0px; top: 0px; width: 320px; height: 100vh; z-index: 1000; display: flex; flex-direction: column;">
            
            <!-- 上方標題和中控區 -->
            <div id="header" style="width: 100%; background: rgba(255, 255, 255, 0.95); padding: 15px 20px; border-radius: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.3); border-left: 4px solid #1f78b4; margin-bottom: 0; position: relative; z-index: 1001;">
                <h2 style="margin: 0 0 8px 0; font-size: 26px; color: #1f78b4; font-weight: bold;">台南市登革熱疫情資料</h2>
                <div id="week-info" style="display: flex; align-items: center; padding: 6px 10px; background: #f0f7ff; border-radius: 4px; border: 1px solid #b3d9ff;">
                    <i class="fas fa-calendar-alt" style="margin-right: 8px; color: #1f78b4; font-size: 14px;"></i>
                    <span style="font-size: 15px; color: #666; font-weight: 600;">預測週次：</span>
                    <span id="current-week" style="margin-left: 5px; font-size: 16px; color: #1f78b4; font-weight: bold;">載入中...</span>
                </div>
            </div>

        <!-- 左側導航欄 -->
        <div id="sidebar" style="width: 100%; background: rgba(255, 255, 255, 0.98); box-shadow: 0 4px 20px rgba(0,0,0,0.15); overflow-y: auto; border-radius: 0 0 12px 12px; border: 1px solid rgba(102, 126, 234, 0.1); border-top: none; flex: 1; margin-top: 0; min-height: 0; position: relative;">
            
            <!-- 固定的標題和面包屑區域 -->
            <div style="position: sticky; top: 0; z-index: 1001; padding: 15px 20px 10px 20px; background: rgba(255, 255, 255, 0.98); border-bottom: 1px solid rgba(102, 126, 234, 0.1); border-radius: 0;">
                <h3 class="sidebar-title" style="margin: 0 0 8px 0; font-size: 20px; color: #1f78b4;">
                    <i class="fas fa-map-marked-alt" style="margin-right: 8px;"></i>
                    <span id="sidebar-main-title">行政區列表</span>
                </h3>
                <div id="breadcrumb-content" style="font-size: 15px; color: #666;">
                    <span id="city-breadcrumb" style="color: #1f78b4; cursor: pointer; font-weight: 600;" onclick="navigateToCity()">台南市</span>
                    <span id="district-breadcrumb" style="display: none; color: #1f78b4; cursor: pointer; font-weight: 600;" onclick="navigateToDistrict()"></span>
                    <span id="village-breadcrumb" style="display: none; color: #666;"></span>
                </div>
            </div>
            
            <!-- 滾動的列表區域 -->
            <div id="district-list" style="font-size: 16px; padding: 10px 20px 20px 20px;">
                <!-- 動態生成區域列表 -->
            </div>
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
// 全局狀態變量
var currentView = 'district'; // 'district' or 'village'
var currentDistrict = null;
var currentVillage = null;

// 初始地圖中心坐標和縮放級別
var initialMapCenter = INITIAL_MAP_CENTER_PLACEHOLDER;
var initialZoomLevel = INITIAL_ZOOM_LEVEL_PLACEHOLDER;

// 面包屑導航函數
function updateBreadcrumb(view, districtName, villageName) {
    var cityBreadcrumb = document.getElementById('city-breadcrumb');
    var districtBreadcrumb = document.getElementById('district-breadcrumb');
    var villageBreadcrumb = document.getElementById('village-breadcrumb');
    
    // 重置所有面包屑
    cityBreadcrumb.style.display = 'inline';
    districtBreadcrumb.style.display = 'none';
    villageBreadcrumb.style.display = 'none';
    
    if (view === 'district') {
        // 只顯示城市級別
        cityBreadcrumb.innerHTML = '台南市';
        cityBreadcrumb.style.color = '#1f78b4';
        cityBreadcrumb.style.cursor = 'default';
    } else if (view === 'village' && districtName) {
        // 顯示城市 > 區域
        cityBreadcrumb.innerHTML = '台南市';
        cityBreadcrumb.style.color = '#1f78b4';
        cityBreadcrumb.style.cursor = 'pointer';
        
        districtBreadcrumb.style.display = 'inline';
        districtBreadcrumb.innerHTML = ' > ' + districtName;
        districtBreadcrumb.style.color = '#1f78b4';
        districtBreadcrumb.style.cursor = 'pointer';
        
        if (villageName) {
            // 顯示城市 > 區域 > 村里
            villageBreadcrumb.style.display = 'inline';
            villageBreadcrumb.innerHTML = ' > ' + villageName;
            villageBreadcrumb.style.color = '#666';
            villageBreadcrumb.style.cursor = 'default';
        }
    }
}

// 高亮指定地圖區域
function highlightMapDistrict(districtName) {
    console.log('嘗試高亮區域:', districtName);
    
    // 首先重置所有地圖區域的樣式
    resetMapDistrictStyles();
    
    var found = false;
    
    // 查找原始GeoJSON圖層
    var originalGeoJsonLayer = null;
    for (var prop in window) {
        if (prop.startsWith('geo_json_') && !prop.includes('_onEachFeature') && !prop.includes('_styler') && window[prop] && typeof window[prop].eachLayer === 'function') {
            originalGeoJsonLayer = window[prop];
            console.log('找到原始圖層:', prop);
            break;
        }
    }
    
    if (!originalGeoJsonLayer) {
        console.log('錯誤：找不到原始GeoJSON圖層');
        return;
    }
    
    var layerCount = 0;
    originalGeoJsonLayer.eachLayer(function(layer) {
        var layerName = layer.feature && layer.feature.properties && layer.feature.properties.name;
        if (layerName === districtName) {
            console.log('找到匹配的區域:', layerName, '索引:', layerCount);
            layer.setStyle({
                color: '#ffc107',
                weight: 3,
                opacity: 1,
                fillColor: '#ffc107',
                fillOpacity: 0.3,
                stroke: true
            });
            found = true;
        }
        layerCount++;
    });
    
    console.log('總共檢查了', layerCount, '個圖層');
    
    if (!found) {
        console.log('警告: 未找到匹配的區域:', districtName);
    }
}

// 重置所有地圖區域樣式
function resetMapDistrictStyles() {
    var originalGeoJsonLayer = null;
    for (var prop in window) {
        if (prop.startsWith('geo_json_') && !prop.includes('_onEachFeature') && !prop.includes('_styler') && window[prop] && typeof window[prop].eachLayer === 'function') {
            originalGeoJsonLayer = window[prop];
            break;
        }
    }
    
    if (originalGeoJsonLayer) {
        originalGeoJsonLayer.setStyle({
            color: '#1f78b4',
            weight: 2,
            opacity: 1,
            fillColor: 'transparent',
            fillOpacity: 0,
            stroke: true
        });
    }
}

// 只顯示行政區詳細資訊，不進入村里視圖
function showDistrictDetailsOnly(districtName) {
    console.log('顯示行政區詳細資訊:', districtName);
    
    // 高亮地圖區域
    highlightMapDistrict(districtName);
    
    // 顯示詳細資料面板
    var infoPanel = document.getElementById('info-panel');
    console.log('找到info-panel元素:', infoPanel);
    
    if (!infoPanel) {
        console.error('找不到info-panel元素！');
        return;
    }
    
    var title = document.getElementById('district-title');
    var population = document.getElementById('population');
    var dengueCases = document.getElementById('dengue-cases');
    var ratePer10k = document.getElementById('rate-per-10k');
    var riskLevel = document.getElementById('risk-level');
    var lastUpdate = document.getElementById('last-update');
    var detailData = document.getElementById('detail-data');
    
    console.log('找到的元素:', {
        title: title,
        population: population,
        dengueCases: dengueCases,
        ratePer10k: ratePer10k,
        riskLevel: riskLevel,
        lastUpdate: lastUpdate
    });
    
    if (title) title.textContent = districtName;
    
    // 查找預測資料
    var forecastData = window.forecastData;
    if (forecastData && forecastData.district_data) {
        var districtData = Object.values(forecastData.district_data).find(d => d.district_name === districtName);
        if (districtData) {
            console.log('找到區域資料:', districtData);
            
            // 顯示人口資料
            var popData = window.populationData && window.populationData[districtName];
            if (population && popData) {
                population.textContent = popData.population.toLocaleString() + ' 人';
            }
            
            if (dengueCases) dengueCases.textContent = districtData.total_pred_cases + ' 病例';
            
            // 計算每萬人病例率
            if (ratePer10k && popData && popData.population > 0) {
                var rate = (districtData.total_pred_cases / popData.population) * 10000;
                ratePer10k.textContent = rate.toFixed(2) + ' /萬人';
            }
            
            if (riskLevel) {
                var riskText = '';
                if (districtData.total_pred_cases >= 1000) riskText = '極高風險';
                else if (districtData.total_pred_cases >= 100) riskText = '高風險';
                else if (districtData.total_pred_cases >= 10) riskText = '中風險';
                else riskText = '低風險';
                riskLevel.textContent = riskText;
            }
            
            if (lastUpdate) lastUpdate.textContent = forecastData.latest_week;
        } else {
            console.log('未找到區域資料:', districtName);
        }
    } else {
        console.log('未找到預測資料或district_data');
    }
    
    // 強制顯示面板
    infoPanel.style.display = 'block';
    console.log('行政區詳細資訊面板已顯示，當前display:', infoPanel.style.display);
}

// 處理地圖上的行政區點擊（展開村里視圖）
function handleMapDistrictClick(districtName) {
    console.log('地圖點擊行政區:', districtName, '（展開村里視圖）');
    
    // 展開村里視圖
    showVillageList(districtName);
    
    // 同時在地圖上顯示該區域的村里邊界
    var mapId = 'MAP_ID_PLACEHOLDER';
    var map = window[mapId];
    if (map) {
        setTimeout(function() {
            showVillagesForDistrict(districtName, map);
        }, 100); // 稍微延遲以確保村里列表已載入
    }
}

// 導航函數
function navigateToCity() {
    if (currentView === 'district') return; // 已經在城市級別
    
    // 清除村里圖層和標籤
    var mapId = 'MAP_ID_PLACEHOLDER';
    var map = window[mapId];
    if (map && villageLayer) {
        map.removeLayer(villageLayer);
        villageLayer = null;
    }
    
    // 清除村里標籤圖層
    if (window.villageLabelsLayer) {
        map.removeLayer(window.villageLabelsLayer);
        window.villageLabelsLayer = null;
    }
    
    // 重置地圖視圖到初始狀態，使用動畫效果
    if (map) {
        map.setView(initialMapCenter, initialZoomLevel, {
            animate: true,
            duration: 0.8
        });
    }
    
    // 返回區域列表
    var districtNames = DISTRICT_NAMES_PLACEHOLDER;
    showDistrictList(districtNames);
    updateBreadcrumb('district');
}

function navigateToDistrict() {
    if (currentView === 'village' && currentDistrict) {
        // 清除村里圖層和標籤
        var mapId = 'MAP_ID_PLACEHOLDER';
        var map = window[mapId];
        if (map && villageLayer) {
            map.removeLayer(villageLayer);
            villageLayer = null;
        }
        
        // 清除村里標籤圖層
        if (window.villageLabelsLayer) {
            map.removeLayer(window.villageLabelsLayer);
            window.villageLabelsLayer = null;
        }
        
        // 重置地圖視圖到初始狀態，使用動畫效果
        if (map) {
            map.setView(initialMapCenter, initialZoomLevel, {
                animate: true,
                duration: 0.8
            });
        }
        
        // 返回區域列表
        var districtNames = DISTRICT_NAMES_PLACEHOLDER;
        showDistrictList(districtNames);
        updateBreadcrumb('district');
    }
}

// 動態生成左側導航列的區域列表
// 確保 DOM 完全加載後再執行
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 已載入，開始生成區域列表...');
    
    // 顯示當前週次
    var weekElement = document.getElementById('current-week');
    if (weekElement && forecastData && forecastData.latest_week) {
        weekElement.textContent = forecastData.latest_week;
    }
    
    // 從 GeoJSON 數據中獲取所有區域名稱（順序與 GeoJSON features 相同）
    var districtNames = DISTRICT_NAMES_PLACEHOLDER;
    
    showDistrictList(districtNames);
});

// 顯示區域列表
function showDistrictList(districtNames) {
    var districtListDiv = document.getElementById('district-list');
    
    if (!districtListDiv) {
        console.error('找不到 district-list 元素！');
        return;
    }
    
    currentView = 'district';
    currentDistrict = null;
    currentVillage = null;
    
    // 更新標題
    document.getElementById('sidebar-main-title').textContent = '行政區列表';
    
    // 更新面包屑
    updateBreadcrumb('district');
    
    // 清空現有內容
    districtListDiv.innerHTML = '';
    
    // 按病例數排序區域（從多到少）
    var sortedDistricts = districtNames.map(function(name) {
        var districtCode = forecastData.district_name_to_code[name];
        var districtData = districtCode ? forecastData.district_data[districtCode] : null;
        var predCases = districtData ? districtData.total_pred_cases : 0;
        return {
            name: name,
            predCases: predCases,
            districtCode: districtCode,
            districtData: districtData
        };
    }).sort(function(a, b) {
        return b.predCases - a.predCases; // 從多到少排序
    });
    
    // 為每個區域創建列表項
    sortedDistricts.forEach(function(district, index) {
        var districtItem = document.createElement('div');
        districtItem.className = 'district-item';
        
        // 根據排名設定樣式（與村里相同的樣式）
        var itemStyle = 'padding: 10px 15px; cursor: pointer; border-bottom: 1px solid #e0e0e0; transition: background-color 0.2s; position: relative;';
        
        if (index < 3) {
            if (index === 0) {
                itemStyle += 'background: linear-gradient(90deg, rgba(128, 0, 128, 0.1) 0%, transparent 100%); border-left: 4px solid purple;';
            } else if (index === 1) {
                itemStyle += 'background: linear-gradient(90deg, rgba(255, 0, 0, 0.1) 0%, transparent 100%); border-left: 4px solid red;';
            } else if (index === 2) {
                itemStyle += 'background: linear-gradient(90deg, rgba(255, 255, 0, 0.2) 0%, transparent 100%); border-left: 4px solid orange;';
            }
        }
        
        districtItem.style.cssText = itemStyle;
        
        // 創建內容 HTML（與村里相同的格式）
        var contentHtml = '';
        if (index < 3) {
            contentHtml += '<span style="font-weight: bold; font-size: 14px;">#' + (index + 1) + '</span> ';
        }
        contentHtml += '<span style="font-weight: 600;">' + district.name + '</span>';
        if (district.predCases > 0) {
            contentHtml += '<br><span style="font-size: 12px; color: #666;">預測病例: ' + district.predCases + '</span>';
        }
        
        districtItem.innerHTML = contentHtml;
        
        // 鼠標懸停效果
        districtItem.addEventListener('mouseenter', function() {
            if (index >= 3) {
                this.style.backgroundColor = '#f0f0f0';
            }
        });
        
        districtItem.addEventListener('mouseleave', function() {
            if (index >= 3) {
                this.style.backgroundColor = 'transparent';
            }
        });
        
        // 點擊事件監聽（只顯示詳細資訊，不進入村里視圖）
        districtItem.addEventListener('click', function() {
            console.log('點擊了側邊欄區域:', district.name, '（只顯示詳細資訊）');
            
            // 只顯示詳細資訊，不進入村里視圖
            showDistrictDetailsOnly(district.name);
        });
        
        districtListDiv.appendChild(districtItem);
    });
    
    console.log('區域列表生成完成，共', districtNames.length, '個區域（已按病例數排序）');
}

// 顯示村里列表
function showVillageList(districtName) {
    var districtListDiv = document.getElementById('district-list');
    
    if (!districtListDiv) {
        console.error('找不到 district-list 元素！');
        return;
    }
    
    currentView = 'village';
    currentDistrict = districtName;
    currentVillage = null;
    
    // 更新面包屑
    updateBreadcrumb('village', districtName);
    
    // 獲取該區域的預測數據
    var districtCode = forecastData.district_name_to_code[districtName];
    var districtData = districtCode ? forecastData.district_data[districtCode] : null;
    
    if (!districtData || !districtData.villages || districtData.villages.length === 0) {
        console.warn('該區域沒有村里數據');
        return;
    }
    
    // 更新標題
    document.getElementById('sidebar-main-title').textContent = districtName + ' 村里列表';
    
    // 清空現有內容
    districtListDiv.innerHTML = '';
    
    // 檢查該區域是否有任何病例數大於0的村里
    var hasNonZeroCases = districtData.villages.some(function(v) {
        return v.pred_cases > 0;
    });
    
    // 顯示村里列表（已按嚴重程度排序）
    districtData.villages.forEach(function(village, index) {
        var villageItem = document.createElement('div');
        villageItem.className = 'village-item';
        
        // 根據排名設定顏色（與行政區相同的樣式）
        // 只有當該區域有非零病例時才顯示前三名顏色
        var itemStyle = 'padding: 10px 15px; cursor: pointer; border-bottom: 1px solid #e0e0e0; transition: background-color 0.2s; position: relative;';
        
        if (hasNonZeroCases && index < 3) {
            if (index === 0) {
                itemStyle += 'background: linear-gradient(90deg, rgba(128, 0, 128, 0.1) 0%, transparent 100%); border-left: 4px solid purple;';
            } else if (index === 1) {
                itemStyle += 'background: linear-gradient(90deg, rgba(255, 0, 0, 0.1) 0%, transparent 100%); border-left: 4px solid red;';
            } else if (index === 2) {
                itemStyle += 'background: linear-gradient(90deg, rgba(255, 255, 0, 0.2) 0%, transparent 100%); border-left: 4px solid orange;';
            }
        }
        
        villageItem.style.cssText = itemStyle;
        
        // 創建內容 HTML（與行政區相同的格式）
        var contentHtml = '';
        if (hasNonZeroCases && index < 3) {
            contentHtml += '<span style="font-weight: bold; font-size: 14px;">#' + (index + 1) + '</span> ';
        }
        contentHtml += '<span style="font-weight: 600;">' + village.village_name + '</span>';
        if (village.pred_cases > 0) {
            contentHtml += '<br><span style="font-size: 12px; color: #666;">預測病例: ' + village.pred_cases + '</span>';
        }
        
        villageItem.innerHTML = contentHtml;
        
        // 鼠標懸停效果
        villageItem.addEventListener('mouseenter', function() {
            if (index >= 3) {
                this.style.backgroundColor = '#f0f0f0';
            }
        });
        
        villageItem.addEventListener('mouseleave', function() {
            if (index >= 3) {
                this.style.backgroundColor = 'transparent';
            }
        });
        
        // 點擊事件（可以添加顯示村里詳情）
        villageItem.addEventListener('click', function() {
            console.log('點擊了村里:', village.village_name, '預測病例:', village.pred_cases);
            currentVillage = village.village_name;
            updateBreadcrumb('village', districtName, village.village_name);
        });
        
        districtListDiv.appendChild(villageItem);
    });
    
    console.log('村里列表生成完成，共', districtData.villages.length, '個村里（已按病例數排序）');
}
</script>

<script>
// 載入村里資料
var villageData = null;
var villageLayer = null;

// 載入村里資料（已包含完整屬性）
fetch('/data/village.geojson')
    .then(response => response.json())
    .then(data => {
        villageData = data;
        console.log('✓ 村里資料載入完成:', villageData.features.length, '個村里');
    })
    .catch(error => {
        console.error('✗ 載入村里資料失敗:', error);
    });

// 顯示指定區域的村里邊界
function showVillagesForDistrict(districtName, map) {
    if (!villageData) {
        console.error('村里資料尚未載入');
        return;
    }
    
    // 清除舊的村里圖層和標籤
    if (villageLayer) {
        map.removeLayer(villageLayer);
        villageLayer = null;
    }
    
    // 清除村里標籤圖層
    if (window.villageLabelsLayer) {
        map.removeLayer(window.villageLabelsLayer);
        window.villageLabelsLayer = null;
    }
    
    // 過濾出該區域的所有村里
    var districtVillages = villageData.features.filter(function(feature) {
        return feature.properties.district_name === districtName;
    });
    
    console.log('找到', districtVillages.length, '個村里在', districtName);
    
    if (districtVillages.length === 0) {
        console.warn('該區域沒有村里資料');
        return;
    }
    
    // 創建村里標籤圖層組
    window.villageLabelsLayer = L.layerGroup();
    
    // 創建村里圖層
    villageLayer = L.geoJSON(districtVillages, {
        style: function(feature) {
            return {
                color: '#1f78b4',
                weight: 2,
                fillColor: '#1f78b4',
                fillOpacity: 0.1,
                opacity: 1
            };
        },
        onEachFeature: function(feature, layer) {
            var props = feature.properties;
            
            // 創建彈出窗口內容
            var popupContent = '<div style="min-width: 220px;">';
            popupContent += '<h4 style="margin: 0 0 10px 0; color: #1f78b4;">' + props.full_name + '</h4>';
            popupContent += '<table style="width: 100%; font-size: 13px;">';
            popupContent += '<tr><td><strong>區域:</strong></td><td>' + props.district_name + '</td></tr>';
            popupContent += '<tr><td><strong>村里:</strong></td><td>' + props.village_name + '</td></tr>';
            popupContent += '<tr><td><strong>預測病例:</strong></td><td><span style="color: #e74c3c; font-weight: bold;">' + (props.pred_cases || 0) + ' 例</span></td></tr>';
            popupContent += '<tr><td><strong>區域人口:</strong></td><td>' + (props.district_population || 0).toLocaleString() + ' 人</td></tr>';
            popupContent += '<tr><td><strong>區域戶數:</strong></td><td>' + (props.district_households || 0).toLocaleString() + ' 戶</td></tr>';
            popupContent += '</table>';
            popupContent += '</div>';
            
            layer.bindPopup(popupContent);
            
            // 添加村里标签（只显示村里名称，不显示区名）
            var center = turf.centroid(feature);
            var label = L.marker([center.geometry.coordinates[1], center.geometry.coordinates[0]], {
                icon: L.divIcon({
                    className: 'village-label',
                    html: '<div style="background: rgba(255, 255, 255, 0.9); border: 1px solid #1f78b4; border-radius: 4px; padding: 2px 6px; font-size: 12px; font-weight: 600; color: #1f78b4; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.3);">' + props.village_name + '</div>',
                    iconSize: [60, 20],
                    iconAnchor: [30, 10]
                })
            });
            window.villageLabelsLayer.addLayer(label);
            
            // 滑鼠懸停效果
            layer.on('mouseover', function(e) {
                this.setStyle({
                    fillOpacity: 0.3,
                    weight: 3,
                    color: '#ff6b6b'
                });
            });
            
            layer.on('mouseout', function(e) {
                this.setStyle({
                    fillOpacity: 0.1,
                    weight: 2,
                    color: '#1f78b4'
                });
            });
            
            // 点击高光效果（只显示详细资讯，不进入其他视图）
            layer.on('click', function(e) {
                // 重置所有村里样式
                villageLayer.eachLayer(function(layer) {
                    layer.setStyle({
                        color: '#1f78b4',
                        weight: 2,
                        fillColor: '#1f78b4',
                        fillOpacity: 0.1,
                        opacity: 1
                    });
                });
                
                // 高光当前选中的村里
                this.setStyle({
                    color: '#ffa500',
                    weight: 3,
                    fillColor: '#ffa500',
                    fillOpacity: 0.4,
                    opacity: 1
                });
                
                // 显示村里详细资讯
                showDistrictInfo(props.village_name, true);
            });
        }
    }).addTo(map);
    
    // 添加標籤圖層到地圖
    window.villageLabelsLayer.addTo(map);
    
    // 自動縮放到村里邊界並居中顯示
    var bounds = villageLayer.getBounds();
    var center = bounds.getCenter();
    
    // 調整中心點，往左偏移一點
    var adjustedCenter = [center.lat, center.lng - 0.005]; // 經度減去0.005度，往左偏移
    
    // 計算適當的縮放級別和中心點
    var zoomLevel = map.getBoundsZoom(bounds, true);
    zoomLevel = Math.min(zoomLevel, 13); // 限制最大縮放級別
    zoomLevel = Math.max(zoomLevel, 10); // 限制最小縮放級別
    
    // 使用 setView 來更精確地控制地圖視圖
    map.setView(adjustedCenter, zoomLevel, {
        animate: true,
        duration: 0.8
    });
    
    console.log('✓ 已顯示', districtName, '的村里邊界，縮放級別:', zoomLevel, '中心點:', center);
}

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
                    
                    // 0.5秒後恢復原樣並顯示村里
                    setTimeout(function() {
                        e.target.setStyle(originalStyle);
                        
                        // 顯示該區域的村里邊界
                        showVillagesForDistrict(districtName, map);
                        
                        // 切換側邊欄到村里列表視圖
                        showVillageList(districtName);
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
forecast_data_json = json.dumps(forecast_data, ensure_ascii=False)

print("組裝最終HTML...")

# 準備初始地圖中心和縮放級別
initial_map_center_json = json.dumps(map_center)  # map_center 已經在前面定義
initial_zoom_level = MAP_CONFIG["zoom_start"]

# 替換HTML中的placeholder
fixed_html = full_html.replace("FOLIUM_SCRIPT_PLACEHOLDER", folium_script)
fixed_html = fixed_html.replace("DISTRICT_NAMES_PLACEHOLDER", district_names_json)
fixed_html = fixed_html.replace("DISTRICT_LABELS_PLACEHOLDER", district_labels_json)
fixed_html = fixed_html.replace("MAP_ID_PLACEHOLDER", actual_map_id)
fixed_html = fixed_html.replace("INITIAL_MAP_CENTER_PLACEHOLDER", initial_map_center_json)
fixed_html = fixed_html.replace("INITIAL_ZOOM_LEVEL_PLACEHOLDER", str(initial_zoom_level))
fixed_html = fixed_html.replace("L.geoJson(null,", f"L.geoJson({geojson_json},")
fixed_html = fixed_html.replace(
    "document.addEventListener('DOMContentLoaded', function() {",
    f"// 人口資料\nvar populationData = {population_data_json};\n\n// 登革熱預測數據\nvar forecastData = {forecast_data_json};\n\ndocument.addEventListener('DOMContentLoaded', function() {{"
)

# 保存完整的HTML文件
with open(str(MAP_HTML), "w", encoding="utf-8") as f:
    f.write(fixed_html)

# 清理臨時文件
try:
    if os.path.exists(str(MAP_TEMP_HTML)):
        os.remove(str(MAP_TEMP_HTML))
        print(f"✓ 已清理臨時文件: {MAP_TEMP_HTML}")
except Exception as e:
    print(f"⚠️ 清理臨時文件失敗: {e}")

print(f"✓ 地圖生成完成！包含 {len(district_names)} 個行政區")
print(f"✓ 輸出文件: {MAP_HTML}")
