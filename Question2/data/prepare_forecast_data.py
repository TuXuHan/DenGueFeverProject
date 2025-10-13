#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
準備登革熱預測數據，用於地圖顯示
整合村里ID、預測案例數據，並按區域和嚴重程度組織
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

print("=" * 60)
print("準備登革熱預測數據...")
print("=" * 60)

# 檔案路徑
RESULT_DIR = Path(__file__).parent / "result"
VILLAGE_IDS_FILE = RESULT_DIR / "village_ids_tainan.csv"
FORECAST_FILE = RESULT_DIR / "forecast_T2_long.csv"
FORECAST_WIDE_FILE = RESULT_DIR / "forecast_T2_wide.csv"
FORECAST_DISTRICT_FILE = RESULT_DIR / "forecast_T2_long_district.csv"
OUTPUT_FILE = Path(__file__).parent / "forecast_data_processed.json"

# 1. 讀取村里ID映射
print("\n步驟 1: 讀取村里ID映射...")
village_mapping = pd.read_csv(VILLAGE_IDS_FILE)
print(f"✓ 讀取 {len(village_mapping)} 個村里記錄")

# 2. 讀取村里級別預測數據（從寬格式CSV）
print("\n步驟 2: 讀取村里級別預測數據（從寬格式CSV）...")
forecast_wide = pd.read_csv(FORECAST_WIDE_FILE)
print(f"✓ 讀取寬格式數據，包含 {len(forecast_wide.columns)-1} 個村里")

# 獲取最新一週的數據（最後一行）
latest_week = forecast_wide['week_start'].iloc[-1]
print(f"✓ 最新預測週次: {latest_week}")

# 轉換寬格式為長格式
village_ids = [col for col in forecast_wide.columns if col != 'week_start']
forecast_latest = pd.DataFrame({
    'VillageID': village_ids,
    'pred_cases': [forecast_wide[vid].iloc[-1] for vid in village_ids],
    'week_start': latest_week
})
print(f"✓ 最新一週數據: {len(forecast_latest)} 條記錄")

# 3. 讀取區域級別預測數據
print("\n步驟 3: 讀取區域級別預測數據...")
forecast_district = pd.read_csv(FORECAST_DISTRICT_FILE)
forecast_district_latest = forecast_district[forecast_district['week_start'] == latest_week].copy()
print(f"✓ 區域級別數據: {len(forecast_district_latest)} 個區域")

# 4. 合併數據
print("\n步驟 4: 合併村里數據...")
merged_data = pd.merge(
    forecast_latest,
    village_mapping,
    on='VillageID',
    how='left'
)
print(f"✓ 合併後數據: {len(merged_data)} 條記錄")

# 檢查未匹配的村里
unmatched = merged_data[merged_data['VillageName'].isna()]
if len(unmatched) > 0:
    print(f"⚠️  警告: {len(unmatched)} 個村里ID未找到匹配")
    print(f"   未匹配ID示例: {unmatched['VillageID'].head().tolist()}")

# 5. 按區域組織數據
print("\n步驟 5: 按區域組織數據...")
district_data = {}

# 處理區域級別匯總
for _, row in forecast_district_latest.iterrows():
    district_code = str(row['DistrictCode'])
    district_data[district_code] = {
        'district_code': district_code,
        'total_pred_cases': int(row['pred_cases']),
        'villages': []
    }

# 處理村里級別數據
for _, row in merged_data.iterrows():
    if pd.notna(row['VillageName']):
        district_code = str(row['DistrictCode'])
        
        if district_code not in district_data:
            district_data[district_code] = {
                'district_code': district_code,
                'district_name': row['DistrictName'],
                'total_pred_cases': 0,
                'villages': []
            }
        
        # 設置區域名稱（如果還沒有）
        if 'district_name' not in district_data[district_code]:
            district_data[district_code]['district_name'] = row['DistrictName']
        
        village_info = {
            'village_id': row['VillageID'],
            'village_name': row['VillageName'],
            'pred_cases': int(row['pred_cases'])
        }
        district_data[district_code]['villages'].append(village_info)

# 6. 對每個區域的村里按預測案例數排序
print("\n步驟 6: 對村里按嚴重程度排序...")
for district_code in district_data:
    villages = district_data[district_code]['villages']
    # 按預測案例數從多到少排序
    villages.sort(key=lambda x: x['pred_cases'], reverse=True)
    district_data[district_code]['villages'] = villages

# 7. 創建區域名稱到區域代碼的映射
print("\n步驟 7: 創建區域名稱映射...")
district_name_to_code = {}
for district_code, data in district_data.items():
    if 'district_name' in data:
        district_name_to_code[data['district_name']] = district_code

# 8. 準備輸出數據
output_data = {
    'latest_week': latest_week,
    'district_data': district_data,
    'district_name_to_code': district_name_to_code,
    'summary': {
        'total_districts': len(district_data),
        'total_villages': len(merged_data),
        'total_pred_cases': int(forecast_district_latest['pred_cases'].sum())
    }
}

# 9. 保存為JSON
print(f"\n步驟 8: 保存處理後的數據...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✓ 數據已保存到: {OUTPUT_FILE}")

# 10. 顯示統計信息
print("\n" + "=" * 60)
print("數據統計")
print("=" * 60)
print(f"預測週次: {latest_week}")
print(f"區域總數: {output_data['summary']['total_districts']}")
print(f"村里總數: {output_data['summary']['total_villages']}")
print(f"預測總病例: {output_data['summary']['total_pred_cases']}")

# 顯示病例最多的5個區域
print(f"\n病例最多的5個區域:")
district_sorted = sorted(
    district_data.items(),
    key=lambda x: x[1]['total_pred_cases'],
    reverse=True
)
for i, (code, data) in enumerate(district_sorted[:5], 1):
    district_name = data.get('district_name', '未知')
    cases = data['total_pred_cases']
    villages_count = len(data['villages'])
    print(f"  {i}. {district_name:8s}: {cases:5d} 例 ({villages_count} 個村里)")

# 顯示每個區域病例最多的村里
print(f"\n各區域病例最多的村里:")
for code, data in district_sorted[:5]:
    district_name = data.get('district_name', '未知')
    if data['villages']:
        top_village = data['villages'][0]
        print(f"  {district_name:8s}: {top_village['village_name']:10s} ({top_village['pred_cases']} 例)")

print("\n" + "=" * 60)
print("數據準備完成！")
print("=" * 60)
