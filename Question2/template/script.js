// 簡化版本的script.js - 只保留核心功能

// 語言切換功能
var urlParams = new URLSearchParams(window.location.search);
let currentLanguage = urlParams.get('lang') || 'zh';

// 翻譯對照表
const translations = {
    'zh': {
        '台南市登革熱疫情資料': '台南市登革熱疫情資料',
        '預測週次：': '預測週次：',
        '載入中...': '載入中...',
        '行政區列表': '行政區列表',
        '台南市': '台南市',
        '區': '區',
        '里': '里',
        '村里列表': '村里列表',
        '預測病例': '預測病例',
        '病例': '病例',
        '個病例': '個病例',
        '無病例': '無病例',
        '區域': '區域',
        '村里': '村里',
        '總計': '總計',
        '個監測點': '個監測點',
        'district-list': '行政區列表',
        'leaflet-marker-icon': '地圖標記圖標',
        'custom-div-icon': '自定義圖標',
        'leaflet-zoom-animated': '地圖縮放動畫',
        'leaflet-interactive': '地圖互動元素',
        'village-label': '村里標籤',
        '例': '例',
        '人': '人',
        '戶': '戶',
        '極高風險': '極高風險',
        '高風險': '高風險',
        '中風險': '中風險',
        '低風險': '低風險',
        '人口數據:': '人口數據:',
        '登革熱預測病例:': '登革熱預測病例:',
        '每萬人病例率:': '每萬人病例率:',
        '風險等級:': '風險等級:',
        '更新時間:': '更新時間:'
    },
    'en': {
        '台南市登革熱疫情資料': 'Tainan City Dengue Fever Epidemic Data',
        '預測週次：': 'Prediction Week:',
        '載入中...': 'Loading...',
        '行政區列表': 'District List',
        '台南市': 'Tainan City',
        '區': ' Dist.',
        '里': ' Village',
        '村里列表': ' Village List',
        '預測病例': 'Predicted Cases',
        '病例': 'Cases',
        '個病例': ' Cases',
        '無病例': 'No Cases',
        '區域': 'District',
        '村里': 'Village',
        '總計': 'Total',
        '個監測點': ' Monitoring Points',
        'district-list': 'District List',
        'leaflet-marker-icon': 'Map Marker Icon',
        'custom-div-icon': 'Custom Icon',
        'leaflet-zoom-animated': 'Map Zoom Animation',
        'leaflet-interactive': 'Map Interactive Element',
        'village-label': 'Village Label',
        '例': 'Cases',
        '人': ' people',
        '戶': ' households',
        '極高風險': 'Very High Risk',
        '高風險': 'High Risk',
        '中風險': 'Medium Risk',
        '低風險': 'Low Risk',
        '人口數據:': 'Population Data:',
        '登革熱預測病例:': 'Dengue Predicted Cases:',
        '每萬人病例率:': 'Cases per 10k People:',
        '風險等級:': 'Risk Level:',
        '更新時間:': 'Last Update:'
    }
};

function getTranslatedText(key) {
    return translations[currentLanguage][key] || key;
}

function updateLanguageElements() {
    // 更新所有可翻譯的元素
    document.querySelectorAll('.translatable').forEach(element => {
        const text = element.textContent.trim();
        if (translations[currentLanguage] && translations[currentLanguage][text]) {
            element.textContent = translations[currentLanguage][text];
        } else if (element.dataset[currentLanguage]) {
            element.textContent = element.dataset[currentLanguage];
        }
    });
    
    // 更新CSS類名的aria-label屬性
    updateCSSClassLabels();
    
    // 更新地圖標籤
    updateMapLabels();
    
    // 更新彈出窗口內容
    updateAllPopupContent();
    
    // 重新生成區域列表
    if (typeof generateDistrictList === 'function') {
        generateDistrictList();
    }
    
    // 更新當前週次顯示
    updateCurrentWeek();
    
    // 重新生成地圖標籤
    if (typeof regenerateMapLabels === 'function') {
        regenerateMapLabels();
    }
    
    // 重新生成村里標籤
    if (typeof regenerateVillageLabels === 'function') {
        regenerateVillageLabels();
    }
    
    // 更新所有地圖標記的aria-label
    const mapMarkers = document.querySelectorAll('.leaflet-marker-icon');
    mapMarkers.forEach(marker => {
        marker.setAttribute('aria-label', translations[currentLanguage]['leaflet-marker-icon']);
    });
    
    // 更新所有自定義圖標的aria-label
    const customIcons = document.querySelectorAll('.custom-div-icon');
    customIcons.forEach(icon => {
        icon.setAttribute('aria-label', translations[currentLanguage]['custom-div-icon']);
    });
    
    // 更新所有村里標籤的aria-label
    const villageLabels = document.querySelectorAll('.village-label');
    villageLabels.forEach(label => {
        label.setAttribute('aria-label', translations[currentLanguage]['village-label']);
    });
}

