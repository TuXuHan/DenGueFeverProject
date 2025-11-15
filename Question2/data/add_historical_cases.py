#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加仁德區歷史確診數據到 forecast_data_processed.json
根據 village_ids_tainan.csv 匹配里名稱，並將里數據相加得到區級數據
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

print("=" * 60)
print("添加仁德區歷史確診數據...")
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

# 4. 按周組織數據
print("\n步驟 4: 按周組織數據...")
weekly_data = defaultdict(lambda: {
    'week_start': None,
    'district_total': 0,
    'villages': []
})

for _, row in rende_cases.iterrows():
    week_start = row['調查日期']
    village_id = row['VillageID']
    village_name = row['VillageName']
    cases = int(row['確診數'])
    
    if week_start not in weekly_data:
        weekly_data[week_start]['week_start'] = week_start
    
    # 添加村里數據
    village_entry = {
        'village_id': village_id,
        'village_name': village_name,
        'cases': cases
    }
    weekly_data[week_start]['villages'].append(village_entry)
    
    # 累加區級總數
    weekly_data[week_start]['district_total'] += cases

# 轉換為列表並按日期排序
historical_data = []
for week_start in sorted(weekly_data.keys()):
    week_data = weekly_data[week_start]
    # 對村里按確診數排序
    week_data['villages'].sort(key=lambda x: x['cases'], reverse=True)
    historical_data.append(week_data)

print(f"✓ 共 {len(historical_data)} 週的數據")

# 5. 讀取現有的 forecast_data_processed.json
print("\n步驟 5: 讀取現有的 forecast_data_processed.json...")
if OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        output_data = json.load(f)
    print(f"✓ 讀取現有數據")
else:
    print("⚠️  警告: forecast_data_processed.json 不存在，將創建新文件")
    output_data = {
        'latest_week': None,
        'district_data': {},
        'district_name_to_code': {},
        'summary': {
            'total_districts': 0,
            'total_villages': 0,
            'total_pred_cases': 0
        }
    }

# 6. 更新仁德區的數據
print("\n步驟 6: 更新仁德區的數據...")
district_code = '6702700'  # 仁德區的代碼

# 確保仁德區在 district_data 中存在
if district_code not in output_data['district_data']:
    output_data['district_data'][district_code] = {
        'district_code': district_code,
        'district_name': '仁德區',
        'total_pred_cases': 0,
        'villages': []
    }

# 添加歷史確診數據
output_data['district_data'][district_code]['historical_cases'] = historical_data

# 計算總確診數（所有周的總和）
total_historical_cases = sum(week['district_total'] for week in historical_data)
output_data['district_data'][district_code]['total_historical_cases'] = total_historical_cases

print(f"✓ 仁德區歷史確診數據已添加")
print(f"  - 總週數: {len(historical_data)}")
print(f"  - 總確診數: {total_historical_cases}")

# 7. 保存更新後的數據
print(f"\n步驟 7: 保存更新後的數據...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✓ 數據已保存到: {OUTPUT_FILE}")

# 8. 顯示統計信息
print("\n" + "=" * 60)
print("數據統計")
print("=" * 60)
print(f"仁德區歷史確診數據:")
print(f"  - 總週數: {len(historical_data)}")
print(f"  - 總確診數: {total_historical_cases}")
print(f"  - 村里數: {len(rende_village_mapping)}")

# 顯示確診數最多的5週
print(f"\n確診數最多的5週:")
weekly_totals = [(week['week_start'], week['district_total']) for week in historical_data]
weekly_totals.sort(key=lambda x: x[1], reverse=True)
for i, (week, total) in enumerate(weekly_totals[:5], 1):
    print(f"  {i}. {week}: {total} 例")

# 顯示確診數最多的5個里（所有周的總和）
print(f"\n確診數最多的5個里（所有周總和）:")
village_totals = defaultdict(int)
for week in historical_data:
    for village in week['villages']:
        village_totals[(village['village_id'], village['village_name'])] += village['cases']

village_totals_sorted = sorted(village_totals.items(), key=lambda x: x[1], reverse=True)
for i, ((village_id, village_name), total) in enumerate(village_totals_sorted[:5], 1):
    print(f"  {i}. {village_name}: {total} 例")

print("\n" + "=" * 60)
print("數據處理完成！")
print("=" * 60)

