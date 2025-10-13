
import geopandas as gpd
import sys
import os
import argparse
from pathlib import Path

# 添加專案根目錄到路徑，以便導入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import COORDINATE_SYSTEM
except ImportError:
    # 如果無法導入 config，使用預設設定
    COORDINATE_SYSTEM = {
        "input_crs": "EPSG:4326",  # WGS84
        "output_crs": "EPSG:4326"  # WGS84
    }

def convert_shapefile_to_geojson(input_file, output_file, input_crs=None, output_crs=None):
    """
    將 Shapefile 轉換為 GeoJSON
    
    Args:
        input_file (str): 輸入的 .shp 或 .shx 檔案路徑
        output_file (str): 輸出的 .geojson 檔案路徑
        input_crs (str): 輸入檔案的座標系統 (可選)
        output_crs (str): 輸出檔案的座標系統 (可選)
    
    Returns:
        bool: 轉換是否成功
    """
    try:
        print(f"開始轉換: {input_file} -> {output_file}")
        
        # 檢查輸入檔案是否存在
        if not os.path.exists(input_file):
            print(f"錯誤: 輸入檔案不存在: {input_file}")
            return False
        
        # 讀取 Shapefile
        print("正在讀取 Shapefile...")
        gdf = gpd.read_file(input_file)
        
        print(f"成功讀取 Shapefile，包含 {len(gdf)} 個要素")
        print(f"欄位: {list(gdf.columns)}")
        
        # 顯示前幾筆資料的資訊
        if len(gdf) > 0:
            print("前3筆資料的屬性:")
            for i in range(min(3, len(gdf))):
                print(f"  要素 {i}: {gdf.iloc[i].to_dict()}")
        
        # 處理座標系統
        if input_crs or output_crs:
            input_crs = input_crs or COORDINATE_SYSTEM["input_crs"]
            output_crs = output_crs or COORDINATE_SYSTEM["output_crs"]
            
            print(f"處理座標系統轉換: {input_crs} -> {output_crs}")
            
            # 設定輸入座標系統
            if gdf.crs is None:
                gdf = gdf.set_crs(input_crs)
                print(f"設定輸入座標系統: {input_crs}")
            
            # 轉換座標系統
            if gdf.crs.to_string() != output_crs:
                gdf = gdf.to_crs(output_crs)
                print(f"座標系統轉換完成: {gdf.crs}")
        
        # 計算邊界框
        bounds = gdf.total_bounds
        print(f"資料邊界框: [{bounds[0]:.6f}, {bounds[1]:.6f}, {bounds[2]:.6f}, {bounds[3]:.6f}]")
        
        # 計算中心點
        center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]
        print(f"中心點: [{center[0]:.6f}, {center[1]:.6f}]")
        
        # 確保輸出目錄存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 轉換為 GeoJSON 並儲存
        print("正在轉換為 GeoJSON...")
        gdf.to_file(output_file, driver="GeoJSON", encoding="utf-8")
        
        print(f"✅ 轉換成功完成!")
        print(f"輸出檔案: {output_file}")
        
        # 驗證輸出檔案
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"檔案大小: {file_size:,} bytes")
            
            # 讀取並顯示 GeoJSON 資訊
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    import json
                    geojson_data = json.load(f)
                    print(f"GeoJSON 要素數量: {len(geojson_data.get('features', []))}")
                    
                    if geojson_data.get('features'):
                        first_feature = geojson_data['features'][0]
                        print(f"第一個要素的屬性: {first_feature.get('properties', {})}")
            except Exception as e:
                print(f"警告: 無法驗證 GeoJSON 檔案: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 轉換失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="將 Shapefile 轉換為 GeoJSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
    python process_map.py input.shp output.geojson
    python process_map.py input.shx output.geojson
    python process_map.py --input-crs EPSG:3826 --output-crs EPSG:4326 input.shp output.geojson
        """
    )
    
    parser.add_argument('input_file', help='輸入的 .shp 或 .shx 檔案路徑')
    parser.add_argument('output_file', help='輸出的 .geojson 檔案路徑')
    parser.add_argument('--input-crs', help='輸入檔案的座標系統 (例如: EPSG:3826)')
    parser.add_argument('--output-crs', help='輸出檔案的座標系統 (例如: EPSG:4326)')
    
    args = parser.parse_args()
    
    # 檢查輸入檔案副檔名
    input_ext = Path(args.input_file).suffix.lower()
    if input_ext not in ['.shp', '.shx']:
        print(f"警告: 輸入檔案副檔名為 {input_ext}，建議使用 .shp 或 .shx")
    
    # 檢查輸出檔案副檔名
    output_ext = Path(args.output_file).suffix.lower()
    if output_ext != '.geojson':
        print(f"警告: 輸出檔案副檔名為 {output_ext}，建議使用 .geojson")
    
    # 執行轉換
    success = convert_shapefile_to_geojson(
        args.input_file, 
        args.output_file,
        args.input_crs,
        args.output_crs
    )
    
    if success:
        print("\n🎉 轉換完成！現在可以在 HTML 中使用這個 GeoJSON 檔案了。")
        sys.exit(0)
    else:
        print("\n💥 轉換失敗！請檢查錯誤訊息。")
        sys.exit(1)

if __name__ == "__main__":
    main()
