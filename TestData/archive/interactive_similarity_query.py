#!/usr/bin/env python3
"""
互動式相似度查詢工具
允許用戶選擇行政區並查看最相似的前3個區域
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class InteractiveSimilarityQuery:
    def __init__(self, data_path):
        """初始化查詢工具"""
        self.data_path = data_path
        self.df = None
        self.districts = None
        self.similarity_matrix = None
        self.features_df = None
        
    def load_and_prepare_data(self):
        """載入並準備資料"""
        print("📊 載入資料...")
        
        # 載入資料
        self.df = pd.read_csv(self.data_path)
        self.df = self.df.fillna(0)
        self.df['確診數'] = pd.to_numeric(self.df['確診數'], errors='coerce').fillna(0)
        self.df['ovum_sum'] = pd.to_numeric(self.df['ovum_sum'], errors='coerce').fillna(0)
        
        self.districts = self.df['區'].unique()
        print(f"✅ 載入完成！共有 {len(self.districts)} 個行政區")
        
        # 提取特徵
        self._extract_features()
        
        # 計算相似度
        self._calculate_similarity()
        
    def _extract_features(self):
        """提取特徵"""
        print("🎯 提取特徵...")
        
        features_list = []
        district_list = []
        
        for district in self.districts:
            district_data = self.df[self.df['區'] == district]
            
            # 綜合特徵
            features = [
                # 天氣特徵
                district_data['週平均氣溫(℃)_x'].mean(),
                district_data['週最高氣溫(℃)_x'].mean(),
                district_data['週最低氣溫(℃)_x'].mean(),
                district_data['週總降水量(mm)_x'].mean(),
                district_data['週平均相對溼度(%)_x'].mean(),
                district_data['週總日照時數(hour)_x'].mean(),
                district_data['週平均測站氣壓(hPa)_x'].mean(),
                # 確診特徵
                district_data['確診數'].sum(),
                district_data['確診數'].mean(),
                district_data['確診數'].std() if district_data['確診數'].std() > 0 else 0,
                # 卵數特徵
                district_data['ovum_sum'].sum(),
                district_data['ovum_sum'].mean(),
                district_data['ovum_sum'].std() if district_data['ovum_sum'].std() > 0 else 0,
                # 颱風特徵
                district_data['颱風數量_x'].sum() + district_data['颱風數量_y'].sum(),
                district_data['颱風數量_x'].mean() + district_data['颱風數量_y'].mean(),
                # 其他特徵
                district_data['噴藥次數'].sum(),
                district_data['噴藥次數'].mean(),
                district_data['人口數總計'].iloc[0] if len(district_data) > 0 else 0
            ]
            
            features_list.append(features)
            district_list.append(district)
        
        # 特徵名稱
        feature_names = [
            'avg_temp', 'max_temp', 'min_temp', 'total_precip', 'avg_humidity', 
            'sunshine_hours', 'avg_pressure',
            'total_cases', 'avg_cases', 'cases_std',
            'total_ovum', 'avg_ovum', 'ovum_std',
            'total_typhoon', 'avg_typhoon',
            'total_spray', 'avg_spray', 'population'
        ]
        
        self.features_df = pd.DataFrame(features_list, index=district_list, columns=feature_names)
        print(f"✅ 特徵提取完成！每個行政區有 {len(feature_names)} 個特徵")
        
    def _calculate_similarity(self):
        """計算相似度矩陣"""
        print("🔍 計算相似度矩陣...")
        
        # 標準化特徵
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(self.features_df)
        
        # 計算相似度
        self.similarity_matrix = cosine_similarity(features_scaled)
        
        print("✅ 相似度計算完成！")
        
    def query_similarity(self, target_district, top_n=3):
        """查詢指定行政區的最相似區域"""
        if target_district not in self.districts:
            print(f"❌ 找不到行政區: {target_district}")
            return None
        
        # 獲取相似度
        target_idx = list(self.districts).index(target_district)
        similarities = self.similarity_matrix[target_idx]
        
        # 創建相似度DataFrame
        similarity_df = pd.DataFrame({
            'district': self.districts,
            'similarity': similarities
        })
        
        # 排序並排除自己
        similarity_df = similarity_df[similarity_df['district'] != target_district]
        similarity_df = similarity_df.sort_values('similarity', ascending=False)
        
        # 返回前N個
        top_similar = similarity_df.head(top_n)
        
        return top_similar
    
    def display_similarity_results(self, target_district, top_n=3):
        """顯示相似度查詢結果"""
        results = self.query_similarity(target_district, top_n)
        
        if results is None:
            return
        
        print(f"\n📍 {target_district} 最相似的前{top_n}個行政區：")
        print("-" * 50)
        
        for i, (_, row) in enumerate(results.iterrows(), 1):
            district = row['district']
            similarity = row['similarity']
            
            print(f"{i}. {district}: {similarity:.4f}")
            
            # 顯示該區域的基本資訊
            district_data = self.df[self.df['區'] == district]
            print(f"   - 總確診數: {district_data['確診數'].sum()}")
            print(f"   - 總卵數: {district_data['ovum_sum'].sum()}")
            print(f"   - 總噴藥次數: {district_data['噴藥次數'].sum()}")
            print(f"   - 平均氣溫: {district_data['週平均氣溫(℃)_x'].mean():.1f}°C")
            print()
    
    def compare_districts(self, district1, district2):
        """比較兩個行政區的詳細資訊"""
        if district1 not in self.districts or district2 not in self.districts:
            print("❌ 找不到指定的行政區")
            return
        
        # 獲取相似度
        idx1 = list(self.districts).index(district1)
        idx2 = list(self.districts).index(district2)
        similarity = self.similarity_matrix[idx1, idx2]
        
        print(f"\n🔍 {district1} vs {district2} 詳細比較")
        print("=" * 60)
        print(f"相似度: {similarity:.4f}")
        print()
        
        # 比較特徵
        features1 = self.features_df.loc[district1]
        features2 = self.features_df.loc[district2]
        
        comparison_df = pd.DataFrame({
            'feature': self.features_df.columns,
            district1: features1.values,
            district2: features2.values
        })
        
        comparison_df['difference'] = abs(comparison_df[district1] - comparison_df[district2])
        comparison_df = comparison_df.sort_values('difference', ascending=False)
        
        print("📊 特徵差異排名（差異越大越不相似）：")
        print("-" * 60)
        for _, row in comparison_df.head(10).iterrows():
            feature = row['feature']
            val1 = row[district1]
            val2 = row[district2]
            diff = row['difference']
            print(f"{feature:15s}: {district1}={val1:8.2f}, {district2}={val2:8.2f}, 差異={diff:8.2f}")
    
    def show_all_districts(self):
        """顯示所有行政區列表"""
        print("\n📋 所有行政區列表：")
        print("-" * 30)
        for i, district in enumerate(self.districts, 1):
            print(f"{i:2d}. {district}")
    
    def interactive_mode(self):
        """互動模式"""
        print("\n🎮 進入互動模式")
        print("=" * 50)
        print("可用指令：")
        print("1. 'list' - 顯示所有行政區")
        print("2. 'query <行政區名>' - 查詢最相似的3個區域")
        print("3. 'compare <行政區1> <行政區2>' - 比較兩個行政區")
        print("4. 'quit' - 退出")
        print()
        
        while True:
            try:
                command = input("請輸入指令: ").strip()
                
                if command.lower() == 'quit':
                    print("👋 再見！")
                    break
                elif command.lower() == 'list':
                    self.show_all_districts()
                elif command.startswith('query '):
                    district = command[6:].strip()
                    self.display_similarity_results(district)
                elif command.startswith('compare '):
                    parts = command[8:].strip().split()
                    if len(parts) == 2:
                        self.compare_districts(parts[0], parts[1])
                    else:
                        print("❌ 請輸入兩個行政區名稱")
                else:
                    print("❌ 未知指令，請重新輸入")
                    
            except KeyboardInterrupt:
                print("\n👋 再見！")
                break
            except Exception as e:
                print(f"❌ 錯誤: {e}")

def main():
    """主函數"""
    data_path = 'data/merged_2023_左台南測站右永康測站.csv'
    
    # 創建查詢工具
    query_tool = InteractiveSimilarityQuery(data_path)
    query_tool.load_and_prepare_data()
    
    # 演示查詢功能
    print("\n🎯 相似度查詢演示")
    print("=" * 50)
    
    demo_districts = ['東區', '永康區', '新營區', '佳里區', '麻豆區']
    
    for district in demo_districts:
        query_tool.display_similarity_results(district, 3)
    
    # 進入互動模式
    query_tool.interactive_mode()
    
    return query_tool

if __name__ == "__main__":
    query_tool = main()
