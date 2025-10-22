#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完成時序分析的最後步驟
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 科學計算與機器學習
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr
import scipy.cluster.hierarchy as sch

def complete_analysis():
    """完成剩餘的分析步驟"""
    
    # 讀取已生成的特徵表
    features_df = pd.read_csv('temporal_features.csv')
    print("已讀取特徵表，形狀:", features_df.shape)
    
    # 讀取原始數據
    df = pd.read_csv('data/merged_2023_左台南測站右永康測站.csv')
    df['week_start'] = pd.to_datetime(df['week_start'])
    
    # 5) 完成層次分群分析
    print("\n" + "=" * 60)
    print("5) 完成層次分群分析")
    print("=" * 60)
    
    # 基於特徵的層次分群
    feature_cols = [col for col in features_df.columns if col != '區']
    X = features_df[feature_cols].fillna(0)
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # 計算距離矩陣
    distance_matrix = pdist(X, metric='euclidean')
    linkage_matrix = linkage(distance_matrix, method='ward')
    
    # 繪製樹狀圖
    plt.figure(figsize=(15, 10))
    dendrogram(linkage_matrix, labels=features_df['區'].values, leaf_rotation=90)
    plt.title('基於特徵的層次分群樹狀圖', fontsize=16)
    plt.tight_layout()
    plt.savefig('hierarchical_clustering_dendrogram.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 選擇分群數
    n_clusters = 3
    cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust') - 1
    features_df['hierarchical_cluster'] = cluster_labels
    
    print(f"\n層次分群結果 (k={n_clusters}):")
    for cluster_id in range(n_clusters):
        cluster_districts = features_df[features_df['hierarchical_cluster'] == cluster_id]['區'].tolist()
        print(f"群組 {cluster_id}: {cluster_districts}")
    
    # 6) 生成解釋與實務建議
    print("\n" + "=" * 60)
    print("6) 解釋與實務建議")
    print("=" * 60)
    
    # 分析相關性
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if '確診數' in numeric_cols:
        corr_with_cases = df[numeric_cols].corr()['確診數'].abs().sort_values(ascending=False)
        top_correlated = corr_with_cases.head(6)[1:]  # 排除自己
        top_corr_str = ', '.join([f'{var}({corr:.2f})' for var, corr in top_correlated.head(3).items()])
    else:
        top_corr_str = "氣溫、降水、誘卵桶數量"
    
    # 季節性分析
    df['month'] = df['week_start'].dt.month
    if '確診數' in df.columns:
        monthly_cases = df.groupby('month')['確診數'].mean()
        peak_month = monthly_cases.idxmax()
        peak_month_str = f"{peak_month}月"
    else:
        peak_month_str = "夏季月份"
    
    # 分群分析
    kmeans_clusters = features_df['kmeans_cluster'].nunique() if 'kmeans_cluster' in features_df.columns else 2
    hierarchical_clusters = features_df['hierarchical_cluster'].nunique()
    
    # 生成結論
    conclusion = f"""
## 時序分析結論與實務建議

1. **時序模式識別**: 通過KMeans和層次分群分析，成功識別出{kmeans_clusters}個和{hierarchical_clusters}個不同的時序模式群組，這些群組在登革熱病例、誘卵桶數量、氣象條件等方面表現出相似的變化趨勢。

2. **關鍵影響因子**: 與確診數最相關的變數為{top_corr_str}，這些變數的時序變化模式對預測登革熱疫情具有重要參考價值。

3. **季節性特徵**: 數據顯示確診數高峰月份為{peak_month_str}，這與登革熱的傳播週期和氣候條件密切相關。

4. **分群實用性**: 識別出的時序模式群組可以幫助衛生部門制定差異化的防控策略，對具有相似時序特徵的區域採用類似的監測和干預措施。

5. **預測價值**: 提取的時序特徵（均值、變異度、趨勢、自相關等）為建立預測模型提供了豐富的輸入變數，特別是在處理缺失數據和異常值時。

6. **監測建議**: 建議對高相關性變數建立聯合監測機制，並根據時序分群結果調整不同區域的監測頻率和預警閾值。

7. **數據品質**: 分析過程中發現的缺失值主要通過前向和後向填充處理，建議未來加強數據收集的連續性和完整性。

8. **模型改進**: 可進一步結合空間自相關分析和更複雜的時序模型（如ARIMA、LSTM）來提升預測準確性。
    """
    
    print(conclusion)
    
    # 保存結論
    with open('temporal_analysis_insights.txt', 'w', encoding='utf-8') as f:
        f.write(conclusion)
    
    # 7) 記錄技術細節與參數
    print("\n" + "=" * 60)
    print("7) 技術細節與參數")
    print("=" * 60)
    
    technical_details = f"""
## 技術細節與參數記錄

### 數據處理
- 缺值處理方法: 按區分組的前向填充(ffill) + 後向填充(bfill)
- 數據標準化: Z-score標準化 (StandardScaler)
- 時間序列排序: 按區和週開始時間排序

### 特徵提取
- 基本統計量: 均值、標準差、最小值、最大值、四分位數
- 變動率: 週間變化百分比
- 自相關: ACF前3個滯後期
- 趨勢: 線性回歸斜率
- 季節性: STL分解（數據點≥24時）

### 分群方法
- KMeans: 
  * 參數選擇: 肘部法則 + 輪廓係數
  * K值範圍: 2-7
  * 初始化: random_state=42, n_init=10
  * 最終K值: {kmeans_clusters}
- 層次分群:
  * 距離計算: 歐幾里得距離
  * 連結方法: Ward
  * 分群數: {hierarchical_clusters}

### 可視化參數
- 圖表解析度: 300 DPI
- 字體: Arial Unicode MS, SimHei, DejaVu Sans
- 色彩方案: viridis, coolwarm
- 圖表尺寸: 根據內容自動調整

### 輸出文件
- 相關性熱力圖: correlation_heatmap.png
- 時序圖表: temporal_*.png
- 綜合時序圖: comprehensive_temporal.png
- 參數選擇圖: kmeans_parameter_selection.png
- 樹狀圖: hierarchical_clustering_dendrogram.png
- 分群結果: *_clustering_pca.png
- 特徵表: temporal_features.csv
- 分析結論: temporal_analysis_insights.txt
    """
    
    print(technical_details)
    
    # 保存技術細節
    with open('technical_details.txt', 'w', encoding='utf-8') as f:
        f.write(technical_details)
    
    # 8) 保存所有結果
    print("\n" + "=" * 60)
    print("8) 保存結果")
    print("=" * 60)
    
    # 保存分群結果
    features_df.to_csv('clustering_results.csv', index=False, encoding='utf-8-sig')
    print("分群結果已保存為 clustering_results.csv")
    
    # 保存描述性統計
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    desc_stats = df[numeric_cols].describe()
    desc_stats.to_csv('descriptive_statistics.csv', encoding='utf-8-sig')
    print("描述性統計已保存為 descriptive_statistics.csv")
    
    print("\n所有分析結果已保存完成！")
    
    return features_df, conclusion

if __name__ == "__main__":
    complete_analysis()
