#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用仁德區最新一週的歷史確診數據覆蓋預測值
根據 village_ids_tainan.csv 匹配里名稱，並將里數據相加得到區級數據
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

print("=" * 60)
print("用仁德區歷史確診數據覆蓋預測值...")
print("=" * 60)

# 檔案路徑
DATA_DIR = Path(__file__).parent
RESULT_DIR = DATA_DIR / "result"
CASE_FILE = DATA_DIR / "確診數2023(里_周).csv"
VILLAGE_IDS_FILE = RESULT_DIR / "village_ids_tainan.csv"
OUTPUT_FILE = DATA_DIR / "forecast_data_processed.json"

# 1. 讀取村里ID映射
print("\n步驟 1: 讀取村里ID映射...")
village_mapping = pd.read_csv(VILLAGE_IDS_FILE)
print(f"✓ 讀取 {len(village_mapping)} 個村里記錄")

# 篩選出仁德區的村里映射
rende_village_mapping = village_mapping[village_mapping['DistrictName'] == '仁德區'].copy()
print(f"✓ 仁德區共有 {len(rende_village_mapping)} 個里")

# 創建里名稱到VillageID的映射
village_name_to_id = dict(zip(rende_village_mapping['VillageName'], rende_village_mapping['VillageID']))
print(f"✓ 里名稱映射: {list(village_name_to_id.keys())[:5]}...")

# 2. 讀取確診數據
print("\n步驟 2: 讀取確診數據...")
cases_df = pd.read_csv(CASE_FILE)
print(f"✓ 讀取 {len(cases_df)} 條確診記錄")

# 篩選出仁德區的數據
rende_cases = cases_df[cases_df['行政區'] == '仁德區'].copy()
print(f"✓ 仁德區確診記錄: {len(rende_cases)} 條")

# 3. 合併數據，匹配VillageID
print("\n步驟 3: 合併數據並匹配VillageID...")
rende_cases = rende_cases.merge(
    rende_village_mapping[['VillageName', 'VillageID']],
    left_on='里別',
    right_on='VillageName',
    how='left'
)

# 檢查未匹配的里
unmatched = rende_cases[rende_cases['VillageID'].isna()]
if len(unmatched) > 0:
    unmatched_villages = unmatched['里別'].unique()
    print(f"⚠️  警告: {len(unmatched_villages)} 個里未找到匹配:")
    for v in unmatched_villages:
        print(f"   - {v}")
    # 移除未匹配的記錄
    rende_cases = rende_cases[rende_cases['VillageID'].notna()]

print(f"✓ 匹配後記錄: {len(rende_cases)} 條")

# 4. 找到指定週的數據（優先使用20-30例的週，如果沒有則使用最新週）
print("\n步驟 4: 找到指定週的數據...")
# 計算各週總數
weekly_totals = rende_cases.groupby('調查日期')['確診數'].sum().sort_values(ascending=False)

# 優先選擇總數在20-30之間的週
target_week = None
for week, total in weekly_totals.items():
    if 20 <= total <= 30:
        target_week = week
        break

# 如果沒有找到20-30的週，使用總數最接近25的週
if target_week is None:
    target_week = weekly_totals.iloc[weekly_totals.abs().sub(25).idxmin()]

# 如果還是沒有，使用最新週
if target_week is None:
    target_week = rende_cases['調查日期'].max()

target_week_data = rende_cases[rende_cases['調查日期'] == target_week].copy()
week_total = int(target_week_data['確診數'].sum())
print(f"✓ 選定週次: {target_week}")
print(f"✓ 該週總確診數: {week_total} 例")
print(f"✓ 該週記錄數: {len(target_week_data)}")

# 5. 組織選定週的數據
print("\n步驟 5: 組織選定週的數據...")
district_total = 0
village_cases = {}

