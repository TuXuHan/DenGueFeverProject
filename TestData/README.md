# 登革熱時序分析專案

本專案針對台南市2023年登革熱數據進行全面的時序分析，包含特徵提取、相關性分析、時序視覺化和分群分析。

## 🎯 主要成果

### 📊 整合分析報告
- **`temporal_analysis_report.html`** - 完整的HTML分析報告（**主要查看檔案**）
- **`ANALYSIS_SUMMARY.md`** - 分析總結報告

### 📈 核心發現
- **關鍵影響因子**: 人口數(0.53)、噴藥次數(0.53)、誘卵桶數(0.44)與確診數最相關
- **季節性特徵**: 9月為確診高峰月份
- **分群結果**: 識別出核心區域與外圍區域的時序模式差異
- **數據規模**: 37個行政區，1,961行×38列的週度數據

## 🚀 快速開始

### 1. 查看分析結果
```bash
# 開啟主要報告（推薦）
open temporal_analysis_report.html

# 或查看總結報告
cat ANALYSIS_SUMMARY.md
```

### 2. 數據檔案
- **`temporal_features.csv`** - 時序特徵表（37區×99特徵）
- **`clustering_results.csv`** - 分群結果
- **`descriptive_statistics.csv`** - 描述性統計

## 📁 檔案結構

### 主要報告
- `temporal_analysis_report.html` - 整合HTML報告
- `ANALYSIS_SUMMARY.md` - 分析總結
- `FILE_STRUCTURE.md` - 檔案結構說明

### 重要圖表
- `correlation_heatmap.png` - 相關性熱力圖
- `comprehensive_temporal.png` - 綜合時序圖
- `temporal_確診數.png` - 確診數時序圖
- `kmeans_clustering_pca.png` - 分群結果
- `hierarchical_clustering_dendrogram.png` - 層次分群樹狀圖

### 分析結論
- `temporal_analysis_insights.txt` - 實務建議
- `technical_details.txt` - 技術細節

### 已歸檔
- `archive/` - 分析腳本和舊版結果

## 🔍 分析內容

### 1. 基本檢查與清理
- 數據品質檢查和缺值處理
- 時間序列排序和格式轉換

### 2. 描述性統計與相關性
- 數值欄位統計摘要
- 相關性矩陣和熱力圖
- 高相關性變數識別

### 3. 時序視覺化
- 主要指標時序圖
- 分區比較視覺化
- 綜合時序趨勢

### 4. 特徵提取
- 99個時序特徵（統計量、變動率、自相關、趨勢等）
- 季節性分解
- 特徵標準化

### 5. 分群分析
- KMeans分群（k=2）
- 層次分群（k=3）
- PCA可視化

### 6. 實務建議
- 監測策略建議
- 防控措施建議
- 預測模型建議

## 💡 主要發現

1. **時序模式識別**: 成功識別出不同行政區的時序模式群組
2. **關鍵影響因子**: 人口數、噴藥次數、誘卵桶數量是主要影響因子
3. **季節性特徵**: 9月為確診高峰，符合登革熱傳播週期
4. **分群實用性**: 核心區域與外圍區域需要差異化防控策略
5. **預測價值**: 豐富的時序特徵為預測模型提供基礎

## 🛠️ 技術實現

### 分析方法
- 時序特徵提取
- 相關性分析
- KMeans和層次分群
- PCA降維可視化

### 數據處理
- 前向/後向填充處理缺值
- Z-score標準化
- 異常值處理

### 視覺化
- 高解析度圖表（300 DPI）
- 響應式HTML報告
- 互動式導航

## 📋 使用建議

1. **主要查看**: `temporal_analysis_report.html` - 包含完整分析結果
2. **數據分析**: 使用CSV檔案進行進一步分析
3. **圖表展示**: PNG檔案可用於報告和簡報
4. **技術參考**: TXT檔案包含技術細節

## 🔧 技術要求

- Python 3.8+
- 主要套件: pandas, numpy, matplotlib, seaborn, scikit-learn, scipy, statsmodels

## 📝 更新日誌

- **v2.0** - 完整時序分析版本
- **v2.1** - 整合HTML報告
- **v2.2** - 檔案結構優化

## 📄 授權

本專案僅供學術研究使用。