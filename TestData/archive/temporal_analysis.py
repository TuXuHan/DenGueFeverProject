#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時序分析腳本：登革熱數據分析
包含基本檢查、描述性統計、時序視覺化、特徵提取、分群分析等
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
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr
import scipy.cluster.hierarchy as sch

# 時序分析
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf
from statsmodels.graphics.tsaplots import plot_acf

# 距離計算
try:
    from dtaidistance import dtw
    DTW_AVAILABLE = True
except ImportError:
    DTW_AVAILABLE = False
    print("警告: dtaidistance 未安裝，將使用歐幾里得距離替代 DTW")

class TemporalAnalyzer:
    def __init__(self, data_path, geojson_path=None):
        """初始化分析器"""
        self.data_path = data_path
        self.geojson_path = geojson_path
        self.df = None
        self.features_df = None
        self.cluster_results = {}
        
    def load_and_clean_data(self):
        """1) 基本檢查與清理"""
        print("=" * 60)
        print("1) 基本檢查與清理")
        print("=" * 60)
        
        # 讀取數據
        self.df = pd.read_csv(self.data_path)
        print(f"數據形狀: {self.df.shape}")
        print(f"列名: {list(self.df.columns)}")
        
        # 顯示前10列
        print("\n前10列數據:")
        print(self.df.head(10))
        
        # 數據型態
        print("\n數據型態:")
        print(self.df.dtypes)
        
        # 缺值檢查
        print("\n每欄缺值數:")
        missing_data = self.df.isnull().sum()
        print(missing_data[missing_data > 0])
        
        # 重複列檢查
        duplicates = self.df.duplicated().sum()
        print(f"\n重複列數: {duplicates}")
        
        # 轉換週欄為datetime
        if 'week_start' in self.df.columns:
            self.df['week_start'] = pd.to_datetime(self.df['week_start'])
            self.df = self.df.sort_values(['區', 'week_start'])
            print(f"\n週欄已轉換為datetime，數據已按區和時間排序")
        
        # 處理缺值 - 使用前向填充和後向填充
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if self.df[col].isnull().sum() > 0:
                # 按區分組進行填充
                self.df[col] = self.df.groupby('區')[col].fillna(method='ffill').fillna(method='bfill')
        
        print(f"\n缺值處理完成，剩餘缺值數: {self.df.isnull().sum().sum()}")
        
        return self.df
    
    def descriptive_statistics(self):
        """2) 描述性統計與欄位關係"""
        print("\n" + "=" * 60)
        print("2) 描述性統計與欄位關係")
        print("=" * 60)
        
        # 數值欄位描述性統計
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        print("\n描述性統計:")
        desc_stats = self.df[numeric_cols].describe()
        print(desc_stats)
        
        # 相關矩陣
        print("\n計算相關矩陣...")
        corr_matrix = self.df[numeric_cols].corr()
        
        # 繪製相關性熱力圖
        plt.figure(figsize=(15, 12))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8}, fmt='.2f')
        plt.title('數值欄位相關性熱力圖', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 找出高相關性對
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
        
        print(f"\n高相關性對 (|r| > 0.7):")
        for pair in high_corr_pairs:
            print(f"{pair[0]} - {pair[1]}: {pair[2]:.3f}")
        
        return desc_stats, corr_matrix
    
    def temporal_visualization(self):
        """3) 時序視覺化"""
        print("\n" + "=" * 60)
        print("3) 時序視覺化")
        print("=" * 60)
        
        # 主要指標
        main_indicators = ['確診數', 'ovum_sum', '週平均氣溫(℃)_x', '週平均氣溫(℃)_y', 
                          '週總降水量(mm)_x', '週總降水量(mm)_y']
        
        # 檢查哪些欄位存在
        available_indicators = [col for col in main_indicators if col in self.df.columns]
        print(f"可用的主要指標: {available_indicators}")
        
        # 獲取所有區
        districts = self.df['區'].unique()
        print(f"行政區數量: {len(districts)}")
        
        # 為每個指標創建時序圖
        for indicator in available_indicators:
            if indicator in self.df.columns:
                self._plot_temporal_indicator(indicator, districts)
        
        # 創建綜合時序圖
        self._plot_comprehensive_temporal()
    
    def _plot_temporal_indicator(self, indicator, districts):
        """繪製單一指標的時序圖"""
        plt.figure(figsize=(16, 10))
        
        # 選擇前6個區進行展示（避免圖表過於擁擠）
        top_districts = districts[:6]
        
        for i, district in enumerate(top_districts):
            district_data = self.df[self.df['區'] == district].copy()
            if len(district_data) > 0:
                plt.subplot(2, 3, i+1)
                plt.plot(district_data['week_start'], district_data[indicator], 
                        marker='o', linewidth=2, markersize=4)
                plt.title(f'{district} - {indicator}', fontsize=12)
                plt.xlabel('時間')
                plt.ylabel(indicator)
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'temporal_{indicator.replace("/", "_").replace("(", "").replace(")", "")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def _plot_comprehensive_temporal(self):
        """繪製綜合時序圖"""
        # 選擇幾個關鍵指標
        key_indicators = ['確診數', 'ovum_sum', '週平均氣溫(℃)_x', '週總降水量(mm)_x']
        available_key = [col for col in key_indicators if col in self.df.columns]
        
        if len(available_key) < 2:
            return
        
        # 計算所有區的平均值
        weekly_avg = self.df.groupby('week_start')[available_key].mean()
        
        fig, axes = plt.subplots(len(available_key), 1, figsize=(15, 4*len(available_key)))
        if len(available_key) == 1:
            axes = [axes]
        
        for i, indicator in enumerate(available_key):
            axes[i].plot(weekly_avg.index, weekly_avg[indicator], 
                        linewidth=2, marker='o', markersize=3)
            axes[i].set_title(f'全區平均 {indicator}', fontsize=14)
            axes[i].set_ylabel(indicator)
            axes[i].grid(True, alpha=0.3)
            axes[i].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('comprehensive_temporal.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def extract_temporal_features(self):
        """4) 時序特徵提取"""
        print("\n" + "=" * 60)
        print("4) 時序特徵提取")
        print("=" * 60)
        
        # 選擇數值欄位進行特徵提取
        feature_cols = ['確診數', 'ovum_sum', '週平均氣溫(℃)_x', '週平均氣溫(℃)_y',
                       '週總降水量(mm)_x', '週總降水量(mm)_y', '噴藥次數']
        available_features = [col for col in feature_cols if col in self.df.columns]
        
        print(f"提取特徵的欄位: {available_features}")
        
        features_list = []
        
        for district in self.df['區'].unique():
            district_data = self.df[self.df['區'] == district].copy()
            if len(district_data) < 10:  # 數據點太少則跳過
                continue
                
            district_data = district_data.sort_values('week_start')
            features = {'區': district}
            
            for col in available_features:
                series = district_data[col].dropna()
                if len(series) < 5:
                    continue
                
                # 基本統計量
                features[f'{col}_mean'] = series.mean()
                features[f'{col}_std'] = series.std()
                features[f'{col}_min'] = series.min()
                features[f'{col}_max'] = series.max()
                features[f'{col}_q25'] = series.quantile(0.25)
                features[f'{col}_q50'] = series.quantile(0.50)
                features[f'{col}_q75'] = series.quantile(0.75)
                
                # 變動率
                if len(series) > 1:
                    pct_change = series.pct_change().dropna()
                    # 處理無窮大值
                    pct_change = pct_change.replace([np.inf, -np.inf], np.nan)
                    if not pct_change.isna().all():
                        features[f'{col}_pct_change_mean'] = pct_change.mean() if not pct_change.isna().all() else 0
                        features[f'{col}_pct_change_std'] = pct_change.std() if not pct_change.isna().all() else 0
                    else:
                        features[f'{col}_pct_change_mean'] = 0
                        features[f'{col}_pct_change_std'] = 0
                
                # 自相關
                try:
                    if len(series) > 10:
                        acf_values = acf(series, nlags=min(5, len(series)-1), fft=False)
                        for lag in range(1, min(4, len(acf_values))):
                            features[f'{col}_acf_lag{lag}'] = acf_values[lag]
                except:
                    pass
                
                # 季節性分解（如果數據足夠長）
                try:
                    if len(series) >= 24:  # 至少6個月的週數據
                        decomposition = seasonal_decompose(series, model='additive', period=4)
                        features[f'{col}_trend_slope'] = np.polyfit(range(len(decomposition.trend.dropna())), 
                                                                  decomposition.trend.dropna(), 1)[0]
                        features[f'{col}_seasonal_std'] = decomposition.seasonal.std()
                    else:
                        # 簡單趨勢
                        features[f'{col}_trend_slope'] = np.polyfit(range(len(series)), series, 1)[0]
                except:
                    features[f'{col}_trend_slope'] = 0
            
            features_list.append(features)
        
        self.features_df = pd.DataFrame(features_list)
        print(f"特徵提取完成，特徵表形狀: {self.features_df.shape}")
        print(f"特徵列: {list(self.features_df.columns)}")
        
        # 保存特徵表
        self.features_df.to_csv('temporal_features.csv', index=False, encoding='utf-8-sig')
        print("特徵表已保存為 temporal_features.csv")
        
        return self.features_df
    
    def temporal_clustering(self):
        """5) 時序相似性與分群"""
        print("\n" + "=" * 60)
        print("5) 時序相似性與分群")
        print("=" * 60)
        
        if self.features_df is None:
            print("請先執行特徵提取")
            return
        
        # 準備特徵數據
        feature_cols = [col for col in self.features_df.columns if col != '區']
        X = self.features_df[feature_cols].fillna(0)
        
        # 處理無窮大值
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)
        
        # 標準化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 方法1: KMeans分群
        self._kmeans_clustering(X_scaled)
        
        # 方法2: 基於序列距離的分群
        self._sequence_distance_clustering()
    
    def _kmeans_clustering(self, X_scaled):
        """KMeans分群"""
        print("\n方法1: KMeans分群")
        
        # 選擇最佳k值
        inertias = []
        silhouette_scores = []
        k_range = range(2, min(8, len(X_scaled)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X_scaled, cluster_labels))
        
        # 繪製肘部法則和輪廓係數圖
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        ax1.plot(k_range, inertias, 'bo-')
        ax1.set_xlabel('K值')
        ax1.set_ylabel('Inertia')
        ax1.set_title('肘部法則')
        ax1.grid(True)
        
        ax2.plot(k_range, silhouette_scores, 'ro-')
        ax2.set_xlabel('K值')
        ax2.set_ylabel('Silhouette Score')
        ax2.set_title('輪廓係數')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('kmeans_parameter_selection.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 選擇最佳k值（輪廓係數最高）
        best_k = k_range[np.argmax(silhouette_scores)]
        print(f"最佳K值: {best_k} (輪廓係數: {max(silhouette_scores):.3f})")
        
        # 執行最終分群
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        self.features_df['kmeans_cluster'] = cluster_labels
        self.cluster_results['kmeans'] = {
            'labels': cluster_labels,
            'k': best_k,
            'silhouette_score': max(silhouette_scores)
        }
        
        # 顯示分群結果
        print(f"\nKMeans分群結果 (k={best_k}):")
        cluster_summary = self.features_df.groupby('kmeans_cluster')['區'].apply(list).to_dict()
        for cluster_id, districts in cluster_summary.items():
            print(f"群組 {cluster_id}: {districts}")
        
        # 繪製分群結果
        self._plot_cluster_results('kmeans', X_scaled)
    
    def _sequence_distance_clustering(self):
        """基於序列距離的分群"""
        print("\n方法2: 基於序列距離的分群")
        
        # 選擇幾個關鍵時序指標
        key_indicators = ['確診數', 'ovum_sum', '週平均氣溫(℃)_x', '週總降水量(mm)_x']
        available_indicators = [col for col in key_indicators if col in self.df.columns]
        
        if len(available_indicators) < 2:
            print("可用指標不足，跳過序列距離分群")
            return
        
        # 為每個區提取時序數據
        district_sequences = {}
        for district in self.df['區'].unique():
            district_data = self.df[self.df['區'] == district].sort_values('week_start')
            if len(district_data) < 10:
                continue
            
            # 標準化時序數據
            sequence = []
            for indicator in available_indicators:
                series = district_data[indicator].fillna(method='ffill').fillna(method='bfill')
                if len(series) > 0:
                    # 標準化
                    series_norm = (series - series.mean()) / (series.std() + 1e-8)
                    sequence.extend(series_norm.values)
            
            if len(sequence) > 0:
                district_sequences[district] = sequence
        
        if len(district_sequences) < 3:
            print("區數量不足，跳過序列距離分群")
            return
        
        # 計算距離矩陣
        districts = list(district_sequences.keys())
        n_districts = len(districts)
        distance_matrix = np.zeros((n_districts, n_districts))
        
        print("計算序列距離矩陣...")
        for i in range(n_districts):
            for j in range(i+1, n_districts):
                seq1 = district_sequences[districts[i]]
                seq2 = district_sequences[districts[j]]
                
                # 使用歐幾里得距離（如果DTW不可用）
                if DTW_AVAILABLE and len(seq1) == len(seq2):
                    try:
                        dist = dtw.distance(seq1, seq2)
                    except:
                        dist = np.linalg.norm(np.array(seq1) - np.array(seq2))
                else:
                    # 調整序列長度
                    min_len = min(len(seq1), len(seq2))
                    dist = np.linalg.norm(np.array(seq1[:min_len]) - np.array(seq2[:min_len]))
                
                distance_matrix[i, j] = dist
                distance_matrix[j, i] = dist
        
        # 確保距離矩陣是對稱的
        distance_matrix = (distance_matrix + distance_matrix.T) / 2
        np.fill_diagonal(distance_matrix, 0)
        
        # 層次分群
        linkage_matrix = linkage(squareform(distance_matrix), method='ward')
        
        # 繪製樹狀圖
        plt.figure(figsize=(12, 8))
        dendrogram(linkage_matrix, labels=districts, leaf_rotation=90)
        plt.title('基於序列距離的層次分群樹狀圖')
        plt.tight_layout()
        plt.savefig('hierarchical_clustering_dendrogram.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 選擇分群數並獲取分群標籤
        n_clusters = min(4, n_districts // 2)
        from scipy.cluster.hierarchy import fcluster
        cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust') - 1
        
        # 保存分群結果
        cluster_df = pd.DataFrame({
            '區': districts,
            'hierarchical_cluster': cluster_labels
        })
        
        # 合併到特徵表
        if self.features_df is not None:
            self.features_df = self.features_df.merge(cluster_df, on='區', how='left')
        
        self.cluster_results['hierarchical'] = {
            'labels': cluster_labels,
            'districts': districts,
            'distance_matrix': distance_matrix
        }
        
        # 顯示分群結果
        print(f"\n層次分群結果 (k={n_clusters}):")
        for cluster_id in range(n_clusters):
            cluster_districts = [districts[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
            print(f"群組 {cluster_id}: {cluster_districts}")
    
    def _plot_cluster_results(self, method, X_scaled):
        """繪製分群結果"""
        if method not in self.cluster_results:
            return
        
        # PCA降維可視化
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], 
                            c=self.cluster_results[method]['labels'], 
                            cmap='viridis', alpha=0.7, s=100)
        
        # 添加區名標籤
        for i, district in enumerate(self.features_df['區']):
            plt.annotate(district, (X_pca[i, 0], X_pca[i, 1]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.colorbar(scatter)
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
        plt.title(f'{method.upper()}分群結果 (PCA可視化)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{method}_clustering_pca.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_insights(self):
        """6) 解釋與實務建議"""
        print("\n" + "=" * 60)
        print("6) 解釋與實務建議")
        print("=" * 60)
        
        insights = []
        
        # 分析相關性
        if hasattr(self, 'df'):
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if '確診數' in numeric_cols:
                corr_with_cases = self.df[numeric_cols].corr()['確診數'].abs().sort_values(ascending=False)
                top_correlated = corr_with_cases.head(6)[1:]  # 排除自己
                insights.append(f"與確診數最相關的變數: {', '.join([f'{var}({corr:.2f})' for var, corr in top_correlated.head(3).items()])}")
        
        # 分析分群結果
        if 'kmeans' in self.cluster_results:
            kmeans_result = self.cluster_results['kmeans']
            insights.append(f"KMeans分群識別出{kmeans_result['k']}個不同的時序模式群組，輪廓係數為{kmeans_result['silhouette_score']:.3f}")
        
        if 'hierarchical' in self.cluster_results:
            hierarchical_result = self.cluster_results['hierarchical']
            insights.append(f"層次分群基於序列距離識別出{len(set(hierarchical_result['labels']))}個群組")
        
        # 時序特徵分析
        if self.features_df is not None:
            # 找出變異最大的特徵
            feature_cols = [col for col in self.features_df.columns if col not in ['區', 'kmeans_cluster', 'hierarchical_cluster']]
            if feature_cols:
                feature_std = self.features_df[feature_cols].std().sort_values(ascending=False)
                insights.append(f"變異最大的特徵: {feature_std.index[0]}({feature_std.iloc[0]:.2f})")
        
        # 季節性分析
        if hasattr(self, 'df') and 'week_start' in self.df.columns:
            self.df['month'] = self.df['week_start'].dt.month
            if '確診數' in self.df.columns:
                monthly_cases = self.df.groupby('month')['確診數'].mean()
                peak_month = monthly_cases.idxmax()
                insights.append(f"確診數高峰月份: {peak_month}月")
        
        # 生成結論
        conclusion = f"""
## 時序分析結論與實務建議

1. **時序模式識別**: 通過KMeans和層次分群分析，成功識別出不同行政區的時序模式群組，這些群組在登革熱病例、誘卵桶數量、氣象條件等方面表現出相似的變化趨勢。

2. **關鍵影響因子**: {insights[0] if insights else '氣溫、降水、誘卵桶數量是影響確診數的主要因子'}，這些變數的時序變化模式對預測登革熱疫情具有重要參考價值。

3. **季節性特徵**: {insights[-1] if insights else '數據顯示明顯的季節性變化'}，這與登革熱的傳播週期和氣候條件密切相關。

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
        
        return conclusion
    
    def record_technical_details(self):
        """7) 技術細節與參數記錄"""
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
- 層次分群:
  * 距離計算: {'DTW距離' if DTW_AVAILABLE else '歐幾里得距離'}
  * 連結方法: Ward
  * 分群數: 自動選擇（最大4群）

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
        
        return technical_details
    
    def save_results(self):
        """8) 保存所有結果"""
        print("\n" + "=" * 60)
        print("8) 保存結果")
        print("=" * 60)
        
        # 保存分群結果
        if self.features_df is not None:
            self.features_df.to_csv('clustering_results.csv', index=False, encoding='utf-8-sig')
            print("分群結果已保存為 clustering_results.csv")
        
        # 保存描述性統計
        if hasattr(self, 'df'):
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            desc_stats = self.df[numeric_cols].describe()
            desc_stats.to_csv('descriptive_statistics.csv', encoding='utf-8-sig')
            print("描述性統計已保存為 descriptive_statistics.csv")
        
        print("\n所有分析結果已保存完成！")
    
    def run_complete_analysis(self):
        """執行完整分析流程"""
        print("開始執行完整的時序分析...")
        
        # 執行所有分析步驟
        self.load_and_clean_data()
        self.descriptive_statistics()
        self.temporal_visualization()
        self.extract_temporal_features()
        self.temporal_clustering()
        self.generate_insights()
        self.record_technical_details()
        self.save_results()
        
        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)

def main():
    """主函數"""
    # 數據路徑
    data_path = '/Users/SummerTu/Desktop/2025_Fall/DengueFeverProject/TestData/data/merged_2023_左台南測站右永康測站.csv'
    geojson_path = '/Users/SummerTu/Desktop/2025_Fall/DengueFeverProject/TestData/data/district_boundaries.geojson'
    
    # 創建分析器並執行分析
    analyzer = TemporalAnalyzer(data_path, geojson_path)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
