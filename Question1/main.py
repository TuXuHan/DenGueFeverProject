from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import time
from pathlib import Path

# 取得專案目錄
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "template"
WEB_DIR = BASE_DIR / "web"

app = FastAPI(
    title="Question1 地圖展示系統",
    version="1.0.0",
    description="基於 FastAPI 和 Leaflet 的地圖展示系統"
)

# 掛載靜態檔案
if WEB_DIR.exists():
    app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")

# 掛載數據檔案目錄
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# 缓存相关变量
_bucket_cache = None
_stat_cache = None
_cache_timestamp = 0
_cache_duration = 300  # 缓存5分钟（300秒）

def load_stat_data(force_reload=False):
    """
    載入 bucket_stat_converted.json 資料，带缓存机制
    
    Args:
        force_reload: 是否强制重新加载数据
    
    Returns:
        list: 监测点统计数据列表
    """
    global _stat_cache, _cache_timestamp
    
    current_time = time.time()
    
    # 检查缓存是否有效
    if not force_reload and _stat_cache is not None and (current_time - _cache_timestamp) < _cache_duration:
        print(f"使用统计数据缓存（缓存时间：{int(current_time - _cache_timestamp)}秒前）")
        return _stat_cache
    
    print("正在重新加载统计数据...")
    
    # 加载统计数据
    stat_file = DATA_DIR / "bucket_stat_converted.json"
    data = []
    
    if stat_file.exists():
        try:
            with open(stat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"載入統計資料：{len(data)} 個監測點")
        except Exception as e:
            print(f"載入統計資料時發生錯誤: {e}")
    
    # 更新缓存
    _stat_cache = data
    _cache_timestamp = current_time
    
    return data

def load_bucket_data(force_reload=False):
    """
    載入 bucket_converted.json 資料，带缓存机制
    
    Args:
        force_reload: 是否强制重新加载数据
    
    Returns:
        list: 监测点数据列表
    """
    global _bucket_cache, _cache_timestamp
    
    current_time = time.time()
    
    # 检查缓存是否有效
    if not force_reload and _bucket_cache is not None and (current_time - _cache_timestamp) < _cache_duration:
        print(f"使用桶子数据缓存（缓存时间：{int(current_time - _cache_timestamp)}秒前）")
        return _bucket_cache
    
    print("正在重新加载桶子数据...")
    
    # 加载桶子数据
    bucket_file = DATA_DIR / "bucket_converted.json"
    data = []
    
    if bucket_file.exists():
        try:
            with open(bucket_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"載入桶子資料：{len(data)} 個監測點")
        except Exception as e:
            print(f"載入桶子資料時發生錯誤: {e}")
    
    # 更新缓存
    _bucket_cache = data
    _cache_timestamp = current_time
    
    return data

@app.get("/", response_class=HTMLResponse)
async def read_map(request: Request):
    """首頁 - 顯示地圖"""
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/api/locations")
async def get_locations(data_type: str = "bucket"):
    """取得所有位置資料的 API
    
    Args:
        data_type: 数据类型 ("bucket" 或 "stat")
    """
    if data_type == "stat":
        data = load_stat_data()
    else:
        data = load_bucket_data()
    
    return {
        "status": "success",
        "data_type": data_type,
        "total": len(data),
        "data": data,
        "cache_info": {
            "cached": (_bucket_cache if data_type == "bucket" else _stat_cache) is not None,
            "cache_age_seconds": int(time.time() - _cache_timestamp) if _cache_timestamp > 0 else 0
        }
    }

@app.get("/api/locations/{location_id}")
async def get_location_by_id(location_id: int):
    """根據 ID 取得特定位置資料"""
    data = load_bucket_data()
    
    location = next((item for item in data if item.get("id") == location_id), None)
    
    if location:
        return {
            "status": "success",
            "data": location
        }
    else:
        return {
            "status": "error",
            "message": f"找不到 ID 為 {location_id} 的位置"
        }

@app.get("/api/locations/type/{location_type}")
async def get_locations_by_type(location_type: str):
    """根據類型取得位置資料"""
    data = load_bucket_data()
    
    filtered_data = [item for item in data if item.get("type") == location_type]
    
    return {
        "status": "success",
        "type": location_type,
        "total": len(filtered_data),
        "data": filtered_data
    }

@app.get("/api/reload-data")
async def reload_data(data_type: str = "bucket"):
    """手動重新載入數據"""
    global _bucket_cache, _stat_cache, _cache_timestamp
    
    # 清除缓存
    if data_type == "bucket":
        _bucket_cache = None
        data = load_bucket_data(force_reload=True)
    else:
        _stat_cache = None
        data = load_stat_data(force_reload=True)
    
    _cache_timestamp = 0
    
    return {
        "status": "success",
        "message": f"已重新載入 {data_type} 數據：{len(data)} 個監測點",
        "total": len(data),
        "data_type": data_type
    }

@app.get("/api/cache-info")
async def get_cache_info():
    """取得緩存資訊"""
    current_time = time.time()
    cache_age = int(current_time - _cache_timestamp) if _cache_timestamp > 0 else 0
    is_valid = cache_age < _cache_duration
    
    return {
        "bucket_cached": _bucket_cache is not None,
        "stat_cached": _stat_cache is not None,
        "cache_age_seconds": cache_age,
        "cache_duration_seconds": _cache_duration,
        "is_valid": is_valid,
        "bucket_data_count": len(_bucket_cache) if _bucket_cache else 0,
        "stat_data_count": len(_stat_cache) if _stat_cache else 0
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Question1 地圖展示系統")
    print("=" * 50)
    print(f"資料目錄: {DATA_DIR}")
    print(f"模板目錄: {TEMPLATE_DIR}")
    print("伺服器啟動中...")
    print("請在瀏覽器中訪問: http://127.0.0.1:8000")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)

