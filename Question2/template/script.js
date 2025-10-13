// 簡化版本的script.js - 只保留核心功能

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== 簡化版script.js已載入 ===');
    
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
            
            // 創建內容 HTML
            var contentHtml = '';
            if (data.rank <= 3) {
                contentHtml += '<span style="font-weight: bold; font-size: 16px;">#' + data.rank + '</span> ';
            }
            contentHtml += '<span style="font-weight: 600;">' + data.name + '</span>';
            if (data.pred_cases > 0) {
                contentHtml += '<br><span style="font-size: 14px; color: #666;">預測病例: ' + data.pred_cases + '</span>';
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
            
            // 清除村里圖層和標籤
            clearVillageDisplay();
            
            // 重置村里高亮樣式
            resetVillageStyles();
        });
    }
    
    console.log('簡化版功能已初始化完成');
});