import geopandas as gpd
import folium
import sys
import os
import json
import re

# 添加專案根目錄到路徑，以便導入 config
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 導入村里翻譯字典
from village_translation import clean_translations
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
<html lang="zh-TW">
<head>
    
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title data-zh="Question2 地圖展示系統" data-en="Question2 Map Display System">Question2 地圖展示系統</title>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@turf/turf@6.5.0/turf.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js"></script>
    <script src="/template/script.js"></script>
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
            
            <script>
            // 初始化語言變量
            var urlParams = new URLSearchParams(window.location.search);
            var currentLanguage = urlParams.get('lang') || 'zh';
            window.currentLanguage = currentLanguage;
            
            // 設置語言切換按鈕的初始狀態
            document.addEventListener('DOMContentLoaded', function() {
                var urlParams = new URLSearchParams(window.location.search);
                var currentLang = urlParams.get('lang') || 'zh';
                
                // 設置按鈕狀態
                document.querySelectorAll('.lang-option').forEach(option => {
                    option.classList.remove('active');
                });
                document.querySelector(`[data-lang="${currentLang}"]`).classList.add('active');
            });
            
            // 全局語言切換函數
            window.switchLanguage = function(lang) {
                console.log('切換語言至:', lang);
                
                // 更新全局語言變量
                if (typeof currentLanguage !== 'undefined') {
                    currentLanguage = lang;
                } else {
                    window.currentLanguage = lang;
                }
                
                // 更新語言切換按鈕狀態
                document.querySelectorAll('.lang-option').forEach(option => {
                    option.classList.remove('active');
                });
                document.querySelector(`[data-lang="${lang}"]`).classList.add('active');
                
                // 重新生成整個頁面，帶語言參數
                window.location.href = '/?lang=' + lang;
                
                console.log('語言切換完成，頁面重新載入:', lang);
            };
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
                        
                        /* 語言切換開關 */
                        .language-switch {
                            position: absolute;
                            top: 15px;
                            right: 15px;
                            z-index: 1000;
                            background: rgba(255, 255, 255, 0.95);
                            padding: 10px 15px;
                            border-radius: 25px;
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                            border: 1px solid rgba(0, 0, 0, 0.1);
                            display: flex;
                            align-items: center;
                            gap: 10px;
                            font-size: 14px;
                            font-weight: 500;
                        }
                        
                        .language-switch .lang-option {
                            padding: 5px 10px;
                            border-radius: 15px;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            color: #666;
                        }
                        
                        .language-switch .lang-option.active {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                        }
                        
                        .language-switch .lang-option:hover:not(.active) {
                            background: rgba(102, 126, 234, 0.1);
                            color: #667eea;
                        }
                    </style>
            
</head>
<body>
    
    <!-- 語言切換開關 -->
    <div class="language-switch">
        <div class="lang-option" data-lang="zh" onclick="switchLanguage('zh')">
            <i class="fas fa-globe-asia"></i> 中文
        </div>
        <div class="lang-option" data-lang="en" onclick="switchLanguage('en')">
            <i class="fas fa-globe-americas"></i> English
        </div>
    </div>
    
        <!-- 左側統一容器 -->
        <div id="left-container" style="position: absolute; left: 0px; top: 0px; width: 320px; height: 100vh; z-index: 1000; display: flex; flex-direction: column;">
            
            <!-- 上方標題和中控區 -->
            <div id="header" style="width: 100%; background: rgba(255, 255, 255, 0.95); padding: 15px 20px; border-radius: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.3); border-left: 4px solid #1f78b4; margin-bottom: 0; position: relative; z-index: 1001;">
                <h2 style="margin: 0 0 8px 0; font-size: 26px; color: #1f78b4; font-weight: bold;" class="translatable" data-zh="台南市登革熱疫情資料" data-en="Tainan City Dengue Fever Epidemic Data">TITLE_PLACEHOLDER</h2>
                <div id="week-info" style="display: flex; align-items: center; padding: 6px 10px; background: #f0f7ff; border-radius: 4px; border: 1px solid #b3d9ff;">
                    <i class="fas fa-calendar-alt" style="margin-right: 8px; color: #1f78b4; font-size: 14px;"></i>
                    <span style="font-size: 15px; color: #666; font-weight: 600;" class="translatable" data-zh="預測週次：" data-en="Prediction Week:">PREDICTION_WEEK_PLACEHOLDER</span>
                    <span id="current-week" style="margin-left: 5px; font-size: 16px; color: #1f78b4; font-weight: bold;" class="translatable" data-zh="載入中..." data-en="Loading...">LOADING_PLACEHOLDER</span>
                </div>
            </div>

        <!-- 左側導航欄 -->
        <div id="sidebar" style="width: 100%; background: rgba(255, 255, 255, 0.98); box-shadow: 0 4px 20px rgba(0,0,0,0.15); overflow-y: auto; border-radius: 0 0 12px 12px; border: 1px solid rgba(102, 126, 234, 0.1); border-top: none; flex: 1; margin-top: 0; min-height: 0; position: relative;">
            
            <!-- 固定的標題和面包屑區域 -->
            <div style="position: sticky; top: 0; z-index: 1001; padding: 15px 20px 10px 20px; background: rgba(255, 255, 255, 0.98); border-bottom: 1px solid rgba(102, 126, 234, 0.1); border-radius: 0;">
                <h3 class="sidebar-title" style="margin: 0 0 8px 0; font-size: 20px; color: #1f78b4;">
                    <i class="fas fa-map-marked-alt" style="margin-right: 8px;"></i>
                    <span id="sidebar-main-title" class="translatable" data-zh="行政區列表" data-en="District List">DISTRICT_LIST_PLACEHOLDER</span>
                </h3>
                <div id="breadcrumb-content" style="font-size: 15px; color: #666;">
                    <span id="city-breadcrumb" style="color: #1f78b4; cursor: pointer; font-weight: 600;" onclick="navigateToCity()" class="translatable" data-zh="台南市" data-en="Tainan City">TAINAN_CITY_PLACEHOLDER</span>
                    <span id="district-breadcrumb" style="display: none; color: #1f78b4; cursor: pointer; font-weight: 600;" onclick="navigateToDistrict()"></span>
                    <span id="village-breadcrumb" style="display: none; color: #666;"></span>
                </div>
            </div>
            
            <!-- 滾動的列表區域 -->
            <div id="district-list" style="font-size: 16px; padding: 10px 20px 20px 20px;" aria-label="行政區列表" data-zh="行政區列表" data-en="District List">
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
            <p><strong class="translatable" data-zh="人口數據:" data-en="Population Data:">POPULATION_DATA_PLACEHOLDER</strong><span id="population">-</span></p>
            <p><strong class="translatable" data-zh="登革熱預測病例:" data-en="Dengue Predicted Cases:">DENGUE_CASES_PLACEHOLDER</strong><span id="dengue-cases">-</span></p>
            <p><strong class="translatable" data-zh="每萬人病例率:" data-en="Cases per 10k People:">RATE_PER_10K_PLACEHOLDER</strong><span id="rate-per-10k">-</span></p>
            <p><strong class="translatable" data-zh="風險等級:" data-en="Risk Level:">RISK_LEVEL_PLACEHOLDER</strong><span id="risk-level">-</span></p>
            <p><strong class="translatable" data-zh="更新時間:" data-en="Last Update:">LAST_UPDATE_PLACEHOLDER</strong><span id="last-update">-</span></p>
            <p id="detail-data" style="margin-top: 10px; border-top: 1px solid #e0e0e0; padding-top: 10px;"></p>
        </div>
    </div>

    <!-- 調整地圖位置，讓出導航欄空間 -->
    <div class="folium-map" id="MAP_ID_PLACEHOLDER" style="position: absolute; top: 0; left: 320px; right: 0; bottom: 0;"></div>

