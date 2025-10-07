// 簡化版本的script.js - 只保留核心功能

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== 簡化版script.js已載入 ===');
    
    // 預測資料（按嚴重程度排序）
    var forecastData = [
        {name: '新營區', pred_cases: 1160, rank: 1, color: 'purple', week_start: '2024-01-08'},
        {name: '仁德區', pred_cases: 298, rank: 2, color: 'red', week_start: '2024-01-08'},
        {name: '南化區', pred_cases: 189, rank: 3, color: 'yellow', week_start: '2024-01-08'},
        {name: '佳里區', pred_cases: 170, rank: 4, color: 'normal', week_start: '2024-01-08'},
        {name: '白河區', pred_cases: 48, rank: 5, color: 'normal', week_start: '2024-01-08'},
        {name: '東山區', pred_cases: 31, rank: 6, color: 'normal', week_start: '2024-01-08'},
        {name: '七股區', pred_cases: 23, rank: 7, color: 'normal', week_start: '2024-01-08'},
        {name: '楠西區', pred_cases: 7, rank: 8, color: 'normal', week_start: '2024-01-08'},
        {name: '大內區', pred_cases: 0, rank: 9, color: 'normal', week_start: '2024-01-01'},
        {name: '新化區', pred_cases: 0, rank: 10, color: 'normal', week_start: '2024-01-01'},
        {name: '北門區', pred_cases: 0, rank: 11, color: 'normal', week_start: '2024-01-01'},
        {name: '將軍區', pred_cases: 0, rank: 12, color: 'normal', week_start: '2024-01-01'},
        {name: '西港區', pred_cases: 0, rank: 13, color: 'normal', week_start: '2024-01-01'},
        {name: '學甲區', pred_cases: 0, rank: 14, color: 'normal', week_start: '2024-01-08'},
        {name: '下營區', pred_cases: 0, rank: 15, color: 'normal', week_start: '2024-01-01'},
        {name: '官田區', pred_cases: 0, rank: 16, color: 'normal', week_start: '2024-01-01'},
        {name: '六甲區', pred_cases: 0, rank: 17, color: 'normal', week_start: '2024-01-01'},
        {name: '新市區', pred_cases: 0, rank: 18, color: 'normal', week_start: '2024-01-01'},
        {name: '麻豆區', pred_cases: 0, rank: 19, color: 'normal', week_start: '2024-01-01'},
        {name: '後壁區', pred_cases: 0, rank: 20, color: 'normal', week_start: '2024-01-01'},
        {name: '柳營區', pred_cases: 0, rank: 21, color: 'normal', week_start: '2024-01-01'},
        {name: '鹽水區', pred_cases: 0, rank: 22, color: 'normal', week_start: '2024-01-01'},
        {name: '安平區', pred_cases: 0, rank: 23, color: 'normal', week_start: '2024-01-01'},
        {name: '安定區', pred_cases: 0, rank: 24, color: 'normal', week_start: '2024-01-01'},
        {name: '善化區', pred_cases: 0, rank: 25, color: 'normal', week_start: '2024-01-01'},
        {name: '玉井區', pred_cases: 0, rank: 26, color: 'normal', week_start: '2024-01-01'},
        {name: '安南區', pred_cases: 0, rank: 27, color: 'normal', week_start: '2024-01-01'},
        {name: '北區', pred_cases: 0, rank: 28, color: 'normal', week_start: '2024-01-01'},
        {name: '南區', pred_cases: 0, rank: 29, color: 'normal', week_start: '2024-01-01'},
        {name: '東區', pred_cases: 0, rank: 30, color: 'normal', week_start: '2024-01-01'},
        {name: '永康區', pred_cases: 0, rank: 31, color: 'normal', week_start: '2024-01-01'},
        {name: '山上區', pred_cases: 0, rank: 32, color: 'normal', week_start: '2024-01-01'},
        {name: '龍崎區', pred_cases: 0, rank: 33, color: 'normal', week_start: '2024-01-01'},
        {name: '關廟區', pred_cases: 0, rank: 34, color: 'normal', week_start: '2024-01-01'},
        {name: '歸仁區', pred_cases: 0, rank: 35, color: 'normal', week_start: '2024-01-01'},
        {name: '左鎮區', pred_cases: 0, rank: 36, color: 'normal', week_start: '2024-01-01'},
        {name: '中西區', pred_cases: 0, rank: 37, color: 'normal', week_start: '2024-01-01'}
    ];

    // 區域名稱列表（按嚴重程度排序）
    var districtNames = forecastData.map(item => item.name);
    
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
        var forecast = forecastData.find(item => item.name === districtName);
        if (forecast) {
            // 顯示人口資料
            var popData = populationData && populationData[districtName];
            if (population) {
                if (popData) {
                    population.textContent = popData.population.toLocaleString() + ' 人';
                } else {
                    population.textContent = '-';
                }
            }
            
            if (dengueCases) dengueCases.textContent = forecast.pred_cases + ' 病例';
            
            // 計算每萬人病例率
            if (ratePer10k) {
                if (popData && popData.population > 0) {
                    var rate = (forecast.pred_cases / popData.population) * 10000;
                    ratePer10k.textContent = rate.toFixed(2) + ' /萬人';
                } else {
                    ratePer10k.textContent = '-';
                }
            }
            
            if (riskLevel) {
                var riskText = '';
                if (forecast.pred_cases >= 1000) riskText = '極高風險';
                else if (forecast.pred_cases >= 100) riskText = '高風險';
                else if (forecast.pred_cases >= 10) riskText = '中風險';
                else riskText = '低風險';
                riskLevel.textContent = riskText;
            }
            
            if (lastUpdate) lastUpdate.textContent = forecast.week_start;
        }
        
        if (infoPanel) {
            infoPanel.style.display = 'block';
            console.log('選中地區：', districtName);
        }
    }
    
    // 處理左側導覽列點擊
    function handleDistrictClick(item) {
        // 從 data 屬性獲取區域名稱
        var districtName = item.getAttribute('data-district-name');
        console.log('點擊的區域:', districtName);
        showDistrictInfo(districtName, false);
    }
    
    // 處理地圖區域點擊
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
        forecastData.forEach(function(data, index) {
            var districtItem = document.createElement('div');
            districtItem.className = 'district-item';
            
            // 根據排名設定顏色
            var itemStyle = 'padding: 10px 15px; cursor: pointer; border-bottom: 1px solid #e0e0e0; transition: background-color 0.2s; position: relative;';
            
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
            
            // 創建內容 HTML
            var contentHtml = '';
            if (data.rank <= 3) {
                contentHtml += '<span style="font-weight: bold; font-size: 14px;">#' + data.rank + '</span> ';
            }
            contentHtml += '<span style="font-weight: 600;">' + data.name + '</span>';
            if (data.pred_cases > 0) {
                contentHtml += '<br><span style="font-size: 12px; color: #666;">預測病例: ' + data.pred_cases + '</span>';
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
        
        console.log('區域列表生成完成，共', forecastData.length, '個區域');
    }
    
    // 生成導覽列
    generateDistrictList();
    
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
        });
    }
    
    console.log('簡化版功能已初始化完成');
});