#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建 imputation.csv 文件
包含27區的中心點位置和預測數量（沒有桶子的區顯示預測值，有桶子的區可以設為None）
"""

import json
import csv
from pathlib import Path

# 計算幾何中心點（簡單方法）
def calculate_centroid(geometry):
    """計算 GeoJSON 幾何體的中心點"""
    if geometry['type'] == 'Polygon':
        coords = geometry['coordinates'][0]  # 外環座標
    elif geometry['type'] == 'MultiPolygon':
        # 對於 MultiPolygon，使用第一個 Polygon
        coords = geometry['coordinates'][0][0]
    else:
        return None
    
    # 計算所有座標的平均值
    lats = [coord[1] for coord in coords]
    lons = [coord[0] for coord in coords]
    
    centroid_lat = sum(lats) / len(lats)
    centroid_lon = sum(lons) / len(lons)
    
    return centroid_lat, centroid_lon

def main():
    # 讀取行政區邊界
    data_dir = Path(__file__).parent
    geojson_path = data_dir / 'district_boundaries.geojson'
    bucket_path = data_dir / 'bucket_converted.json'
    
    print("正在讀取數據...")
    
    # 讀取行政區邊界
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geo = json.load(f)
    
    # 讀取桶子數據，找出有桶子的區
    with open(bucket_path, 'r', encoding='utf-8') as f:
        bucket_data = json.load(f)
    
    # 獲取有桶子的區
    buckets_districts = set([item['DIST'] for item in bucket_data])
    print(f"有桶子的區: {sorted(buckets_districts)}")
    print(f"有桶子的區數量: {len(buckets_districts)}")
    
    # 計算所有區的中心點並生成數據
    imputation_data = []
    
    for feature in geo['features']:
        district_name = feature['properties']['name']
        geometry = feature['geometry']
        
        # 計算中心點
        centroid = calculate_centroid(geometry)
        if centroid is None:
            print(f"警告: 無法計算 {district_name} 的中心點")
            continue
        
        lat, lon = centroid
        
        # 檢查是否有桶子
        has_bucket = district_name in buckets_districts
        
        # 創建記錄
        # 預設預測數量為 None（顯示灰色），如果沒有桶子則可以設置預測值
        # 這裡先設為 None，用戶可以後續更新
        record = {
            'district': district_name,
            'lat': lat,
            'lon': lon,
            'predicted_value': None,  # 預測數量，None 表示沒有值（顯示灰色）
            'has_bucket': has_bucket
        }
        
        imputation_data.append(record)
    
    # 排序
    imputation_data.sort(key=lambda x: x['district'])
    
    print(f"\n找到 {len(imputation_data)} 個區")
    print("\n沒有桶子的區:")
    no_bucket = [d for d in imputation_data if not d['has_bucket']]
    print(f"總數: {len(no_bucket)}")
    for d in no_bucket:
        print(f"  {d['district']}: 中心點 [{d['lat']:.6f}, {d['lon']:.6f}]")
    
    # 寫入 CSV 文件
    output_path = data_dir / 'imputation.csv'
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['district', 'lat', 'lon', 'predicted_value'])
        writer.writeheader()
        for record in imputation_data:
            writer.writerow({
                'district': record['district'],
                'lat': record['lat'],
                'lon': record['lon'],
                'predicted_value': record['predicted_value'] if record['predicted_value'] is not None else ''
            })
    
    print(f"\n✓ 已創建 imputation.csv 文件: {output_path}")
    print(f"  總共 {len(imputation_data)} 個區")
    print(f"  其中 {len(no_bucket)} 個區沒有桶子（需要設置預測值）")

if __name__ == '__main__':
    main()

