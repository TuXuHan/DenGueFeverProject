# 多語言功能使用指南 / Multilingual Feature Guide

## 中文說明

### 🌐 功能概述
本專案已為 Question1 和 Question2 的網頁添加了完整的中英文雙語支援功能，用戶可以隨時切換語言介面。

### 🎯 主要特色
- **雙語支援**：完整支援中文和英文兩種語言
- **智能縮寫**：英文模式下，行政區自動縮寫為 "Dist."
- **即時切換**：無需重新載入頁面即可切換語言
- **響應式設計**：語言切換開關適配各種設備

### 🔧 使用方法
1. 打開 Question1 或 Question2 的網頁
2. 在右上角找到語言切換開關
3. 點擊 "中文" 或 "English" 按鈕即可切換語言
4. 所有介面元素會即時更新為選定語言

### 📋 翻譯內容
- **標題**：台南登革熱資料預測 ↔ Tainan Dengue Fever Data Prediction
- **控制項**：桶子位置 ↔ Bucket Locations
- **圖例**：卵數等級 ↔ Egg Count Level
- **行政區**：南區 ↔ South Dist.
- **統計**：桶數 ↔ Buckets

### 🚀 啟動方式
```bash
# 啟動 Question1
cd Question1
python main.py

# 啟動 Question2  
cd Question2
python main.py

# 查看功能展示頁面
open language_demo.html
```

---

## English Description

### 🌐 Feature Overview
This project has added complete Chinese-English bilingual support to both Question1 and Question2 web pages, allowing users to switch language interfaces at any time.

### 🎯 Key Features
- **Bilingual Support**: Complete support for both Chinese and English languages
- **Smart Abbreviation**: Administrative districts automatically abbreviated to "Dist." in English mode
- **Real-time Switch**: Switch languages without reloading the page
- **Responsive Design**: Language switch adapts to various devices

### 🔧 How to Use
1. Open Question1 or Question2 web page
2. Find the language switch in the top-right corner
3. Click "中文" or "English" button to switch language
4. All interface elements will update instantly to the selected language

### 📋 Translation Content
- **Title**: 台南登革熱資料預測 ↔ Tainan Dengue Fever Data Prediction
- **Controls**: 桶子位置 ↔ Bucket Locations
- **Legend**: 卵數等級 ↔ Egg Count Level
- **Districts**: 南區 ↔ South Dist.
- **Statistics**: 桶數 ↔ Buckets

### 🚀 Launch Instructions
```bash
# Launch Question1
cd Question1
python main.py

# Launch Question2
cd Question2
python main.py

# View feature demo page
open language_demo.html
```

---

## 🔧 技術實現 / Technical Implementation

### 前端實現 / Frontend Implementation
- 使用 JavaScript 實現即時語言切換
- CSS 樣式支援響應式設計
- HTML 元素添加 `data-zh` 和 `data-en` 屬性

### 核心功能 / Core Functions
```javascript
function switchLanguage(lang) {
    // 更新語言切換按鈕狀態
    // 更新所有可翻譯的元素
    // 重新渲染地圖標籤
}
```

### 翻譯對照表 / Translation Mapping
```javascript
const translations = {
    zh: { /* 中文翻譯 */ },
    en: { /* English translations */ }
};
```

---

## 📱 瀏覽器支援 / Browser Support
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 🎨 設計特色 / Design Features
- 漸層背景設計
- 圓角按鈕樣式
- 懸停動畫效果
- 陰影和光澤效果

---

*最後更新 / Last Updated: 2024年10月*
