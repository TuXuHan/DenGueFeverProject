#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桶數統計程式
計算各區、各里的誘卵桶數量
"""

import json
import pandas as pd
from collections import defaultdict
import os

def load_bucket_data(json_file_path):
    """
    載入桶的資料
    
    Args:
        json_file_path (str): JSON檔案路徑
        
    Returns:
        list: 桶的資料列表
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功載入 {len(data)} 筆桶的資料")
        return data
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"錯誤：JSON檔案格式錯誤 {json_file_path}")
        return []
    except Exception as e:
        print(f"載入資料時發生錯誤：{e}")
        return []

def count_buckets_by_district_and_village(data):
    """
    計算各區、各里的桶數
    
    Args:
        data (list): 桶的資料列表
        
    Returns:
        dict: 統計結果
    """
    # 使用defaultdict來統計
    district_village_count = defaultdict(lambda: defaultdict(int))
    district_total = defaultdict(int)
    village_total = defaultdict(int)
    
    for bucket in data:
        district = bucket.get('DIST', '未知區')
        village = bucket.get('VILL', '未知里')
        
        # 統計各區各里的桶數
        district_village_count[district][village] += 1
        
        # 統計各區總桶數
        district_total[district] += 1
        
        # 統計各里總桶數
        village_total[village] += 1
    
    return {
        'district_village': dict(district_village_count),
        'district_total': dict(district_total),
        'village_total': dict(village_total)
    }

def print_statistics(stats):
    """
    印出統計結果
    
    Args:
        stats (dict): 統計結果
    """
    print("\n" + "="*60)
    print("各區、各里桶數統計結果")
    print("="*60)
    
    # 按區印出詳細統計
    for district, villages in stats['district_village'].items():
        print(f"\n【{district}】")
        print("-" * 40)
        
        # 印出該區各里的桶數
        for village, count in sorted(villages.items()):
            print(f"  {village}: {count} 個桶")
        
        # 印出該區總桶數
        total = stats['district_total'][district]
        print(f"  {'總計':>10}: {total} 個桶")
    
    # 印出全市總桶數
    grand_total = sum(stats['district_total'].values())
    print(f"\n【全市總計】: {grand_total} 個桶")
    
    # 印出各區總桶數排序
    print(f"\n【各區桶數排序】")
    print("-" * 40)
    sorted_districts = sorted(stats['district_total'].items(), 
                            key=lambda x: x[1], reverse=True)
    for district, count in sorted_districts:
        print(f"  {district}: {count} 個桶")

def save_statistics_to_file(stats, output_file):
    """
    將統計結果儲存到檔案
    
    Args:
        stats (dict): 統計結果
        output_file (str): 輸出檔案路徑
    """
    try:
        # 準備要儲存的資料
        output_data = {
            'summary': {
                'total_buckets': sum(stats['district_total'].values()),
                'total_districts': len(stats['district_total']),
                'total_villages': len(stats['village_total'])
            },
            'district_statistics': stats['district_total'],
            'village_statistics': stats['village_total'],
            'detailed_statistics': stats['district_village']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n統計結果已儲存到: {output_file}")
        
    except Exception as e:
        print(f"儲存檔案時發生錯誤：{e}")

def save_to_csv(stats, output_file):
    """
    將統計結果儲存為CSV格式
    
    Args:
        stats (dict): 統計結果
        output_file (str): 輸出CSV檔案路徑
    """
    try:
        # 準備CSV資料
        csv_data = []
        for district, villages in stats['district_village'].items():
            for village, count in villages.items():
                csv_data.append({
                    '區': district,
                    '里': village,
                    '桶數': count
                })
        
        # 轉換為DataFrame並儲存
        df = pd.DataFrame(csv_data)
        df = df.sort_values(['區', '桶數'], ascending=[True, False])
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"CSV格式統計結果已儲存到: {output_file}")
        
    except Exception as e:
        print(f"儲存CSV檔案時發生錯誤：{e}")

def main():
    """
    主程式
    """
    # 設定檔案路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    bucket_file = os.path.join(project_root, 'Question1', 'data', 'bucket_converted.json')
    
    print("開始計算各區、各里的桶數...")
    print(f"資料檔案路徑: {bucket_file}")
    
    # 載入資料
    data = load_bucket_data(bucket_file)
    if not data:
        print("無法載入資料，程式結束")
        return
    
    # 計算統計
    stats = count_buckets_by_district_and_village(data)
    
    # 印出結果
    print_statistics(stats)
    
    # 儲存結果到檔案
    output_dir = current_dir
    json_output = os.path.join(output_dir, 'bucket_statistics.json')
    csv_output = os.path.join(output_dir, 'bucket_statistics.csv')
    
    save_statistics_to_file(stats, json_output)
    save_to_csv(stats, csv_output)
    
    print("\n程式執行完成！")

if __name__ == "__main__":
    main()