<script>
FOLIUM_SCRIPT_PLACEHOLDER
</script>

<script>
// 添加區域標籤到地圖的函數
function addDistrictLabels() {
    // 區域標籤數據（與 GeoJSON features 順序完全一致）
    var districtLabels = DISTRICT_LABELS_PLACEHOLDER;
    window.districtLabels = districtLabels; // 設為全局變量
    
    // 等待地圖載入完成
    setTimeout(function() {
        var mapId = 'MAP_ID_PLACEHOLDER';
        var map = window[mapId];
        
        if (!map) {
            console.error('找不到地圖對象:', mapId);
            return;
        }
        
        console.log('開始添加', districtLabels.length, '個區域標籤...');
        console.log('當前語言:', window.currentLanguage);
        console.log('翻譯字典:', window.districtTranslations);
        
        // 為每個區域添加標籤
        districtLabels.forEach(function(label, index) {
            // 重新獲取語言設置
            var urlParams = new URLSearchParams(window.location.search);
            var currentLanguage = urlParams.get('lang') || 'zh';
            window.currentLanguage = currentLanguage;
            
            var displayName = label.name;
            if (currentLanguage === 'zh') {
                displayName = label.name + '區';
            } else {
                // 使用翻譯後的區域名稱 - 使用 full_name 作為鍵值
                var fullDistrictName = label.full_name || (label.name + '區');
                var translatedName = window.districtTranslations && window.districtTranslations[fullDistrictName] ? window.districtTranslations[fullDistrictName] : fullDistrictName;
                displayName = translatedName;
                console.log('翻譯', fullDistrictName, '->', translatedName);
            }
            
            // 根據語言調整標籤樣式
            var labelStyle, iconSize, iconAnchor;
            if (currentLanguage === 'zh') {
                // 中文版本：較小標籤
                labelStyle = 'background: rgba(255, 255, 255, 0.9); border: 1px solid #1f78b4; border-radius: 4px; padding: 2px 6px; font-size: 12px; font-weight: bold; color: #1f78b4; text-align: center; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.2); pointer-events: none; user-select: none;';
                iconSize = [50, 18];
                iconAnchor = [25, 9];
            } else {
                // 英文版本：較大標籤，支持更長的英文名稱
                labelStyle = 'background: rgba(255, 255, 255, 0.95); border: 1px solid #2c5aa0; border-radius: 6px; padding: 3px 8px; font-size: 11px; font-weight: 600; color: #2c5aa0; text-align: center; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3); pointer-events: none; user-select: none; min-width: 60px;';
                iconSize = [70, 18];
                iconAnchor = [35, 9];
            }
            
            var divIcon = L.divIcon({
                html: '<div class="district-label" style="' + labelStyle + '" title="' + (label.full_name || label.name) + '" aria-label="' + (currentLanguage === 'zh' ? '地圖標記圖標' : 'Map Marker Icon') + '" data-zh="地圖標記圖標" data-en="Map Marker Icon">' + displayName + '</div>',
                className: 'custom-div-icon leaflet-marker-icon leaflet-zoom-animated leaflet-interactive',
                iconSize: iconSize,
                iconAnchor: iconAnchor
            });
            
            var marker = L.marker([label.lat, label.lon], {
                icon: divIcon,
                zIndexOffset: 1000
            }).addTo(map);
            
            if (index < 5) {
                console.log('添加標籤', index + ':', label.name, '->', displayName, 'at [' + label.lat + ', ' + label.lon + ']');
            }
        });
        
        console.log('區域標籤添加完成！');
    }, 500);  // 延遲 500ms 確保地圖完全初始化
}

// 在 DOM 載入完成後調用
document.addEventListener('DOMContentLoaded', function() {
    addDistrictLabels();
});

// 重新生成地圖標籤的函數（用於語言切換）
function regenerateMapLabels() {
    console.log('重新生成地圖標籤...');
    
    // 清除現有的標籤
    var mapId = 'MAP_ID_PLACEHOLDER';
    var map = window[mapId];
    
    if (!map) {
        console.error('找不到地圖對象:', mapId);
        return;
    }
    
    // 清除所有現有的標籤
    map.eachLayer(function(layer) {
        if (layer.options && layer.options.icon && layer.options.icon.options && layer.options.icon.options.className === 'custom-div-icon') {
            map.removeLayer(layer);
        }
    });
    
    // 重新添加標籤
    var districtLabels = window.districtLabels || DISTRICT_LABELS_PLACEHOLDER;
    districtLabels.forEach(function(label, index) {
        // 重新獲取語言設置
        var urlParams = new URLSearchParams(window.location.search);
        var currentLanguage = urlParams.get('lang') || 'zh';
        window.currentLanguage = currentLanguage;
        
        var displayName = label.name;
        if (currentLanguage === 'zh') {
            displayName = label.name + '區';
        } else {
            // 使用翻譯後的區域名稱 - 使用 full_name 作為鍵值
            var fullDistrictName = label.full_name || (label.name + '區');
            var translatedName = window.districtTranslations && window.districtTranslations[fullDistrictName] ? window.districtTranslations[fullDistrictName] : fullDistrictName;
            displayName = translatedName;
        }
        
        // 根據語言調整標籤樣式
        var labelStyle, iconSize, iconAnchor;
        if (currentLanguage === 'zh') {
            // 中文版本：較小標籤
            labelStyle = 'background: rgba(255, 255, 255, 0.9); border: 1px solid #1f78b4; border-radius: 4px; padding: 2px 6px; font-size: 12px; font-weight: bold; color: #1f78b4; text-align: center; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.2); pointer-events: none; user-select: none;';
            iconSize = [50, 18];
            iconAnchor = [25, 9];
        } else {
            // 英文版本：較大標籤，支持更長的英文名稱
            labelStyle = 'background: rgba(255, 255, 255, 0.95); border: 1px solid #2c5aa0; border-radius: 6px; padding: 3px 8px; font-size: 11px; font-weight: 600; color: #2c5aa0; text-align: center; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3); pointer-events: none; user-select: none; min-width: 60px;';
            iconSize = [70, 18];
            iconAnchor = [35, 9];
        }
        
        var divIcon = L.divIcon({
            html: '<div class="district-label" style="' + labelStyle + '" title="' + (label.full_name || label.name) + '" aria-label="' + (currentLanguage === 'zh' ? '地圖標記圖標' : 'Map Marker Icon') + '" data-zh="地圖標記圖標" data-en="Map Marker Icon">' + displayName + '</div>',
            className: 'custom-div-icon leaflet-marker-icon leaflet-zoom-animated leaflet-interactive',
            iconSize: iconSize,
            iconAnchor: iconAnchor
        });
        
        var marker = L.marker([label.lat, label.lon], {
            icon: divIcon,
            zIndexOffset: 1000
        }).addTo(map);
    });
    
    console.log('地圖標籤重新生成完成！');
}

