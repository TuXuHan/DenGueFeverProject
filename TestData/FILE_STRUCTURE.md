# 檔案結構說明

## 主要報告檔案
- **`temporal_analysis_report.html`** - 整合的HTML分析報告（主要查看檔案）
- **`ANALYSIS_SUMMARY.md`** - 分析總結報告

## 核心數據檔案
- **`temporal_features.csv`** - 時序特徵表（37區×99特徵）
- **`clustering_results.csv`** - 分群結果
- **`descriptive_statistics.csv`** - 描述性統計

## 重要圖表檔案
### 相關性分析
- **`correlation_heatmap.png`** - 相關性熱力圖

### 時序視覺化
- **`comprehensive_temporal.png`** - 綜合時序圖
- **`temporal_確診數.png`** - 確診數時序圖
- **`temporal_ovum_sum.png`** - 誘卵桶時序圖
- **`temporal_週平均氣溫℃_x.png`** - 氣溫時序圖
- **`temporal_週平均氣溫℃_y.png`** - 氣溫時序圖（測站2）
- **`temporal_週總降水量mm_x.png`** - 降水量時序圖
- **`temporal_週總降水量mm_y.png`** - 降水量時序圖（測站2）

### 分群分析
- **`kmeans_parameter_selection.png`** - KMeans參數選擇圖
- **`kmeans_clustering_pca.png`** - KMeans分群結果
- **`hierarchical_clustering_dendrogram.png`** - 層次分群樹狀圖

## 分析結論檔案
- **`temporal_analysis_insights.txt`** - 實務建議與結論
- **`technical_details.txt`** - 技術細節與參數

## 其他檔案
- **`enhanced_interactive_map.html`** - 互動式地圖
- **`README.md`** - 專案說明
- **`requirements.txt`** - Python依賴套件

## 已歸檔檔案
- **`archive/`** 資料夾包含：
  - 分析腳本（temporal_analysis.py, complete_analysis.py）
  - 相似性分析相關檔案
  - 舊版分析結果

## 使用建議
1. **主要查看**: `temporal_analysis_report.html` - 包含完整分析結果
2. **數據分析**: 使用CSV檔案進行進一步分析
3. **圖表展示**: PNG檔案可用於報告和簡報
4. **技術參考**: TXT檔案包含技術細節