function updateCSSClassLabels() {
    // 為CSS類名添加翻譯標籤
    const cssClassTranslations = {
        'leaflet-marker-icon': translations[currentLanguage]['leaflet-marker-icon'],
        'custom-div-icon': translations[currentLanguage]['custom-div-icon'],
        'leaflet-zoom-animated': translations[currentLanguage]['leaflet-zoom-animated'],
        'leaflet-interactive': translations[currentLanguage]['leaflet-interactive'],
        'village-label': translations[currentLanguage]['village-label']
    };
    
    // 更新所有相關元素的aria-label
    Object.keys(cssClassTranslations).forEach(className => {
        const elements = document.querySelectorAll(`.${className}`);
        elements.forEach(element => {
            element.setAttribute('aria-label', cssClassTranslations[className]);
        });
    });
    
    // 更新district-list的aria-label
    const districtList = document.getElementById('district-list');
    if (districtList) {
        districtList.setAttribute('aria-label', translations[currentLanguage]['district-list']);
    }
    
    // 更新所有地圖標記的aria-label
    const mapMarkers = document.querySelectorAll('.leaflet-marker-icon');
    mapMarkers.forEach(marker => {
        marker.setAttribute('aria-label', translations[currentLanguage]['leaflet-marker-icon']);
    });
    
    // 更新所有自定義圖標的aria-label
    const customIcons = document.querySelectorAll('.custom-div-icon');
    customIcons.forEach(icon => {
        icon.setAttribute('aria-label', translations[currentLanguage]['custom-div-icon']);
    });
    
    // 更新所有村里標籤的aria-label
    const villageLabels = document.querySelectorAll('.village-label');
    villageLabels.forEach(label => {
        label.setAttribute('aria-label', translations[currentLanguage]['village-label']);
    });
}

function updateMapLabels() {
    // 更新地圖上的標籤文字
    if (window.districtLabels) {
        window.districtLabels.forEach(label => {
            const districtName = label.getLatLng().districtName;
            const villageName = label.getLatLng().villageName;
            const bucketCount = label.getLatLng().bucketCount;
            
            let displayText;
            if (currentLanguage === 'en') {
                displayText = `${districtName} Dist.<br/>${villageName}<br/>${bucketCount} Buckets`;
            } else {
                displayText = `${districtName}區<br/>${villageName}<br/>${bucketCount}個桶`;
            }
            
            label.setContent(displayText);
        });
    }
    
    // 更新所有地圖標記的aria-label
    const mapMarkers = document.querySelectorAll('.leaflet-marker-icon');
    mapMarkers.forEach(marker => {
        marker.setAttribute('aria-label', translations[currentLanguage]['leaflet-marker-icon']);
    });
    
    // 更新所有自定義圖標的aria-label
    const customIcons = document.querySelectorAll('.custom-div-icon');
    customIcons.forEach(icon => {
        icon.setAttribute('aria-label', translations[currentLanguage]['custom-div-icon']);
    });
    
    // 更新所有村里標籤的aria-label
    const villageLabels = document.querySelectorAll('.village-label');
    villageLabels.forEach(label => {
        label.setAttribute('aria-label', translations[currentLanguage]['village-label']);
    });
}

