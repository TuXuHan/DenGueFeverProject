# 指定七個區域的村里層級相似度分析

## 專案概述

本專案針對台南市7個核心行政區（中西區、仁德區、北區、南區、安平區、東區、永康區）的**村里層級**進行了深入的相似度分析，基於TestData/ANALYSIS_SUMMARY.md的分析方法，專注於誘卵桶數量的時序數據分析。

## 檔案結構

```
cityside/
├── README.md                             # 本文件
├── COMPLETE_EXPERIMENT_REPORT.md        # 完整實驗報告（主要）
├── VILLAGE_ANALYSIS_SUMMARY.md          # 村里分析總結
├── ANALYSIS_SUMMARY.md                  # 行政區分析總結
├── FIXED_IMPUTATION_REPORT.md           # 修正版補值實驗報告
├── IMPUTATION_EXPERIMENT_REPORT.md      # 補值實驗報告
├── EXPERIMENT_SUMMARY.md                # 實驗總結
├── village_level_analysis_report.md     # 村里詳細分析報告
├── village_similarity_analysis_report.md # 行政區詳細分析報告
├── village_temporal_features.csv        # 村里時序特徵表（主要）
├── village_feature_similarities.csv     # 村里特徵相似度矩陣（主要）
├── village_temporal_similarities.csv    # 村里時序相似度矩陣（主要）
├── village_combined_similarities.csv    # 村里綜合相似度矩陣（主要）
├── village_clustering_results.csv       # 村里分群結果（主要）
├── village_district_statistics.csv      # 各區域統計摘要（主要）
├── clustering_results.csv               # 行政區分群結果
├── combined_similarities.csv            # 行政區綜合相似度矩陣
├── feature_similarities.csv             # 行政區特徵相似度矩陣
├── temporal_similarities.csv            # 行政區時序相似度矩陣
├── temporal_features.csv                # 行政區時序特徵表
└── requirements.txt                     # 依賴套件
```

## 快速開始

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 查看分析結果

**主要分析報告:**
- `COMPLETE_EXPERIMENT_REPORT.md` - **完整實驗報告（推薦）**
- `VILLAGE_ANALYSIS_SUMMARY.md` - 村里層級分析總結
- `FIXED_IMPUTATION_REPORT.md` - 修正版補值實驗報告

**數據文件:**
- `village_temporal_features.csv` - 207個村里的23個時序特徵
- `village_combined_similarities.csv` - 村里綜合相似度矩陣
- `village_clustering_results.csv` - 村里分群結果

## 主要結果（村里層級分析）

### 分析規模
- **分析村里總數**: 207個
- **時間範圍**: 2023年1月-12月（51週）
- **特徵數量**: 23個時序特徵

### 相似度排名

**特徵相似度（前5名）:**
1. 南區-大林里 - 南區-開南里: 0.9580
2. 安平區-文平里 - 安平區-育平里: 0.9561
3. 南區-大成里 - 安平區-金城里: 0.9541
4. 南區-鯤鯓里 - 安平區-金城里: 0.9491
5. 東區-大智里 - 東區-關聖里: 0.9451

**時序相似度（前5名）:**
1. 北區-力行里 - 永康區-南灣里: 0.1189
2. 永康區-南灣里 - 永康區-永明里: 0.1006
3. 安平區-平通里 - 東區-崇文里: 0.0894
4. 安平區-文平里 - 永康區-南灣里: 0.0894
5. 安平區-文平里 - 東區-東智里: 0.0880

### 分群結果

**KMeans分群 (k=2):**
- 群組0: 141個村里（68.1%）
- 群組1: 66個村里（31.9%）

**層次分群 (k=3):**
- 群組0: 主要包含中西區、仁德區、安平區的村里
- 群組1: 主要包含北區、南區的村里
- 群組2: 主要包含東區、永康區的村里

## 數據說明

### 輸入數據
- `../data/merged_2023_左台南測站右永康測站.csv`: 主要數據文件
- `../data/bucket_statistics.csv`: 村里誘卵桶數據

### 輸出數據
- **特徵表**: 包含85個時序特徵
- **相似度矩陣**: 7×7的相似度矩陣
- **分群結果**: 各區域的分群標籤

## 分析方法

### 特徵提取
- 基本統計量（均值、標準差、四分位數等）
- 變動率統計（週間變化百分比）
- 自相關係數（ACF前3個滯後期）
- 趨勢斜率
- 氣象特徵

### 相似度計算
- **特徵相似度**: 餘弦相似度
- **時序相似度**: DTW（動態時間規整）
- **綜合相似度**: 加權平均（α=0.5）

### 分群方法
- **KMeans**: 使用肘部法則選擇最佳k值
- **層次分群**: Ward連結方法

## 實務應用

### 監測策略
- 根據相似度分析結果，對高相似度區域採用相似的監測策略
- 根據分群結果調整不同區域的監測頻率

### 防控措施
- 制定差異化防控策略
- 合理配置監測和防控資源

### 預測模型
- 使用提取的時序特徵作為預測模型輸入
- 考慮區域間的相似度關係

## 技術細節

### 數據處理
- 缺值處理：前向填充 + 後向填充
- 標準化：Z-score標準化
- 異常值處理：替換無窮大值為0

### 可視化參數
- 圖表解析度：300 DPI
- 字體：Arial Unicode MS, SimHei, DejaVu Sans
- 色彩方案：viridis

## 注意事項

1. 確保數據文件路徑正確
2. 安裝所有必要的依賴套件
3. 分析結果基於2023年數據
4. 相似度計算結果可能因參數調整而變化

## 聯絡資訊

如有問題或建議，請參考TestData/ANALYSIS_SUMMARY.md中的相關說明。
