import json
from pyproj import Transformer

# 讀取 bucket.json
with open("bucket.json", "r", encoding="utf-8") as f:
    data = json.load(f)["data"]

# 建立 TWD97 -> WGS84 轉換器
# 台灣常用投影 EPSG:3826 (TWD97 TM2 zone 121)
transformer = Transformer.from_crs("EPSG:3826", "EPSG:4326", always_xy=True)

# 執行轉換
for item in data:
    x = item["TWD97_X"]
    y = item["TWD97_Y"]
    lon, lat = transformer.transform(x, y)
    item["lat"] = lat
    item["lon"] = lon

# 儲存成新檔
with open("bucket_converted.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("轉換完成，結果已輸出到 bucket_converted.json")