// 初始化語言標籤的函數
function initializeLanguageLabels() {
    console.log('初始化語言標籤...');
    
    // 為所有地圖標記添加語言標籤
    setTimeout(function() {
        const mapMarkers = document.querySelectorAll('.leaflet-marker-icon');
        mapMarkers.forEach(marker => {
            marker.setAttribute('aria-label', currentLanguage === 'zh' ? '地圖標記圖標' : 'Map Marker Icon');
        });
        
        // 為所有自定義圖標添加語言標籤
        const customIcons = document.querySelectorAll('.custom-div-icon');
        customIcons.forEach(icon => {
            icon.setAttribute('aria-label', currentLanguage === 'zh' ? '自定義圖標' : 'Custom Icon');
        });
        
        // 為所有村里標籤添加語言標籤
        const villageLabels = document.querySelectorAll('.village-label');
        villageLabels.forEach(label => {
            label.setAttribute('aria-label', currentLanguage === 'zh' ? '村里標籤' : 'Village Label');
        });
        
        // 為district-list添加語言標籤
        const districtList = document.getElementById('district-list');
        if (districtList) {
            districtList.setAttribute('aria-label', currentLanguage === 'zh' ? '行政區列表' : 'District List');
        }
        
        console.log('語言標籤初始化完成！');
    }, 1000);
}
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
    // 重新獲取語言設置
    var urlParams = new URLSearchParams(window.location.search);
    var currentLanguage = urlParams.get('lang') || 'zh';
    window.currentLanguage = currentLanguage;
    
    var cityBreadcrumb = document.getElementById('city-breadcrumb');
    var districtBreadcrumb = document.getElementById('district-breadcrumb');
    var villageBreadcrumb = document.getElementById('village-breadcrumb');
    
    // 重置所有面包屑
    cityBreadcrumb.style.display = 'inline';
    districtBreadcrumb.style.display = 'none';
    villageBreadcrumb.style.display = 'none';
    
    if (view === 'district') {
        // 只顯示城市級別
        cityBreadcrumb.innerHTML = (currentLanguage === 'zh' ? '台南市' : 'Tainan City');
        cityBreadcrumb.style.color = '#1f78b4';
        cityBreadcrumb.style.cursor = 'default';
    } else if (view === 'village' && districtName) {
        // 顯示城市 > 區域
        cityBreadcrumb.innerHTML = (currentLanguage === 'zh' ? '台南市' : 'Tainan City');
        cityBreadcrumb.style.color = '#1f78b4';
        cityBreadcrumb.style.cursor = 'pointer';
        
        districtBreadcrumb.style.display = 'inline';
        // 使用翻譯後的區域名稱
        var displayDistrictName = districtName;
        if (currentLanguage === 'en') {
            displayDistrictName = window.districtTranslations && window.districtTranslations[districtName] ? window.districtTranslations[districtName] : districtName;
        }
        districtBreadcrumb.innerHTML = ' > ' + displayDistrictName;
        districtBreadcrumb.style.color = '#1f78b4';
        districtBreadcrumb.style.cursor = 'pointer';
        
        if (villageName) {
            // 顯示城市 > 區域 > 村里
            villageBreadcrumb.style.display = 'inline';
            // 使用翻譯後的村里名稱
            var displayVillageName = villageName;
            if (currentLanguage === 'en') {
                displayVillageName = window.villageTranslations && window.villageTranslations[villageName] ? window.villageTranslations[villageName] : villageName;
            }
            villageBreadcrumb.innerHTML = ' > ' + displayVillageName;
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
    
    // 重新獲取語言設置
    var urlParams = new URLSearchParams(window.location.search);
    var currentLanguage = urlParams.get('lang') || 'zh';
    window.currentLanguage = currentLanguage;
    
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
    
    if (title) {
        // 根據語言顯示區域名稱
        var displayDistrictName = districtName;
        if (currentLanguage === 'en') {
            displayDistrictName = window.districtTranslations && window.districtTranslations[districtName] ? window.districtTranslations[districtName] : districtName;
        }
        title.textContent = displayDistrictName;
    }
    
    // 查找預測資料
    var forecastData = window.forecastData;
    if (forecastData && forecastData.district_data) {
        var districtData = Object.values(forecastData.district_data).find(d => d.district_name === districtName);
        if (districtData) {
            console.log('找到區域資料:', districtData);
            
            // 顯示人口資料
            var popData = window.populationData && window.populationData[districtName];
            if (population && popData) {
                population.textContent = popData.population.toLocaleString() + (currentLanguage === 'zh' ? ' 人' : ' people');
            }
            
            if (dengueCases) dengueCases.textContent = districtData.total_pred_cases + (currentLanguage === 'zh' ? ' 病例' : ' cases');
            
            // 計算每萬人病例率
            if (ratePer10k && popData && popData.population > 0) {
                var rate = (districtData.total_pred_cases / popData.population) * 10000;
                ratePer10k.textContent = rate.toFixed(2) + (currentLanguage === 'zh' ? ' /萬人' : ' /10k people');
            }
            
            if (riskLevel) {
                var riskText = '';
                if (districtData.total_pred_cases >= 1000) riskText = (currentLanguage === 'zh' ? '極高風險' : 'Very High Risk');
                else if (districtData.total_pred_cases >= 100) riskText = (currentLanguage === 'zh' ? '高風險' : 'High Risk');
                else if (districtData.total_pred_cases >= 10) riskText = (currentLanguage === 'zh' ? '中風險' : 'Medium Risk');
                else riskText = (currentLanguage === 'zh' ? '低風險' : 'Low Risk');
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
    
    // 重新獲取語言設置
    var urlParams = new URLSearchParams(window.location.search);
    var currentLanguage = urlParams.get('lang') || 'zh';
    window.currentLanguage = currentLanguage;
    
    // 初始化語言標籤
    if (typeof initializeLanguageLabels === 'function') {
        initializeLanguageLabels();
    }
    
    // 顯示當前週次
    var weekElement = document.getElementById('current-week');
    if (weekElement && forecastData && forecastData.latest_week) {
        weekElement.textContent = forecastData.latest_week;
    } else if (weekElement) {
        weekElement.textContent = (currentLanguage === 'zh' ? '載入中...' : 'Loading...');
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
    
    // 重新獲取語言設置
    var urlParams = new URLSearchParams(window.location.search);
    var currentLanguage = urlParams.get('lang') || 'zh';
    window.currentLanguage = currentLanguage;
    
    currentView = 'district';
    currentDistrict = null;
    currentVillage = null;
    
    // 更新標題
    var titleElement = document.getElementById('sidebar-main-title');
    if (titleElement) {
        titleElement.textContent = (currentLanguage === 'zh' ? '行政區列表' : 'District List');
    }
    
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
        // 使用翻譯後的區域名稱
        var displayDistrictName = district.name;
        if (currentLanguage === 'en') {
            displayDistrictName = window.districtTranslations && window.districtTranslations[district.name] ? window.districtTranslations[district.name] : district.name;
        }
        contentHtml += '<span style="font-weight: 600;">' + displayDistrictName + '</span>';
        if (district.predCases > 0) {
            contentHtml += '<br><span style="font-size: 12px; color: #666;">' + (currentLanguage === 'zh' ? '預測病例' : 'Predicted Cases') + ': ' + district.predCases + '</span>';
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
    
    // 重新獲取語言設置
    var urlParams = new URLSearchParams(window.location.search);
    var currentLanguage = urlParams.get('lang') || 'zh';
    window.currentLanguage = currentLanguage;
    
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
    var titleElement = document.getElementById('sidebar-main-title');
    if (titleElement) {
        // 使用翻譯後的區域名稱
        var displayDistrictName = districtName;
        if (currentLanguage === 'en') {
            displayDistrictName = window.districtTranslations && window.districtTranslations[districtName] ? window.districtTranslations[districtName] : districtName;
        }
        titleElement.textContent = displayDistrictName + (currentLanguage === 'zh' ? '村里列表' : ' Village List');
    }
    
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
        // 使用翻譯後的村里名稱
        var displayVillageName = village.village_name;
        if (currentLanguage === 'en') {
            displayVillageName = window.villageTranslations && window.villageTranslations[village.village_name] ? window.villageTranslations[village.village_name] : village.village_name;
        }
        contentHtml += '<span style="font-weight: 600;">' + displayVillageName + '</span>';
        if (village.pred_cases > 0) {
            contentHtml += '<br><span style="font-size: 12px; color: #666;">' + (currentLanguage === 'zh' ? '預測病例' : 'Predicted Cases') + ': ' + village.pred_cases + '</span>';
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
            
            // 重新獲取語言設置
            var urlParams = new URLSearchParams(window.location.search);
            var currentLanguage = urlParams.get('lang') || 'zh';
            window.currentLanguage = currentLanguage;
            
            // 創建彈出窗口內容
            var popupContent = '<div style="min-width: 220px;">';
            // 使用翻譯後的區域名稱作為標題
            var displayDistrictNameTitle = props.district_name;
            if (currentLanguage === 'en') {
                displayDistrictNameTitle = window.districtTranslations && window.districtTranslations[props.district_name] ? window.districtTranslations[props.district_name] : props.district_name;
            }
            popupContent += '<h4 style="margin: 0 0 10px 0; color: #1f78b4;">' + displayDistrictNameTitle + '</h4>';
            popupContent += '<table style="width: 100%; font-size: 13px;">';
            // 使用翻譯後的區域名稱
            var displayDistrictName = props.district_name;
            if (currentLanguage === 'en') {
                displayDistrictName = window.districtTranslations && window.districtTranslations[props.district_name] ? window.districtTranslations[props.district_name] : props.district_name;
            }
            popupContent += '<tr><td><strong>' + (currentLanguage === 'zh' ? '區域:' : 'District:') + '</strong></td><td>' + displayDistrictName + '</td></tr>';
            // 使用翻譯後的村里名稱
            var displayVillageNamePopup = props.village_name;
            if (currentLanguage === 'en') {
                displayVillageNamePopup = window.villageTranslations && window.villageTranslations[props.village_name] ? window.villageTranslations[props.village_name] : props.village_name;
            }
            popupContent += '<tr><td><strong>' + (currentLanguage === 'zh' ? '村里:' : 'Village:') + '</strong></td><td>' + displayVillageNamePopup + '</td></tr>';
            popupContent += '<tr><td><strong>' + (currentLanguage === 'zh' ? '預測病例:' : 'Predicted Cases:') + '</strong></td><td><span style="color: #e74c3c; font-weight: bold;">' + (props.pred_cases || 0) + ' ' + (currentLanguage === 'zh' ? '例' : 'Cases') + '</span></td></tr>';
            popupContent += '<tr><td><strong>' + (currentLanguage === 'zh' ? '區域人口:' : 'District Population:') + '</strong></td><td>' + (props.district_population || 0).toLocaleString() + (currentLanguage === 'zh' ? ' 人' : ' people') + '</td></tr>';
            popupContent += '<tr><td><strong>' + (currentLanguage === 'zh' ? '區域戶數:' : 'District Households:') + '</strong></td><td>' + (props.district_households || 0).toLocaleString() + (currentLanguage === 'zh' ? ' 戶' : ' households') + '</td></tr>';
            popupContent += '</table>';
            popupContent += '</div>';
            
            layer.bindPopup(popupContent);
            
            // 添加村里标签（只显示村里名称，不显示区名）
            var center = turf.centroid(feature);
            
            // 根據語言調整村里標籤樣式
            var villageLabelStyle, villageIconSize, villageIconAnchor;
            if (currentLanguage === 'zh') {
                // 中文版本：較小標籤
                villageLabelStyle = 'background: rgba(255, 255, 255, 0.9); border: 1px solid #1f78b4; border-radius: 4px; padding: 2px 6px; font-size: 12px; font-weight: 600; color: #1f78b4; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.3);';
                villageIconSize = [60, 20];
                villageIconAnchor = [30, 10];
            } else {
                // 英文版本：較大標籤，支持更長的村里名稱
                villageLabelStyle = 'background: rgba(255, 255, 255, 0.95); border: 1px solid #2c5aa0; border-radius: 6px; padding: 3px 8px; font-size: 11px; font-weight: 600; color: #2c5aa0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3); min-width: 50px;';
                villageIconSize = [70, 20];
                villageIconAnchor = [35, 10];
            }
            
            // 根據語言顯示村里名稱
            var displayVillageName = props.village_name;
            if (currentLanguage === 'en') {
                // 英文版本：使用翻譯字典
                var translatedName = window.villageTranslations && window.villageTranslations[props.village_name] ? window.villageTranslations[props.village_name] : props.village_name;
                displayVillageName = translatedName;
                console.log('村里翻譯:', props.village_name, '->', translatedName);
            }
            
            var label = L.marker([center.geometry.coordinates[1], center.geometry.coordinates[0]], {
                icon: L.divIcon({
                    className: 'village-label leaflet-marker-icon leaflet-zoom-animated leaflet-interactive',
                    html: '<div style="' + villageLabelStyle + '" aria-label="' + (currentLanguage === 'zh' ? '村里標籤' : 'Village Label') + '" data-zh="村里標籤" data-en="Village Label">' + displayVillageName + '</div>',
                    iconSize: villageIconSize,
                    iconAnchor: villageIconAnchor
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

# 行政區名稱縮寫對照表
district_abbreviations = {
    '南區': '南',
    '北區': '北', 
    '東區': '東',
    '中西區': '中西',
    '安平區': '安平',
    '安南區': '安南',
    '永康區': '永康',
    '歸仁區': '歸仁',
    '新化區': '新化',
    '左鎮區': '左鎮',
    '玉井區': '玉井',
    '楠西區': '楠西',
    '南化區': '南化',
    '仁德區': '仁德',
    '關廟區': '關廟',
    '龍崎區': '龍崎',
    '官田區': '官田',
    '麻豆區': '麻豆',
    '佳里區': '佳里',
    '西港區': '西港',
    '七股區': '七股',
    '將軍區': '將軍',
    '學甲區': '學甲',
    '北門區': '北門',
    '新營區': '新營',
    '後壁區': '后壁',
    '白河區': '白河',
    '東山區': '東山',
    '六甲區': '六甲',
    '下營區': '下營',
    '柳營區': '柳營',
    '鹽水區': '鹽水',
    '善化區': '善化',
    '大內區': '大內',
    '山上區': '山上',
    '新市區': '新市',
    '安定區': '安定'
}

# 準備標籤數據（名稱和位置）
district_labels = []
for idx, row in gdf.iterrows():
    try:
        label_point = row.geometry.representative_point()
    except:
        label_point = row.geometry.centroid
    
    # 使用縮寫名稱
    original_name = row['name']
    abbreviated_name = district_abbreviations.get(original_name, original_name)
    
    district_labels.append({
        'name': abbreviated_name,
        'full_name': original_name,  # 保留完整名稱用於彈出窗口
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

# 語言翻譯對照表
translations = {
    'zh': {
        'title': '台南市登革熱疫情資料',
        'prediction_week': '預測週次：',
        'loading': '載入中...',
        'district_list': '行政區列表',
        'tainan_city': '台南市',
        'district_suffix': '區',
        'village_list': '村里列表',
        'predicted_cases': '預測病例',
        'cases': '病例',
        'population_data': '人口數據:',
        'dengue_cases': '登革熱預測病例:',
        'rate_per_10k': '每萬人病例率:',
        'risk_level': '風險等級:',
        'last_update': '更新時間:',
        'people': ' 人',
        'per_10k': ' /萬人',
        'very_high_risk': '極高風險',
        'high_risk': '高風險',
        'medium_risk': '中風險',
        'low_risk': '低風險'
    },
    'en': {
        'title': 'Tainan City Dengue Fever Epidemic Data',
        'prediction_week': 'Prediction Week:',
        'loading': 'Loading...',
        'district_list': 'District List',
        'tainan_city': 'Tainan City',
        'district_suffix': ' Dist.',
        'village_list': ' Village List',
        'predicted_cases': 'Predicted Cases',
        'cases': 'Cases',
        'population_data': 'Population Data:',
        'dengue_cases': 'Dengue Predicted Cases:',
        'rate_per_10k': 'Cases per 10k People:',
        'risk_level': 'Risk Level:',
        'last_update': 'Last Update:',
        'people': ' people',
        'per_10k': ' /10k people',
        'very_high_risk': 'Very High Risk',
        'high_risk': 'High Risk',
        'medium_risk': 'Medium Risk',
        'low_risk': 'Low Risk'
    }
}

village_translations = {
    "zh": {
        # 中文版本保持原樣
    },
    "en": {
        "內角里": "NeiJiao",
        "蓮潭里": "LianTan",
        "草店里": "CaoDian",
        "詔安里": "ZhaoAn",
        "嘉田里": "JiaTian",
        "崎內里": "QiNei",
        "崁頂里": "KanDing",
        "廣安里": "GuangAn",
        "甘宅里": "GanZhai",
        "嘉民里": "JiaMin",
        "菁豊里": "JingLi",
        "土溝里": "TuGou",
        "玉豐里": "YuFeng",
        "菁寮里": "JingLiao",
        "長安里": "ZhangAn",
        "崁頭里": "KanTou",
        "東正里": "DongZheng",
        "埤寮里": "PiLiao",
        "福安里": "FuAn",
        "水秀里": "ShuiXiu",
        "六溪里": "LiuXi",
        "下中里": "XiaZhong",
        "義稠里": "YiChou",
        "土庫里": "TuKu",
        "大客里": "DaKe",
        "聖賢里": "ShengXian",
        "武廟里": "WuMiao",
        "後■里": "Hou",
        "竹門里": "ZhuMen",
        "墨林里": "MoLin",
        "新嘉里": "XinJia",
        "侯伯里": "HouBo",
        "昇安里": "ShengAn",
        "平安里": "PingAn",
        "大竹里": "DaZhu",
        "汴頭里": "BianTou",
        "頂長里": "DingZhang",
        "後壁里": "HouBi",
        "仙草里": "XianCao",
        "仕安里": "ShiAn",
        "虎山里": "HuShan",
        "嘉苳里": "JiaDong",
        "庄內里": "ZhuangNei",
        "秀祐里": "XiuYou",
        "竹新里": "ZhuXin",
        "汫水里": "JingShui",
        "永安里": "YongAn",
        "河東里": "HeDong",
        "白河里": "BaiHe",
        "外角里": "WaiJiao",
        "烏樹里": "WuShu",
        "新東里": "XinDong",
        "頂安里": "DingAn",
        "關嶺里": "GuanLing",
        "護鎮里": "HuZhen",
        "大林里": "DaLin",
        "雙春里": "ShuangChun",
        "三榮里": "SanRong",
        "岸內里": "AnNei",
        "東山里": "DongShan",
        "三仙里": "SanXian",
        "後宅里": "HouZhai",
        "中營里": "ZhongYing",
        "新南里": "XinNan",
        "嘉芳里": "JiaFang",
        "錦湖里": "JinHu",
        "東原里": "DongYuan",
        "大宏里": "DaHong",
        "太南里": "TaiNan",
        "人和里": "RenHe",
        "桐寮里": "TongLiao",
        "光華里": "GuangHua",
        "舊■里": "Jiu",
        "角帶里": "JiaoDai",
        "大農里": "DaNong",
        "水雲里": "ShuiYun",
        "旭山里": "XuShan",
        "舊營里": "JiuYing",
        "民權里": "MinQuan",
        "民生里": "MinSheng",
        "科里里": "KeLi",
        "東河里": "DongHe",
        "南紙里": "NanZhi",
        "民榮里": "MinRong",
        "興業里": "XingYe",
        "太康里": "TaiKang",
        "永生里": "YongSheng",
        "重溪里": "ZhongXi",
        "太北里": "TaiBei",
        "鯤江里": "KunJiang",
        "好平里": "HaoPing",
        "延平里": "YanPing",
        "孫厝里": "SunCuo",
        "興安里": "XingAn",
        "三慶里": "SanQing",
        "大莊里": "DaZhuang",
        "南興里": "NanXing",
        "保吉里": "BaoJi",
        "高原里": "GaoYuan",
        "篤農里": "DuNong",
        "東壁里": "DongBi",
        "歡雅里": "HuanYa",
        "林安里": "LinAn",
        "中境里": "ZhongJing",
        "東中里": "DongZhong",
        "三生里": "SanSheng",
        "福得里": "FuDe",
        "橋南里": "QiaoNan",
        "新北里": "XinBei",
        "水正里": "ShuiZheng",
        "水仙里": "ShuiXian",
        "王公里": "WangGong",
        "忠政里": "ZhongZheng",
        "慈安里": "CiAn",
        "中洲里": "ZhongZhou",
        "河南里": "HeNan",
        "仁里里": "RenLi",
        "中社里": "ZhongShe",
        "後街里": "HouJie",
        "中樞里": "ZhongShu",
        "紅厝里": "HongCuo",
        "新達里": "XinDa",
        "大屯里": "DaTun",
        "宅內里": "ZhaiNei",
        "菁埔里": "JingPu",
        "大埤里": "DaPi",
        "新榮里": "XinRong",
        "豐和里": "FengHe",
        "北勢里": "BeiShi",
        "將富里": "JiangFu",
        "甲南里": "JiaNan",
        "茅港里": "MaoGang",
        "港尾里": "GangWei",
        "南■里": "Nan",
        "二鎮里": "ErZhen",
        "廣山里": "GuangShan",
        "龍湖里": "LongHu",
        "保源里": "BaoYuan",
        "新興里": "XinXing",
        "大丘里": "DaQiu",
        "甲東里": "JiaDong",
        "三光里": "SanGuang",
        "王爺里": "WangYe",
        "長沙里": "ZhangSha",
        "關山里": "GuanShan",
        "仁和里": "RenHe",
        "明宜里": "MingYi",
        "密枝里": "MiZhi",
        "北埔里": "BeiPu",
        "苓和里": "LingHe",
        "下營里": "XiaYing",
        "仁得里": "RenDe",
        "慈福里": "CiFu",
        "六甲里": "LiuJia",
        "營前里": "YingQian",
        "二甲里": "ErJia",
        "東昇里": "DongSheng",
        "光福里": "GuangFu",
        "姑爺里": "GuYe",
        "士林里": "ShiLin",
        "田寮里": "TianLiao",
        "永隆里": "YongLong",
        "青山里": "QingShan",
        "飯店里": "FanDian",
        "竹埔里": "ZhuPu",
        "南溪里": "NanXi",
        "八翁里": "BaWeng",
        "五興里": "WuXing",
        "中埕里": "ZhongCheng",
        "鐵線里": "TieXian",
        "南勢里": "NanShi",
        "玉港里": "YuGang",
        "宅港里": "ZhaiGang",
        "永華里": "YongHua",
        "嶺南里": "LingNan",
        "北門里": "BeiMen",
        "大豐里": "DaFeng",
        "秀昌里": "XiuChang",
        "果毅里": "GuoYi",
        "神農里": "ShenNong",
        "平和里": "PingHe",
        "下林里": "XiaLin",
        "南港里": "NanGang",
        "賀建里": "HeJian",
        "龜港里": "GuiGang",
        "水林里": "ShuiLin",
        "甲中里": "JiaZhong",
        "溪州里": "XiZhou",
        "埤頭里": "PiTou",
        "海埔里": "HaiPu",
        "忠興里": "ZhongXing",
        "營頂里": "YingDing",
        "鯤鯓里": "KunShen",
        "大崎里": "DaQi",
        "隆本里": "LongBen",
        "西和里": "XiHe",
        "寮■里": "Liao",
        "小埤里": "XiaoPi",
        "官田里": "GuanTian",
        "西華里": "XiHua",
        "大山里": "DaShan",
        "環湖里": "HuanHu",
        "東角里": "DongJiao",
        "豐里里": "FengLi",
        "漳洲里": "ZhangZhou",
        "總榮里": "ZongRong",
        "西庄里": "XiZhuang",
        "三協里": "SanXie",
        "新建里": "XinJian",
        "海澄里": "HaiCheng",
        "莊禮里": "ZhuangLi",
        "長榮里": "ZhangRong",
        "東庄里": "DongZhuang",
        "隆田里": "LongTian",
        "禮化里": "LiHua",
        "佳化里": "JiaHua",
        "大潭里": "DaTan",
        "油車里": "YouChe",
        "後港里": "HouGang",
        "灣丘里": "WanQiu",
        "興化里": "XingHua",
        "麻口里": "MaKou",
        "楠西里": "NanXi",
        "鯤溟里": "KunMing",
        "大埕里": "DaCheng",
        "西寮里": "XiLiao",
        "社子里": "SheZi",
        "七甲里": "QiJia",
        "照興里": "ZhaoXing",
        "大灣里": "DaWan",
        "平沙里": "PingSha",
        "西連里": "XiLian",
        "嘉昌里": "JiaChang",
        "將貴里": "JiangGui",
        "玉山里": "YuShan",
        "湖山里": "HuShan",
        "開化里": "KaiHua",
        "嘉南里": "JiaNan",
        "三吉里": "SanJi",
        "磚井里": "ZhuanJing",
        "安正里": "AnZheng",
        "嘉福里": "JiaFu",
        "安西里": "AnXi",
        "黦}里": "Yue",
        "東隆里": "DongLong",
        "中正里": "ZhongZheng",
        "安東里": "AnDong",
        "篤加里": "DuJia",
        "中寮里": "ZhongLiao",
        "溪美里": "XiMei",
        "鹿田里": "LuTian",
        "東昌里": "DongChang",
        "東寧里": "DongNing",
        "金砂里": "JinSha",
        "通興里": "TongXing",
        "後營里": "HouYing",
        "胡厝里": "HuCuo",
        "什乃里": "ShenNai",
        "營西里": "YingXi",
        "光文里": "GuangWen",
        "忠仁里": "ZhongRen",
        "建南里": "JianNan",
        "安業里": "AnYe",
        "石湖里": "ShiHu",
        "胡家里": "HuJia",
        "鎮山里": "ZhenShan",
        "龜丹里": "GuiDan",
        "中民里": "ZhongMin",
        "嘉北里": "JiaBei",
        "謝安里": "XieAn",
        "大寮里": "DaLiao",
        "頂山里": "DingShan",
        "穀興里": "GuXing",
        "拔林里": "BaLin",
        "子龍里": "ZiLong",
        "東勢里": "DongShi",
        "保安里": "BaoAn",
        "城內里": "ChengNei",
        "民安里": "MinAn",
        "茼縐": "TongZhou",
        "巷口里": "XiangKou",
        "中興里": "ZhongXing",
        "渡頭里": "DuTou",
        "興農里": "XingNong",
        "六安里": "LuAn",
        "龍泉里": "LongQuan",
        "頂■里": "Ding",
        "六德里": "LiuDe",
        "六分里": "LiuFen",
        "頭社里": "TouShe",
        "西港里": "XiGang",
        "龍山里": "LongShan",
        "龍安里": "LongAn",
        "石林里": "ShiLin",
        "東關里": "DongGuan",
        "竹圍里": "ZhuWei",
        "安定里": "AnDing",
        "管寮里": "GuanLiao",
        "石城里": "ShiCheng",
        "竹港里": "ZhuGang",
        "南海里": "NanHai",
        "劉厝里": "LiuCuo",
        "文正里": "WenZheng",
        "內郭里": "NeiGuo",
        "七股里": "QiGu",
        "明和里": "MingHe",
        "溪南里": "XiNan",
        "蚶寮里": "HanLiao",
        "北關里": "BeiGuan",
        "蘇林里": "SuLin",
        "看坪里": "KanPing",
        "小新里": "XiaoXin",
        "蘇厝里": "SuCuo",
        "西關里": "XiGuan",
        "曲溪里": "QuXi",
        "港東里": "GangDong",
        "三股里": "SanGu",
        "坐駕里": "ZuoJia",
        "南關里": "NanGuan",
        "文昌里": "WenChang",
        "三民里": "SanMin",
        "龜洞里": "GuiDong",
        "竹林里": "ZhuLin",
        "沙田里": "ShaTian",
        "玉井里": "YuJing",
        "保西里": "BaoXi",
        "大內里": "DaNei",
        "玉田里": "YuTian",
        "玉成里": "YuCheng",
        "牛庄里": "NiuZhuang",
        "■林里": "Lin",
        "二溪里": "ErXi",
        "慶安里": "QingAn",
        "竹橋里": "ZhuQiao",
        "山上里": "ShanShang",
        "大社里": "DaShe",
        "南洲里": "NanZhou",
        "三埔里": "SanPu",
        "層林里": "CengLin",
        "中榮里": "ZhongRong",
        "新莊里": "XinZhuang",
        "癸L里": "Gui",
        "港口里": "GangKou",
        "唪口里": "FengKou",
        "西埔里": "XiPu",
        "南化里": "NanHua",
        "洵w里": "Xun",
        "泵璅": "BengSuo",
        "礁坑里": "JiaoKeng",
        "烏竹里": "WuZhu",
        "埔園里": "PuYuan",
        "岡林里": "GangLin",
        "港南里": "GangNan",
        "新吉里": "XinJi",
        "平陽里": "PingYang",
        "潭頂里": "TanDing",
        "北寮里": "BeiLiao",
        "社內里": "SheNei",
        "大同里": "DaTong",
        "港墘里": "GangQian",
        "新市里": "XinShi",
        "榮和里": "RongHe",
        "新和里": "XinHe",
        "六嘉里": "LiuJia",
        "豐德里": "FengDe",
        "北平里": "BeiPing",
        "■拔里": "Ba",
        "大洲里": "DaZhou",
        "光和里": "GuangHe",
        "永就里": "YongJiu",
        "睦光里": "MuGuang",
        "小崙里": "XiaoLun",
        "羊林里": "YangLin",
        "中坑里": "ZhongKeng",
        "太平里": "TaiPing",
        "王行里": "WangXing",
        "左鎮里": "ZuoZhen",
        "澄山里": "ChengShan",
        "護國里": "HuGuo",
        "內庄里": "NeiZhuang",
        "蔦松里": "NiaoSong",
        "樹林里": "ShuLin",
        "安加里": "AnJia",
        "新復里": "XinFu",
        "內江里": "NeiJiang",
        "三和里": "SanHe",
        "十份里": "ShiFen",
        "望明里": "WangMing",
        "玉◢": "Yu",
        "南安里": "NanAn",
        "永吉里": "YongJi",
        "義合里": "YiHe",
        "海寮里": "HaiLiao",
        "永樂里": "YongLe",
        "豐華里": "FengHua",
        "三舍里": "SanShe",
        "大營里": "DaYing",
        "永康里": "YongKang",
        "知義里": "ZhiYi",
        "崙頂里": "LunDing",
        "西勢里": "XiShi",
        "甲頂里": "JiaDing",
        "山ㄗ": "Shan",
        "大橋里": "DaQiao",
        "大坑里": "DaKeng",
        "網寮里": "WangLiao",
        "二王里": "ErWang",
        "北灣里": "BeiWan",
        "西橋里": "XiQiao",
        "建國里": "JianGuo",
        "神洲里": "ShenZhou",
        "土崎里": "TuQi",
        "二寮里": "ErLiao",
        "勝利里": "ShengLi",
        "南灣里": "NanWan",
        "東灣里": "DongWan",
        "安康里": "AnKang",
        "復華里": "FuHua",
        "西灣里": "XiWan",
        "草山里": "CaoShan",
        "五王里": "WuWang",
        "三合里": "SanHe",
        "六合里": "LiuHe",
        "大廟里": "DaMiao",
        "媽廟里": "MaMiao",
        "復國里": "FuGuo",
        "崑山里": "KunShan",
        "協興里": "XieXing",
        "龍潭里": "LongTan",
        "東榮里": "DongRong",
        "觀音里": "GuanYin",
        "清水里": "QingShui",
        "正強里": "ZhengQiang",
        "豐榮里": "FengRong",
        "東橋里": "DongQiao",
        "東和里": "DongHe",
        "中央里": "ZhongYang",
        "全興里": "QuanXing",
        "武安里": "WuAn",
        "新樹里": "XinShu",
        "尚頂里": "ShangDing",
        "後市里": "HouShi",
        "許厝里": "XuCuo",
        "新田里": "XinTian",
        "歸南里": "GuiNan",
        "辜厝里": "GuCuo",
        "新厝里": "XinCuo",
        "看東里": "KanDong",
        "香洋里": "XiangYang",
        "看西里": "KanXi",
        "關廟里": "GuanMiao",
        "南花里": "NanHua",
        "仁愛里": "RenAi",
        "成功里": "ChengGong",
        "松腳里": "SongJiao",
        "龍船里": "LongChuan",
        "沙崙里": "ShaLun",
        "五甲里": "WuJia",
        "大坪里": "DaPing",
        "上崙里": "ShangLun",
        "楠坑里": "NanKeng",
        "深坑里": "ShenKeng",
        "田厝里": "TianCuo",
        "牛埔里": "NiuPu",
        "武東里": "WuDong",
        "三甲里": "SanJia",
        "大甲里": "DaJia",
        "布袋里": "BuDai",
        "二行里": "ErXing",
        "中生里": "ZhongSheng",
        "田中里": "TianZhong",
        "復興里": "FuXing",
        "中華里": "ZhongHua",
        "光復里": "GuangFu",
        "新光里": "XinGuang",
        "太子里": "TaiZi",
        "下湖里": "XiaHu",
        "崎頂里": "QiDing",
        "一甲里": "YiJia",
        "新埔里": "XinPu",
        "仁德里": "RenDe",
        "八甲里": "BaJia",
        "仁義里": "RenYi",
        "北花里": "BeiHua",
        "南保里": "NanBao",
        "文化里": "WenHua",
        "歸仁里": "GuiRen",
        "山西里": "ShanXi",
        "石■里": "Shi",
        "城西里": "ChengXi",
        "■南里": "Nan",
        "州北里": "ZhouBei",
        "城東里": "ChengDong",
        "學東里": "XueDong",
        "砂崙里": "ShaLun",
        "青草里": "QingCao",
        "佃西里": "DianXi",
        "佃東里": "DianDong",
        "公親里": "GongQin",
        "公■里": "Gong",
        "新順里": "XinShun",
        "安順里": "AnShun",
        "淵中里": "YuanZhong",
        "洛虼": "LuoGe",
        "海東里": "HaiDong",
        "鳳凰里": "FengHuang",
        "梅花里": "MeiHua",
        "成德里": "ChengDe",
        "文元里": "WenYuan",
        "小康里": "XiaoKang",
        "大和里": "DaHe",
        "正覺里": "ZhengJue",
        "永祥里": "YongXiang",
        "安慶里": "AnQing",
        "海西里": "HaiXi",
        "理想里": "LiXiang",
        "鹿耳里": "LuEr",
        "安和里": "AnHe",
        "大安里": "DaAn",
        "四草里": "SiCao",
        "安富里": "AnFu",
        "溪墘里": "XiQian",
        "溪東里": "XiDong",
        "溪北里": "XiBei",
        "海佃里": "HaiDian",
        "溪頂里": "XiDing",
        "國安里": "GuoAn",
        "海南里": "HaiNan",
        "幸福里": "XingFu",
        "城南里": "ChengNan",
        "州南里": "ZhouNan",
        "城中里": "ChengZhong",
        "城北里": "ChengBei",
        "淵西里": "YuanXi",
        "淵東里": "YuanDong",
        "顯宮里": "XianGong",
        "溪心里": "XiXin",
        "原佃里": "YuanDian",
        "總頭里": "ZongTou",
        "新勝里": "XinSheng",
        "光武里": "GuangWu",
        "大道里": "DaDao",
        "文成里": "WenCheng",
        "國興里": "GuoXing",
        "賢北里": "XianBei",
        "石門里": "ShiMen",
        "安民里": "AnMin",
        "東興里": "DongXing",
        "五福里": "WuFu",
        "三德里": "SanDe",
        "玉皇里": "YuHuang",
        "成大里": "ChengDa",
        "藥王里": "YaoWang",
        "港仔里": "GangZai",
        "大學里": "DaXue",
        "力行里": "LiXing",
        "國姓里": "GuoXing",
        "勝安里": "ShengAn",
        "華興里": "HuaXing",
        "大仁里": "DaRen",
        "振興里": "ZhenXing",
        "興北里": "XingBei",
        "和順里": "HeShun",
        "西賢里": "XiXian",
        "光賢里": "GuangXian",
        "重興里": "ZhongXing",
        "西湖里": "XiHu",
        "中樓里": "ZhongLou",
        "興南里": "XingNan",
        "西門里": "XiMen",
        "海頭里": "HaiTou",
        "長德里": "ZhangDe",
        "文賢里": "WenXian",
        "公園里": "GongYuan",
        "裕民里": "YuMin",
        "協和里": "XieHe",
        "金城里": "JinCheng",
        "正風里": "ZhengFeng",
        "開元里": "KaiYuan",
        "大港里": "DaGang",
        "實踐里": "ShiJian",
        "元寶里": "YuanBao",
        "東明里": "DongMing",
        "漁光里": "YuGuang",
        "銀同里": "YinTong",
        "中西里": "ZhongXi",
        "萬昌里": "WanChang",
        "育平里": "YuPing",
        "國平里": "GuoPing",
        "東門里": "DongMen",
        "崇誨里": "ChongHui",
        "郡西里": "JunXi",
        "小西里": "XiaoXi",
        "南聖里": "NanSheng",
        "元安里": "YuanAn",
        "文平里": "WenPing",
        "進學里": "JinXue",
        "裕農里": "YuNong",
        "衛國里": "WeiGuo",
        "開山里": "KaiShan",
        "裕聖里": "YuSheng",
        "金華里": "JinHua",
        "忠孝里": "ZhongXiao",
        "彰南里": "ZhangNan",
        "虎尾里": "HuWei",
        "路東里": "LuDong",
        "再興里": "ZaiXing",
        "大成里": "DaCheng",
        "明德里": "MingDe",
        "文華里": "WenHua",
        "東安里": "DongAn",
        "泉南里": "QuanNan",
        "東聖里": "DongSheng",
        "富強里": "FuQiang",
        "廣州里": "GuangZhou",
        "關聖里": "GuanSheng",
        "新昌里": "XinChang",
        "大南里": "DaNan",
        "文南里": "WenNan",
        "富裕里": "FuYu",
        "五妃里": "WuFei",
        "文聖里": "WenSheng",
        "自強里": "ZiQiang",
        "法華里": "FaHua",
        "德光里": "DeGuang",
        "崇信里": "ChongXin",
        "普濟里": "PuJi",
        "小東里": "XiaoDong",
        "天后里": "TianHou",
        "莊敬里": "ZhuangJing",
        "赤嵌里": "ChiQian",
        "協進里": "XieJin",
        "平通里": "PingTong",
        "後甲里": "HouJia",
        "億載里": "YiZai",
        "建平里": "JianPing",
        "怡平里": "YiPing",
        "安海里": "AnHai",
        "華平里": "HuaPing",
        "大涼里": "DaLiang",
        "公正里": "GongZheng",
        "永福里": "YongFu",
        "東光里": "DongGuang",
        "圍下里": "WeiXia",
        "民主里": "MinZhu",
        "青年里": "QingNian",
        "大忠里": "DaZhong",
        "明亮里": "MingLiang",
        "崇成里": "ChongCheng",
        "白雪里": "BaiXue",
        "崇文里": "ChongWen",
        "德高里": "DeGao",
        "開南里": "KaiNan",
        "大恩里": "DaEn",
        "郡南里": "JunNan",
        "明興里": "MingXing",
        "大智里": "DaZhi",
        "東智里": "DongZhi",
        "南華里": "NanHua",
        "南都里": "NanDou",
        "喜北里": "XiBei",
        "喜東里": "XiDong",
        "喜南里": "XiNan",
        "省躬里": "ShengGong",
        "永寧里": "YongNing",
        "松安里": "SongAn",
        "同安里": "TongAn",
        "佛壇里": "FuTan",
        "郡王里": "JunWang",
        "竹溪里": "ZhuXi",
        "新生里": "XinSheng",
        "崇善里": "ChongShan",
        "和平里": "HePing",
        "崇學里": "ChongXue",
        "大德里": "DaDe",
        "國宅里": "GuoZhai",
        "崇德里": "ChongDe",
        "荔宅里": "LiZhai",
        "大福里": "DaFu",
        "日新里": "RiXin",
        "府南里": "FuNan",
        "光明里": "GuangMing",
        "崇明里": "ChongMing",
        "中沙里": "ZhongSha",
    }
}


def get_village_translation(village_name, language):
    """獲取村里名稱的翻譯"""
    if language == 'zh':
        return village_name
    elif language == 'en':
        # 英文版本：使用翻譯字典
        return village_translations['en'].get(village_name, village_name)
    else:
        return village_name

# 區域名稱翻譯對照表
district_translations = {
    'zh': {
        '中西區': '中西區',
        '東區': '東區',
        '南區': '南區',
        '北區': '北區',
        '安平區': '安平區',
        '安南區': '安南區',
        '永康區': '永康區',
        '歸仁區': '歸仁區',
        '新化區': '新化區',
        '左鎮區': '左鎮區',
        '玉井區': '玉井區',
        '楠西區': '楠西區',
        '南化區': '南化區',
        '仁德區': '仁德區',
        '關廟區': '關廟區',
        '龍崎區': '龍崎區',
        '官田區': '官田區',
        '麻豆區': '麻豆區',
        '佳里區': '佳里區',
        '西港區': '西港區',
        '七股區': '七股區',
        '將軍區': '將軍區',
        '學甲區': '學甲區',
        '北門區': '北門區',
        '新營區': '新營區',
        '後壁區': '後壁區',
        '白河區': '白河區',
        '東山區': '東山區',
        '六甲區': '六甲區',
        '下營區': '下營區',
        '柳營區': '柳營區',
        '鹽水區': '鹽水區',
        '善化區': '善化區',
        '大內區': '大內區',
        '山上區': '山上區',
        '新市區': '新市區',
        '安定區': '安定區'
    },
    'en': {
        # 使用簡潔的英文名稱，適合地圖標籤顯示
        '中西區': 'W. Central',
        '東區': 'East',
        '南區': 'South',
        '北區': 'North',
        '安平區': 'Anping',
        '安南區': 'Annan',
        '永康區': 'Yongkang',
        '歸仁區': 'Guiren',
        '新化區': 'Xinhua',
        '左鎮區': 'Zuozhen',
        '玉井區': 'Yujing',
        '楠西區': 'Nanxi',
        '南化區': 'Nanhua',
        '仁德區': 'Rende',
        '關廟區': 'Guanmiao',
        '龍崎區': 'Longqi',
        '官田區': 'Guantian',
        '麻豆區': 'Madou',
        '佳里區': 'Jiali',
        '西港區': 'Xigang',
        '七股區': 'Cigu',
        '將軍區': 'Jiangjun',
        '學甲區': 'Xuejia',
        '北門區': 'Beimen',
        '新營區': 'Xinying',
        '後壁區': 'Houbi',
        '白河區': 'Baihe',
        '東山區': 'Dongshan',
        '六甲區': 'Liujia',
        '下營區': 'Xiaying',
        '柳營區': 'Liuying',
        '鹽水區': 'Yanshui',
        '善化區': 'Shanhua',
        '大內區': 'Danei',
        '山上區': 'Shanshang',
        '新市區': 'Xinshi',
        '安定區': 'Anding'
    }
}

# 獲取語言參數（從環境變量或默認為中文）
import os
language = os.environ.get('LANGUAGE', 'zh')
if language not in translations:
    language = 'zh'

# 獲取翻譯文本的函數
def get_translation(key):
    return translations[language].get(key, translations['zh'][key])

# 獲取翻譯後的區域名稱
def get_district_translation(district_name):
    return district_translations[language].get(district_name, district_name)

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
    f"// 人口資料\nvar populationData = {population_data_json};\n\n// 登革熱預測數據\nvar forecastData = {forecast_data_json};\n\n// 區域名稱翻譯對照表\nwindow.districtTranslations = {json.dumps(district_translations[language])};\n\n// 村里名稱翻譯對照表\nwindow.villageTranslations = {json.dumps(village_translations[language])};\n\ndocument.addEventListener('DOMContentLoaded', function() {{"
)

# 替換語言相關的文本
fixed_html = fixed_html.replace("TITLE_PLACEHOLDER", get_translation('title'))
fixed_html = fixed_html.replace("PREDICTION_WEEK_PLACEHOLDER", get_translation('prediction_week'))
fixed_html = fixed_html.replace("LOADING_PLACEHOLDER", get_translation('loading'))
fixed_html = fixed_html.replace("DISTRICT_LIST_PLACEHOLDER", get_translation('district_list'))
fixed_html = fixed_html.replace("TAINAN_CITY_PLACEHOLDER", get_translation('tainan_city'))
fixed_html = fixed_html.replace("DISTRICT_SUFFIX_PLACEHOLDER", get_translation('district_suffix'))
fixed_html = fixed_html.replace("VILLAGE_LIST_PLACEHOLDER", get_translation('village_list'))
fixed_html = fixed_html.replace("PREDICTED_CASES_PLACEHOLDER", get_translation('predicted_cases'))
fixed_html = fixed_html.replace("CASES_PLACEHOLDER", get_translation('cases'))
fixed_html = fixed_html.replace("POPULATION_DATA_PLACEHOLDER", get_translation('population_data'))
fixed_html = fixed_html.replace("DENGUE_CASES_PLACEHOLDER", get_translation('dengue_cases'))
fixed_html = fixed_html.replace("RATE_PER_10K_PLACEHOLDER", get_translation('rate_per_10k'))
fixed_html = fixed_html.replace("RISK_LEVEL_PLACEHOLDER", get_translation('risk_level'))
fixed_html = fixed_html.replace("LAST_UPDATE_PLACEHOLDER", get_translation('last_update'))
fixed_html = fixed_html.replace("PEOPLE_PLACEHOLDER", get_translation('people'))
fixed_html = fixed_html.replace("PER_10K_PLACEHOLDER", get_translation('per_10k'))
fixed_html = fixed_html.replace("VERY_HIGH_RISK_PLACEHOLDER", get_translation('very_high_risk'))
fixed_html = fixed_html.replace("HIGH_RISK_PLACEHOLDER", get_translation('high_risk'))
fixed_html = fixed_html.replace("MEDIUM_RISK_PLACEHOLDER", get_translation('medium_risk'))
fixed_html = fixed_html.replace("LOW_RISK_PLACEHOLDER", get_translation('low_risk'))

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
