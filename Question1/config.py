"""
Question1 登革熱監測點位系統 - 配置文件
"""
import os
from pathlib import Path

# =============================================================================
# 基本系統設定
# =============================================================================

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.absolute()

# 應用程式基本設定
APP_NAME = "台南登革熱資料預測"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "台南市登革热監測點展示系統"

# =============================================================================
# 目錄結構設定
# =============================================================================

# 資料集
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATE_DIR = PROJECT_ROOT / "template"
WEB_DIR = PROJECT_ROOT / "web"

# 檔案路徑
BUCKET_JSON = DATA_DIR / "bucket.json"
BUCKET_CONVERTED_JSON = DATA_DIR / "bucket_converted.json"

# =============================================================================
# 伺服器設定
# =============================================================================

# FastAPI 設定
FASTAPI_CONFIG = {
    "title": APP_NAME,
    "version": APP_VERSION,
    "description": APP_DESCRIPTION,
    "host": "127.0.0.1",
    "port": 8000,
    "reload": True,
}

# 靜態檔案掛載
STATIC_MOUNTS = {
    "/web": str(WEB_DIR),
}

# =============================================================================
# 地圖設定
# =============================================================================

# 地圖基本設定
MAP_CONFIG = {
    "center": [23.143297, 120.240932],  # 台南市中心
    "zoom_start": 11,
    "tile_url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "tile_attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}

# =============================================================================
# 資料更新設定
# =============================================================================

# 資料來源設定
DATA_SOURCES = {
    "tainan_data_url": "https://data.tainan.gov.tw/DataSet/Detail/4ad2dba4-4fed-4224-9456-c6ac776cb1cd",
    "data_titles": ["誘卵桶點位"],
    "update_interval_hours": 6,  # 每6小时更新一次
}

# Selenium 設定
SELENIUM_CONFIG = {
    "headless": True,
    "wait_timeout": 3,
    "scroll_delay": 0.5,
    "max_retries": 10,
}

# =============================================================================
# UI 設定
# =============================================================================

# 頁面標題和文字
UI_TEXT = {
    "page_title": "台南登革熱資料預測",
    "monitoring_points_label": "登革熱監測點",
}

# 顏色主題
COLOR_THEME = {
    "primary_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "monitoring_point_color": "#667eea",
}

# =============================================================================
# 座標轉換設定
# =============================================================================

# 座標系統設定
COORDINATE_SYSTEM = {
    "input_crs": "EPSG:3826",  # TWD97 台湾坐标系统
    "output_crs": "EPSG:4326",  # WGS84 (经纬度)
}

# =============================================================================
# 工具函数
# =============================================================================

def get_config_value(key_path: str, default=None):
    """
    取得設定值的工具函數
    
    Args:
        key_path: 設定路徑,例如 'MAP_CONFIG.center'
        default: 预设值
    
    Returns:
        設定值
    """
    keys = key_path.split('.')
    value = globals()
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def validate_config():
    """
    驗證配置文件的有效性
    """
    errors = []
    
    # 檢查必要目錄是否存在
    required_dirs = [DATA_DIR, TEMPLATE_DIR]
    for dir_path in required_dirs:
        if not dir_path.exists():
            errors.append(f"目录不存在: {dir_path}")
    
    # 檢查地圖設定
    if not isinstance(MAP_CONFIG["center"], list) or len(MAP_CONFIG["center"]) != 2:
        errors.append("地圖中心點設定錯誤")
    
    if errors:
        raise ValueError(f"配置文件驗證失敗: {', '.join(errors)}")
    
    return True

# 自動驗證設定
if __name__ == "__main__":
    try:
        validate_config()
        print("✅ 配置文件驗證通過")
    except ValueError as e:
        print(f"❌ 配置文件驗證失敗: {e}")