function updateAllPopupContent() {
    // 更新所有現有標記的彈出窗口內容
    if (window.districtLayer) {
        window.districtLayer.eachLayer(function(layer) {
            if (layer.feature && layer.feature.properties && layer.feature.properties.name) {
                const districtName = layer.feature.properties.name;
                const isZhTw = currentLanguage === 'zh';
                const popupContent = `<strong>${districtName}${isZhTw ? '區' : ' Dist.'}</strong>`;
                layer.setPopupContent(popupContent);
            }
        });
    }
    
    if (window.villageLayer) {
        window.villageLayer.eachLayer(function(layer) {
            if (layer.feature && layer.feature.properties) {
                const props = layer.feature.properties;
                const isZhTw = currentLanguage === 'zh';
                let popupContent = '<div style="font-family: Arial, sans-serif; min-width: 200px;">';
                popupContent += '<h4 style="margin: 0 0 10px 0; color: #1f78b4;">' + props.full_name + '</h4>';
                popupContent += '<table style="width: 100%; font-size: 13px;">';
                popupContent += '<tr><td><strong>' + (isZhTw ? '區域:' : 'District:') + '</strong></td><td>' + props.district_name + '</td></tr>';
                popupContent += '<tr><td><strong>' + (isZhTw ? '村里:' : 'Village:') + '</strong></td><td>' + props.village_name + '</td></tr>';
                popupContent += '<tr><td><strong>' + (isZhTw ? '預測病例:' : 'Predicted Cases:') + '</strong></td><td><span style="color: #e74c3c; font-weight: bold;">' + (props.pred_cases || 0) + ' ' + (isZhTw ? '例' : 'Cases') + '</span></td></tr>';
                popupContent += '<tr><td><strong>' + (isZhTw ? '區域人口:' : 'District Population:') + '</strong></td><td>' + (props.district_population || 0).toLocaleString() + (isZhTw ? ' 人' : ' people') + '</td></tr>';
                popupContent += '<tr><td><strong>' + (isZhTw ? '區域戶數:' : 'District Households:') + '</strong></td><td>' + (props.district_households || 0).toLocaleString() + (isZhTw ? ' 戶' : ' households') + '</td></tr>';
                popupContent += '</table></div>';
                layer.setPopupContent(popupContent);
            }
        });
    }
    
    // 更新所有地圖標記的aria-label
    const mapMarkers = document.querySelectorAll('.leaflet-marker-icon');
    mapMarkers.forEach(marker => {
        marker.setAttribute('aria-label', translations[currentLanguage]['leaflet-marker-icon']);
    });
    
    // 更新所有自定義圖標的aria-label
    const customIcons = document.querySelectorAll('.custom-div-icon');
    customIcons.forEach(icon => {
        icon.setAttribute('aria-label', translations[currentLanguage]['custom-div-icon']);
    });
    
    // 更新所有村里標籤的aria-label
    const villageLabels = document.querySelectorAll('.village-label');
    villageLabels.forEach(label => {
        label.setAttribute('aria-label', translations[currentLanguage]['village-label']);
    });
}

// 重寫全局的switchLanguage函數
window.switchLanguage = function(lang) {
    console.log('切換語言至:', lang);
    
    // 更新全局語言變量
    currentLanguage = lang;
    window.currentLanguage = lang;
    
    // 更新語言切換按鈕狀態
    document.querySelectorAll('.lang-option').forEach(option => {
        option.classList.remove('active');
    });
    document.querySelector(`[data-lang="${lang}"]`).classList.add('active');
    
    // 重新生成整個頁面，帶語言參數
    window.location.href = '/?lang=' + lang;
    
    console.log('語言切換完成，頁面重新載入:', lang);
};

// 重新生成地圖標籤的函數
function regenerateMapLabels() {
    console.log('重新生成地圖標籤...');
    
    // 查找地圖實例
    var map = null;
    for (var prop in window) {
        if (prop.startsWith('map_') && window[prop] && typeof window[prop].removeLayer === 'function') {
            map = window[prop];
            break;
        }
    }
    
    if (!map) {
        console.error('找不到地圖對象');
        return;
    }
    
    // 清除所有現有的標籤
    map.eachLayer(function(layer) {
        if (layer.options && layer.options.icon && layer.options.icon.options && layer.options.icon.options.className === 'custom-div-icon') {
            map.removeLayer(layer);
        }
    });
    
    // 重新添加標籤
    if (typeof window.districtLabels !== 'undefined') {
        window.districtLabels.forEach(function(label, index) {
            var displayName = label.name;
            if (currentLanguage === 'zh') {
                displayName = label.name + '區';
            } else {
                displayName = label.name + ' Dist.';
            }
            
            var divIcon = L.divIcon({
                html: '<div class="district-label" style="background: rgba(255, 255, 255, 0.9); border: 1px solid #1f78b4; border-radius: 4px; padding: 2px 6px; font-size: 12px; font-weight: bold; color: #1f78b4; text-align: center; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.2); pointer-events: none; user-select: none;" title="' + (label.full_name || label.name) + '" aria-label="' + (currentLanguage === 'zh' ? '地圖標記圖標' : 'Map Marker Icon') + '" data-zh="地圖標記圖標" data-en="Map Marker Icon">' + displayName + '</div>',
                className: 'custom-div-icon',
                iconSize: [50, 18],
                iconAnchor: [25, 9]
            });
            
            var marker = L.marker([label.lat, label.lon], {
                icon: divIcon,
                zIndexOffset: 1000
            }).addTo(map);
        });
    }
    
    console.log('地圖標籤重新生成完成！');
}

