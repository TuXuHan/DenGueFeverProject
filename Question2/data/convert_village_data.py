#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换和标准化村里 GeoJSON 数据
将 village_from_shp.geojson 转换为与系统兼容的格式
"""

import json
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("开始转换村里数据...")
print("=" * 60)

# 读取原始 Shapefile
print("\n步骤 1: 读取 Shapefile 数据...")
try:
    gdf = gpd.read_file('village/10_tn-village.shp', encoding='cp950')
    print(f"✓ 成功读取 {len(gdf)} 个村里")
except Exception as e:
    print(f"✗ 读取失败: {e}")
    exit(1)

# 检查并转换坐标系统
print("\n步骤 2: 转换坐标系统...")
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')
    print(f"✓ 已转换为 WGS84 (EPSG:4326)")
else:
    print(f"✓ 已是 WGS84 坐标系统")

# 标准化属性字段
print("\n步骤 3: 标准化属性字段...")

# 创建新的标准化属性
gdf['district_name'] = gdf['TOWN']  # 区域名称
gdf['village_name'] = gdf['VILLAGE']  # 村里名称
gdf['village_id'] = gdf['VILLAGE_ID']  # 村里ID
gdf['district_code'] = gdf['TOWN_ID']  # 区域代码
gdf['full_name'] = gdf['TOWN'] + gdf['VILLAGE']  # 完整名称

# 保留原有的有用字段
keep_columns = [
    'district_name',  # 区域名称（必需，用于匹配）
    'village_name',   # 村里名称（必需，用于显示）
    'village_id',     # 村里ID（必需，唯一标识）
    'district_code',  # 区域代码
    'full_name',      # 完整名称
    'COUNTY',         # 县市名称
    'TV_ALL',         # 完整地址
    'VILLCODE',       # 村里代码
    'AREA',           # 面积
    'V_ID',           # 村里唯一ID
    'geometry'        # 几何数据
]

# 选择需要的列
gdf_clean = gdf[keep_columns].copy()

print(f"✓ 标准化完成，保留 {len(keep_columns)-1} 个属性字段")

# 统计各区域的村里数量
print("\n步骤 4: 统计各区域村里数量...")
district_counts = gdf_clean['district_name'].value_counts().sort_index()
print(f"\n区域村里统计（共 {len(district_counts)} 个区域）：")
for district, count in district_counts.items():
    print(f"  {district:8s}: {count:3d} 个村里")

# 保存为标准化的 GeoJSON
output_file = 'village.geojson'
print(f"\n步骤 5: 保存为 {output_file}...")
gdf_clean.to_file(output_file, driver='GeoJSON', encoding='utf-8')
print(f"✓ 已保存到 {output_file}")

# 验证生成的文件
print("\n步骤 6: 验证生成的文件...")
with open(output_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✓ 文件类型: {data['type']}")
print(f"✓ 特征数量: {len(data['features'])}")
print(f"\n样本村里数据（第一个）：")
sample = data['features'][0]['properties']
for key, value in sample.items():
    if key != 'geometry':
        print(f"  {key:15s}: {value}")

# 创建备份
backup_file = 'village_standardized.geojson'
gdf_clean.to_file(backup_file, driver='GeoJSON', encoding='utf-8')
print(f"\n✓ 备份已保存到 {backup_file}")

print("\n" + "=" * 60)
print("转换完成！")
print("=" * 60)
print(f"\n生成的文件：")
print(f"  • {output_file} - 主文件，系统使用")
print(f"  • {backup_file} - 备份文件")
print(f"\n村里总数: {len(gdf_clean)}")
print(f"区域总数: {len(district_counts)}")

