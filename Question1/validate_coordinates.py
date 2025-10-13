"""
验证坐标转换结果的脚本
"""
import json

def validate_coordinates():
    """验证转换后的坐标数据"""
    
    # 台南市的大致坐标范围
    TAINAN_BOUNDS = {
        'min_lat': 22.8,
        'max_lat': 23.4,
        'min_lng': 120.1,
        'max_lng': 120.5
    }
    
    try:
        with open('data/bucket_converted.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("=" * 60)
        print("坐标验证报告")
        print("=" * 60)
        
        print(f"总监测点数: {len(data)}")
        
        # 统计坐标范围
        lats = [point['latitude'] for point in data]
        lngs = [point['longitude'] for point in data]
        
        print(f"\n坐标范围:")
        print(f"纬度: {min(lats):.6f} ~ {max(lats):.6f}")
        print(f"经度: {min(lngs):.6f} ~ {max(lngs):.6f}")
        
        # 检查是否在台南市范围内
        out_of_bounds = []
        for point in data:
            lat, lng = point['latitude'], point['longitude']
            if (lat < TAINAN_BOUNDS['min_lat'] or lat > TAINAN_BOUNDS['max_lat'] or
                lng < TAINAN_BOUNDS['min_lng'] or lng > TAINAN_BOUNDS['max_lng']):
                out_of_bounds.append(point)
        
        if out_of_bounds:
            print(f"\n⚠️  发现 {len(out_of_bounds)} 个超出台南市范围的监测点:")
            for point in out_of_bounds[:5]:  # 只显示前5个
                print(f"  {point['name']}: ({point['latitude']:.6f}, {point['longitude']:.6f})")
            if len(out_of_bounds) > 5:
                print(f"  ... 还有 {len(out_of_bounds) - 5} 个")
        else:
            print("\n✅ 所有监测点都在台南市范围内")
        
        # 检查重复坐标
        coordinates = [(p['latitude'], p['longitude']) for p in data]
        unique_coords = set(coordinates)
        
        if len(coordinates) != len(unique_coords):
            print(f"\n⚠️  发现 {len(coordinates) - len(unique_coords)} 个重复坐标")
        else:
            print("\n✅ 没有重复坐标")
        
        # 显示一些样本点
        print(f"\n样本监测点:")
        for i in range(min(5, len(data))):
            point = data[i]
            print(f"  {i+1}. {point['name']}")
            print(f"     坐标: ({point['latitude']:.6f}, {point['longitude']:.6f})")
            print(f"     区域: {point['district']} {point['village']}")
        
        print("\n" + "=" * 60)
        print("验证完成")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"验证过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    validate_coordinates()