// 重新生成村里標籤的函數
function regenerateVillageLabels() {
    console.log('重新生成村里標籤...');
    
    // 如果當前有村里圖層，重新生成標籤
    if (window.villageLabelsLayer && window.villageData) {
        // 清除現有標籤
        window.villageLabelsLayer.clearLayers();
        
        // 重新添加標籤
        window.villageData.features.forEach(function(feature) {
            var props = feature.properties;
            var center = turf.centroid(feature);
            
            var label = L.marker([center.geometry.coordinates[1], center.geometry.coordinates[0]], {
                icon: L.divIcon({
                    className: 'village-label',
                    html: '<div style="background: rgba(255, 255, 255, 0.9); border: 1px solid #1f78b4; border-radius: 4px; padding: 2px 6px; font-size: 12px; font-weight: 600; color: #1f78b4; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.3);" aria-label="' + (currentLanguage === 'zh' ? '村里標籤' : 'Village Label') + '" data-zh="村里標籤" data-en="Village Label">' + props.village_name + '</div>',
                    iconSize: [60, 20],
                    iconAnchor: [30, 10]
                })
            });
            
            window.villageLabelsLayer.addLayer(label);
        });
        
        console.log('村里標籤重新生成完成！');
    }
}

function updateCurrentWeek() {
    const weekElement = document.getElementById('current-week');
    if (weekElement && window.forecastData && window.forecastData.latest_week) {
        weekElement.textContent = window.forecastData.latest_week;
    } else if (weekElement) {
        weekElement.textContent = getTranslatedText('載入中...');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== 簡化版script.js已載入 ===');
    
    // 設置語言切換按鈕的初始狀態
    var urlParams = new URLSearchParams(window.location.search);
    var currentLang = urlParams.get('lang') || 'zh';
    
    // 設置按鈕狀態
    document.querySelectorAll('.lang-option').forEach(option => {
        option.classList.remove('active');
    });
    document.querySelector(`[data-lang="${currentLang}"]`).classList.add('active');
    
    // 從全局變量獲取預測資料
    if (typeof window.forecastData === 'undefined') {
        console.error('forecastData 全局變量未找到');
        return;
    }
    
    // 將全局 forecastData 轉換為列表格式
    var forecastDataList = [];
    if (window.forecastData && window.forecastData.district_data) {
        var districts = Object.values(window.forecastData.district_data);
        // 按預測病例排序
        districts.sort(function(a, b) {
            return b.total_pred_cases - a.total_pred_cases;
        });
        
        // 轉換為列表格式
        forecastDataList = districts.map(function(district, index) {
            return {
                name: district.district_name,
                pred_cases: district.total_pred_cases,
                rank: index + 1,
                color: index < 3 ? (index === 0 ? 'purple' : index === 1 ? 'red' : 'yellow') : 'normal',
                week_start: window.forecastData.latest_week
            };
        });
    }
    
    console.log('處理後的預測資料:', forecastDataList.slice(0, 5));

    // 區域名稱列表（按嚴重程度排序）
    var districtNames = forecastDataList.map(item => item.name);
    
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
    
    // 清除村里圖層和標籤
    function clearVillageDisplay() {
        console.log('清除村里顯示...');
        
        // 查找地圖實例
        var map = null;
        for (var prop in window) {
            if (prop.startsWith('map_') && window[prop] && typeof window[prop].removeLayer === 'function') {
                map = window[prop];
                break;
            }
        }
        
        if (map) {
            // 清除村里圖層
            if (typeof villageLayer !== 'undefined' && villageLayer) {
                map.removeLayer(villageLayer);
                villageLayer = null;
                console.log('村里圖層已清除');
            }
            
            // 清除村里標籤圖層
            if (window.villageLabelsLayer) {
                map.removeLayer(window.villageLabelsLayer);
                window.villageLabelsLayer = null;
                console.log('村里標籤已清除');
            }
        }
    }
    
    // 重置村里高亮樣式
    function resetVillageStyles() {
        // 重置村里圖層樣式
        if (typeof villageLayer !== 'undefined' && villageLayer && typeof villageLayer.eachLayer === 'function') {
            villageLayer.eachLayer(function(layer) {
                layer.setStyle({
                    color: '#1f78b4',
                    weight: 2,
                    fillColor: '#1f78b4',
                    fillOpacity: 0.1,
                    opacity: 1
                });
            });
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
    
    // 顯示區域詳細資訊的通用函數
    function showDistrictInfo(districtName, isFromMap) {
        console.log('顯示區域資訊:', districtName, '來源:', isFromMap ? '地圖' : '導覽列');
        
        // 如果不是從地圖點擊，則處理導覽列樣式
        if (!isFromMap) {
            // 移除所有active樣式
            var allItems = document.querySelectorAll('.district-item');
            allItems.forEach(function(activeItem) {
                activeItem.style.backgroundColor = '';
                activeItem.style.borderLeft = '';
            });
            
            // 為當前點擊的地區添加active樣式
            var clickedItem = document.querySelector('[data-district-name="' + districtName + '"]');
            if (clickedItem) {
                clickedItem.style.backgroundColor = '#e1f5fe';
                clickedItem.style.borderLeft = '4px solid #2196F3';
            }
        }
        
        // 高亮地圖區域
        highlightMapDistrict(districtName);
        
        // 顯示詳細資料
        var infoPanel = document.getElementById('info-panel');
        var title = document.getElementById('district-title');
        var population = document.getElementById('population');
        var dengueCases = document.getElementById('dengue-cases');
        var ratePer10k = document.getElementById('rate-per-10k');
        var riskLevel = document.getElementById('risk-level');
        var lastUpdate = document.getElementById('last-update');
        var detailData = document.getElementById('detail-data');
        
        if (title) title.textContent = districtName;
        
        // 查找預測資料
        var forecast = forecastDataList.find(item => item.name === districtName);
        if (forecast) {
            // 顯示人口資料
            var popData = populationData && populationData[districtName];
            if (population) {
                if (popData) {
                    population.textContent = popData.population.toLocaleString() + (currentLanguage === 'zh' ? ' 人' : ' people');
                } else {
                    population.textContent = '-';
                }
            }
            
            if (dengueCases) dengueCases.textContent = forecast.pred_cases + ' ' + getTranslatedText('病例');
            
            // 計算每萬人病例率
            if (ratePer10k) {
                if (popData && popData.population > 0) {
                    var rate = (forecast.pred_cases / popData.population) * 10000;
                    ratePer10k.textContent = rate.toFixed(2) + (currentLanguage === 'zh' ? ' /萬人' : ' /10k people');
                } else {
                    ratePer10k.textContent = '-';
                }
            }
            
            if (riskLevel) {
                var riskText = '';
                if (forecast.pred_cases >= 1000) riskText = getTranslatedText('極高風險');
                else if (forecast.pred_cases >= 100) riskText = getTranslatedText('高風險');
                else if (forecast.pred_cases >= 10) riskText = getTranslatedText('中風險');
                else riskText = getTranslatedText('低風險');
                riskLevel.textContent = riskText;
            }
            
            if (lastUpdate) lastUpdate.textContent = forecast.week_start;
        }
        
        if (infoPanel) {
            infoPanel.style.display = 'block';
            console.log('選中地區：', districtName);
        }
    }
    
    // 處理左側導覽列點擊（只顯示詳細資訊，不進入村里視圖）
    function handleDistrictClick(item) {
        // 從 data 屬性獲取區域名稱
        var districtName = item.getAttribute('data-district-name');
        console.log('點擊的區域:', districtName);
        
        // 只顯示詳細資訊，不進入村里視圖
        showDistrictInfo(districtName, true);
    }
    
    // 處理地圖區域點擊（只顯示詳細資訊，不進入村里視圖）
    function handleMapDistrictClick(districtName) {
        console.log('地圖點擊區域:', districtName);
        showDistrictInfo(districtName, true);
    }
    
    // 生成左側導覽列（按嚴重程度排序）
    function generateDistrictList() {
        var districtListDiv = document.getElementById('district-list');
        if (!districtListDiv) return;
        
        // 清空現有內容
        districtListDiv.innerHTML = '';
        
        // 為每個區域創建列表項
        forecastDataList.forEach(function(data, index) {
            var districtItem = document.createElement('div');
            districtItem.className = 'district-item';
            
            // 根據排名設定顏色
            var itemStyle = 'padding: 10px 15px; cursor: pointer; border-bottom: 1px solid #e0e0e0; transition: background-color 0.2s; position: relative; font-size: 16px;';
            
            if (data.rank <= 3) {
                if (data.rank === 1) {
                    itemStyle += 'background: linear-gradient(90deg, rgba(128, 0, 128, 0.1) 0%, transparent 100%); border-left: 4px solid purple;';
                } else if (data.rank === 2) {
                    itemStyle += 'background: linear-gradient(90deg, rgba(255, 0, 0, 0.1) 0%, transparent 100%); border-left: 4px solid red;';
                } else if (data.rank === 3) {
                    itemStyle += 'background: linear-gradient(90deg, rgba(255, 255, 0, 0.2) 0%, transparent 100%); border-left: 4px solid orange;';
                }
            }
            
            districtItem.style.cssText = itemStyle;
            
            // 創建內容 HTML（支持語言切換）
            var contentHtml = '';
            if (data.rank <= 3) {
                contentHtml += '<span style="font-weight: bold; font-size: 16px;">#' + data.rank + '</span> ';
            }
            contentHtml += '<span style="font-weight: 600;">' + data.name + '</span>';
            if (data.pred_cases > 0) {
                contentHtml += '<br><span style="font-size: 14px; color: #666;">' + getTranslatedText('預測病例') + ': ' + data.pred_cases + '</span>';
            }
            
            districtItem.innerHTML = contentHtml;
            
            // 儲存區域名稱到 data 屬性
            districtItem.setAttribute('data-district-name', data.name);
            
            // 鼠標懸停效果
            districtItem.addEventListener('mouseenter', function() {
                if (data.rank > 3) {
                    this.style.backgroundColor = '#f0f0f0';
                }
            });
            
            districtItem.addEventListener('mouseleave', function() {
                if (data.rank > 3) {
                    this.style.backgroundColor = 'transparent';
                }
            });
            
            // 點擊事件
            districtItem.addEventListener('click', function() {
                handleDistrictClick(this);
            });
            
            districtListDiv.appendChild(districtItem);
        });
        
        console.log('區域列表生成完成，共', forecastDataList.length, '個區域');
    }
    
    // 生成導覽列
    generateDistrictList();
    
    // 初始化週次顯示
    updateCurrentWeek();
    
    // 初始化CSS類名標籤
    updateCSSClassLabels();
    
    // 綁定左側導覽列點擊事件（備用）
    setTimeout(function() {
        var districtItems = document.querySelectorAll('.district-item');
        districtItems.forEach(function(item) {
            item.addEventListener('click', function() {
                handleDistrictClick(item);
            });
        });
    }, 100);
    
    // 綁定關閉按鈕事件
    var closeButton = document.getElementById('close-panel');
    var infoPanel = document.getElementById('info-panel');
    
    if (closeButton && infoPanel) {
        closeButton.addEventListener('click', function() {
            infoPanel.style.display = 'none';
            
            // 重置所有導覽列樣式
            var allItems = document.querySelectorAll('.district-item');
            allItems.forEach(function(item) {
                item.style.backgroundColor = '';
                item.style.borderLeft = '';
            });
            
            // 重置地圖樣式
            resetMapDistrictStyles();
            
            // 清除村里圖層和標籤
            clearVillageDisplay();
            
            // 重置村里高亮樣式
            resetVillageStyles();
        });
    }
    
    console.log('簡化版功能已初始化完成');
});