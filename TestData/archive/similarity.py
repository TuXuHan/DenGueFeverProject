#!/usr/bin/env python3
"""
相似度計算模組 - 獨立運行版本
這個文件包含了所有相似度計算函數，可以直接運行
"""

import numpy as np
from scipy.spatial.distance import cosine
from dtaidistance import dtw

def feature_similarity(f1, f2):
    """使用 cosine similarity 比較特徵相似度"""
    return 1 - cosine(f1, f2)

def temporal_similarity(ts1, ts2, sigma=50):
    """使用 DTW 計算時間序列相似度"""
    distance = dtw.distance(ts1, ts2)
    sim = np.exp(-distance / sigma)
    return sim

def combined_similarity(f1, f2, ts1, ts2, alpha=0.5, sigma=50):
    """融合特徵相似度 + 時序相似度"""
    f_sim = feature_similarity(f1, f2)
    t_sim = temporal_similarity(ts1, ts2, sigma)
    return alpha * f_sim + (1 - alpha) * t_sim

def demo():
    """演示所有函數的使用"""
    print("🎯 相似度計算模組演示")
    print("=" * 50)
    
    
    print(f"特徵向量1: {f1}")
    print(f"特徵向量2: {f2}")
    print(f"時間序列1: {ts1}")
    print(f"時間序列2: {ts2}")
    
    print("\n🔍 計算相似度...")
    
    # 特徵相似度
    feature_sim = feature_similarity(f1, f2)
    print(f"特徵相似度: {feature_sim:.4f}")
    
    # 時間序列相似度
    temporal_sim = temporal_similarity(ts1, ts2)
    print(f"時間序列相似度: {temporal_sim:.4f}")
    
    # 綜合相似度
    combined_sim = combined_similarity(f1, f2, ts1, ts2)
    print(f"綜合相似度: {combined_sim:.4f}")
    
    print("\n📝 參數說明:")
    print("- alpha: 特徵相似度的權重（0-1之間），預設為0.5")
    print("- sigma: DTW距離的標準化參數，預設為50")
    
    print("\n✅ 演示完成！")

if __name__ == "__main__":
    demo()
