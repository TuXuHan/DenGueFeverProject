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

def update_map():
    """執行 process_map.py 來更新地圖"""
    try:
        result = subprocess.run(
            ["python", str(PROCESS_MAP_SCRIPT)],
            cwd=str(DATA_DIR),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("地圖更新成功！")
        else:
            print(f"地圖更新失敗: {result.stderr}")
    except Exception as e:
        print(f"執行 process_map.py 時發生錯誤: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_map(request: Request):
    # 每次訪問首頁時更新地圖
    update_map()
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/api/update-map")
async def api_update_map():
    """手動更新地圖的 API"""
    update_map()
    return {"status": "success", "message": "地圖已更新"}