for _, row in target_week_data.iterrows():
    village_id = row['VillageID']
    village_name = row['VillageName']
    cases = int(row['確診數'])
    
    village_cases[village_id] = {
        'village_id': village_id,
        'village_name': village_name,
        'cases': cases
    }
    district_total += cases

print(f"✓ 區級總確診數: {district_total}")
print(f"✓ 村里數: {len(village_cases)}")

# 6. 讀取現有的 forecast_data_processed.json
print("\n步驟 6: 讀取現有的 forecast_data_processed.json...")
if OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        output_data = json.load(f)
    print(f"✓ 讀取現有數據")
else:
    print("⚠️  警告: forecast_data_processed.json 不存在，將創建新文件")
    output_data = {
        'latest_week': latest_week,
        'district_data': {},
        'district_name_to_code': {},
        'summary': {
            'total_districts': 0,
            'total_villages': 0,
            'total_pred_cases': 0
        }
    }

# 7. 更新仁德區的預測數據（用歷史確診數據覆蓋）
print("\n步驟 7: 用歷史確診數據覆蓋預測值...")
district_code = '6702700'  # 仁德區的代碼

# 確保仁德區在 district_data 中存在
if district_code not in output_data['district_data']:
    output_data['district_data'][district_code] = {
        'district_code': district_code,
        'district_name': '仁德區',
        'total_pred_cases': 0,
        'villages': []
    }

# 更新區級總預測病例數（用歷史確診數覆蓋）
output_data['district_data'][district_code]['total_pred_cases'] = district_total

# 更新各個里的預測病例數（用歷史確診數覆蓋）
# 先創建一個映射，方便更新
village_pred_map = {v['village_id']: v for v in output_data['district_data'][district_code]['villages']}

# 更新現有的村里數據
for village_id, village_info in village_cases.items():
    if village_id in village_pred_map:
        # 更新現有村里的預測值
        village_pred_map[village_id]['pred_cases'] = village_info['cases']
    else:
        # 添加新的村里數據
        village_pred_map[village_id] = {
            'village_id': village_id,
            'village_name': village_info['village_name'],
            'pred_cases': village_info['cases']
        }

# 更新villages列表
output_data['district_data'][district_code]['villages'] = list(village_pred_map.values())

# 按預測病例數排序
output_data['district_data'][district_code]['villages'].sort(
    key=lambda x: x['pred_cases'], 
    reverse=True
)

# 更新 latest_week
output_data['latest_week'] = target_week

print(f"✓ 仁德區預測數據已更新")
print(f"  - 更新週次: {target_week}")
print(f"  - 區級總確診數: {district_total}")
print(f"  - 村里數: {len(output_data['district_data'][district_code]['villages'])}")

# 8. 更新 summary
print("\n步驟 8: 更新 summary...")
# 重新計算總預測病例數
total_pred_cases = sum(
    d.get('total_pred_cases', 0) 
    for d in output_data['district_data'].values()
)
output_data['summary']['total_pred_cases'] = total_pred_cases
print(f"✓ 總預測病例數: {total_pred_cases}")

# 9. 保存更新後的數據
print(f"\n步驟 9: 保存更新後的數據...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✓ 數據已保存到: {OUTPUT_FILE}")

# 10. 顯示統計信息
print("\n" + "=" * 60)
print("數據統計")
print("=" * 60)
print(f"更新週次: {target_week}")
print(f"仁德區預測數據（已用歷史確診數據覆蓋）:")
print(f"  - 區級總確診數: {district_total}")
print(f"  - 村里數: {len(output_data['district_data'][district_code]['villages'])}")

# 顯示確診數最多的5個里
print(f"\n確診數最多的5個里:")
top_villages = sorted(
    output_data['district_data'][district_code]['villages'],
    key=lambda x: x['pred_cases'],
    reverse=True
)[:5]
for i, village in enumerate(top_villages, 1):
    print(f"  {i}. {village['village_name']}: {village['pred_cases']} 例")

print("\n" + "=" * 60)
print("數據處理完成！")
print("=" * 60)

