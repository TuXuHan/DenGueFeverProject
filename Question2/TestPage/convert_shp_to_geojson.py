#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHP 轉換為 GeoJSON 工具
將 shapefile 轉換為 GeoJSON 格式，並轉換坐標系統為 WGS84
"""

import geopandas as gpd
import os
import json

def convert_shp_to_geojson(shp_path, output_path=None, target_crs="EPSG:4326"):
    """
    將 shapefile 轉換為 GeoJSON
    
    參數:
        shp_path: shapefile 路徑
        output_path: 輸出 GeoJSON 路徑（可選，默認為同名 .geojson）
        target_crs: 目標坐標系統（默認為 WGS84）
    """
    print(f"讀取 shapefile: {shp_path}")
    
    # 讀取 shapefile
    gdf = gpd.read_file(shp_path)
    
    # 顯示基本資訊
    print(f"✓ 讀取成功")
    print(f"  記錄數: {len(gdf)}")
    print(f"  欄位: {list(gdf.columns)}")
    print(f"  原始坐標系統: {gdf.crs}")
    
    # 轉換坐標系統（如果需要）
    if gdf.crs is None:
        print("⚠️  未設定坐標系統，假設為 TWD97 (EPSG:3826)")
        gdf = gdf.set_crs("EPSG:3826")
    
    if gdf.crs.to_string() != target_crs:
        print(f"轉換坐標系統: {gdf.crs} -> {target_crs}")
        gdf = gdf.to_crs(target_crs)
    
    # 確定輸出路徑
    if output_path is None:
        output_path = os.path.splitext(shp_path)[0] + '.geojson'
    
    # 顯示前幾筆資料
    print("\n前3筆資料範例:")
    for idx, row in gdf.head(3).iterrows():
        print(f"  {idx}: {dict(row.drop('geometry'))}")
    
    # 保存為 GeoJSON
    print(f"\n保存 GeoJSON: {output_path}")
    gdf.to_file(output_path, driver='GeoJSON', encoding='utf-8')
    
    # 驗證輸出
    file_size = os.path.getsize(output_path) / 1024  # KB
    print(f"✓ 轉換完成！")
    print(f"  輸出文件: {output_path}")
    print(f"  文件大小: {file_size:.2f} KB")
    
    # 顯示 GeoJSON 的前100個字符
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\nGeoJSON 內容預覽（前150字符）:")
        print(content[:150] + "...")
    
    return output_path

if __name__ == "__main__":
    # 當前目錄下的 shp 文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "10_tn-village.shp")
    
    if not os.path.exists(shp_file):
        print(f"❌ 找不到文件: {shp_file}")
        print(f"\n當前目錄的文件:")
        for f in os.listdir(script_dir):
            if f.endswith('.shp'):
                print(f"  - {f}")
    else:
        # 轉換為 GeoJSON (WGS84)
        output_file = os.path.join(script_dir, "10_tn-village.geojson")
        convert_shp_to_geojson(shp_file, output_file)
        
        print("\n" + "="*60)
        print("轉換完成！你現在可以使用這個 GeoJSON 文件了。")
        print("="*60)

