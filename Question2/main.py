from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import os
from config import (
    FASTAPI_CONFIG, STATIC_MOUNTS, WEB_DIR, DATA_DIR, TEMPLATE_DIR,
    PROCESS_MAP_SCRIPT, APP_NAME
)

app = FastAPI(
    title=FASTAPI_CONFIG["title"],
    version=FASTAPI_CONFIG["version"],
    description=FASTAPI_CONFIG["description"]
)

# 使用設定檔中的靜態檔案掛載點
for mount_path, directory in STATIC_MOUNTS.items():
    app.mount(mount_path, StaticFiles(directory=directory), name=mount_path[1:])

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

def update_data():
    """執行數據準備腳本來更新預測數據"""
    try:
        print("正在更新預測數據...")
        prepare_script = DATA_DIR / "prepare_forecast_data.py"
        result = subprocess.run(
            ["python", str(prepare_script)],
            cwd=str(DATA_DIR),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ 預測數據更新成功！")
        else:
            print(f"✗ 預測數據更新失敗: {result.stderr}")
    except Exception as e:
        print(f"執行 prepare_forecast_data.py 時發生錯誤: {e}")

def update_map(language="zh"):
    """執行 process_map.py 來更新地圖（包含村里顯示功能）"""
    try:
        print(f"正在更新地圖（包含 752 個村里資料，語言: {language}）...")
        env = os.environ.copy()
        env['LANGUAGE'] = language
        result = subprocess.run(
            ["python", str(PROCESS_MAP_SCRIPT)],
            cwd=str(DATA_DIR),
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode == 0:
            print("✓ 地圖更新成功！")
        else:
            print(f"✗ 地圖更新失敗: {result.stderr}")
    except Exception as e:
        print(f"執行 process_map.py 時發生錯誤: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_map(request: Request, lang: str = "zh"):
    # 每次訪問首頁時更新數據和地圖
    update_data()  # 先更新預測數據
    update_map(lang)   # 再更新地圖，使用指定的語言
    return templates.TemplateResponse("map.html", {"request": request, "language": lang})

@app.get("/api/update-map")
async def api_update_map(lang: str = "zh"):
    """手動更新數據和地圖的 API"""
    update_data()  # 先更新預測數據
    update_map(lang)   # 再更新地圖，使用指定的語言
    return {"status": "success", "message": f"數據和地圖已更新（語言: {lang}）"}

@app.get("/api/villages")
async def get_villages():
    """取得所有村里資料（用於地圖顯示）"""
    import json
    village_file = DATA_DIR / "village.geojson"
    
    if not village_file.exists():
        return {"error": "村里資料檔案不存在"}
    
    try:
        with open(village_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "status": "success",
            "total": len(data["features"]),
            "data": data
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/villages/{district_name}")
async def get_villages_by_district(district_name: str):
    """根據區域名稱取得該區域的所有村里"""
    import json
    village_file = DATA_DIR / "village.geojson"
    
    if not village_file.exists():
        return {"error": "村里資料檔案不存在"}
    
    try:
        with open(village_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 過濾出指定區域的村里
        district_villages = [
            f for f in data["features"]
            if f["properties"].get("district_name") == district_name
        ]
        
        return {
            "status": "success",
            "district": district_name,
            "total": len(district_villages),
            "villages": district_villages
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/forecast-data")
async def get_forecast_data():
    """取得登革熱預測數據"""
    import json
    forecast_file = DATA_DIR / "forecast_data_processed.json"
    
    if not forecast_file.exists():
        return {"error": "預測數據檔案不存在"}
    
    try:
        with open(forecast_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "status": "success",
            "latest_week": data.get("latest_week", "unknown"),
            "district_count": len(data.get("district_data", {})),
            "data": data
        }
    except Exception as e:
        return {"error": str(e)}