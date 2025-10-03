"""
登革熱疫情資料系統 - 統一設定檔
這個檔案包含了系統中所有的UI設定,路徑設定,API設定等參數
使用者可以根據需要修改這些設定來客製化系統
"""

import os
from pathlib import Path

# =============================================================================
# 基本系統設定
# =============================================================================

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.absolute()

# 應用程式基本設定
APP_NAME = "台南市登革熱疫情資料系統"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "台南市登革熱疫情監控與視覺化系統"

# =============================================================================
# 目錄結構設定
# =============================================================================

# 資料目錄
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATE_DIR = PROJECT_ROOT / "template"
WEB_DIR = PROJECT_ROOT / "web"

# 檔案路徑
BUCKET_JSON = DATA_DIR / "bucket.json"
PROCESS_MAP_SCRIPT = DATA_DIR / "process_map.py"
DENGUE_DATA_JSON = DATA_DIR / "dengue_data.json"
DISTRICT_DATA_JSON = DATA_DIR / "district_data.json"
DISTRICTS_SUMMARY_JSON = DATA_DIR / "districts_summary.json"
OVITRAP_DATA_JSON = DATA_DIR / "ovitrap_data.json"
WEATHER_DATA_JSON = DATA_DIR / "weather_data.json"
VILLAGE_LIST_CSV = DATA_DIR / "village_list.csv"

# 地圖相關檔案
MAP_TEMP_HTML = TEMPLATE_DIR / "map_temp.html"
MAP_HTML = TEMPLATE_DIR / "map.html"
SCRIPT_JS = TEMPLATE_DIR / "script.js"
DISTRICT_BOUNDARIES_GEOJSON = DATA_DIR / "district_boundaries.geojson"
TAINAN_TOWN_SHP = DATA_DIR / "tainan_town.shp"

# 樣式檔案
STYLE_CSS = WEB_DIR / "style.css"

# =============================================================================
# Web 伺服器設定
# =============================================================================

# FastAPI 設定
FASTAPI_CONFIG = {
    "title": APP_NAME,
    "version": APP_VERSION,
    "description": APP_DESCRIPTION,
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
}

# 靜態檔案掛載點
STATIC_MOUNTS = {
    "/Home": str(WEB_DIR),
    "/data": str(DATA_DIR),
    "/template": str(TEMPLATE_DIR),
}

# =============================================================================
# 地圖設定
# =============================================================================

# 地圖基本設定
MAP_CONFIG = {
    # 地圖中心點 (台南市) - 當 use_dynamic_center 為 False 時使用
    "center": [23.126724381730643, 120.37003378640675],
    "use_dynamic_center": True,  # 設為 True 從地理資料動態計算中心點,False 使用上方預設中心點
    "zoom_start": 10.5,
    "zoom_control": True,
    "prefer_canvas": False,
    
    # 地圖圖磚設定
    "tile_url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    "tile_min_zoom": 0,
    "tile_max_zoom": 19,
    "tile_max_native_zoom": 19,
    "tile_no_wrap": False,
    "tile_attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    "tile_subdomains": "abc",
    "tile_detect_retina": False,
    "tile_tms": False,
    "tile_opacity": 1,
}

# 行政區樣式設定
DISTRICT_STYLE = {
    "default": {
        "color": "#1f78b4",
        "weight": 2,
        "fill_opacity": 0,
        "opacity": 1,
        "stroke": True,
        "line_join": "round",
        "line_cap": "round",
    },
    "highlighted": {
        "color": "#ff6b6b",
        "weight": 3,
        "fill_opacity": 0.3,
        "opacity": 1,
    },
    "selected": {
        "color": "#4ecdc4",
        "weight": 3,
        "fill_opacity": 0.5,
        "opacity": 1,
    }
}

# 座標系統設定
COORDINATE_SYSTEM = {
    "input_crs": "EPSG:3826",  # 台灣座標系統
    "output_crs": "EPSG:4326",  # WGS84 (經緯度)
}

# =============================================================================
# UI 設定
# =============================================================================

# 頁面標題和文字
UI_TEXT = {
    "page_title": "台南市登革熱疫情資料",
    "sidebar_title": "行政區列表",
    "sidebar_icon": "fas fa-map-marked-alt",
    "population_label": "人口數據",
    "dengue_cases_label": "登革熱病例",
    "rate_per_10k_label": "每萬人病例率",
    "risk_level_label": "風險等級",
    "last_update_label": "更新時間",
}

# 顏色主題
COLOR_THEME = {
    # 漸層色彩
    "primary_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "header_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    
    # 基本色彩
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "accent_color": "#1f78b4",
    "success_color": "#4ecdc4",
    "warning_color": "#ff6b6b",
    "danger_color": "#ff4757",
    
    # 文字色彩
    "text_primary": "#333333",
    "text_secondary": "#666666",
    "text_light": "#999999",
    "text_white": "#ffffff",
    
    # 背景色彩
    "bg_primary": "#ffffff",
    "bg_secondary": "#f8f9fa",
    "bg_tertiary": "#e9ecef",
    "bg_overlay": "rgba(255, 255, 255, 0.95)",
}

# 版面配置
LAYOUT_CONFIG = {
    # 標題區域
    "header": {
        "position": "absolute",
        "top": "10px",
        "left": "10px",
        "z_index": 1000,
        "background": "rgba(255, 255, 255, 0.9)",
        "padding": "15px",
        "border_radius": "8px",
        "box_shadow": "0 2px 10px rgba(0,0,0,0.3)",
    },
    
    # 側邊欄
    "sidebar": {
        "position": "absolute",
        "left": "10px",
        "top": "80px",
        "bottom": "10px",
        "width": "300px",
        "background": "rgba(255, 255, 255, 0.98)",
        "padding": "20px",
        "box_shadow": "0 4px 20px rgba(0,0,0,0.15)",
        "overflow_y": "auto",
        "border_radius": "12px",
        "z_index": 1000,
        "border": "1px solid rgba(102, 126, 234, 0.1)",
    },
    
    # 資訊面板
    "info_panel": {
        "position": "absolute",
        "top": "10px",
        "right": "10px",
        "width": "300px",
        "background": "rgba(255, 255, 255, 0.95)",
        "padding": "15px",
        "box_shadow": "0 2px 10px rgba(0,0,0,0.3)",
        "border_radius": "8px",
        "z_index": 1000,
        "display": "none",
    },
    
    # 地圖區域
    "map": {
        "position": "absolute",
        "top": "0",
        "left": "320px",
        "right": "0",
        "bottom": "0",
    }
}

# 字體設定
FONT_CONFIG = {
    "header_size": "24px",
    "sidebar_title_size": "20px",
    "content_size": "14px",
    "small_size": "12px",
    "font_weight_bold": "bold",
    "font_weight_normal": "normal",
    "font_weight_medium": "600",
}

# =============================================================================
# 資料更新設定
# =============================================================================

# 資料來源設定
DATA_SOURCES = {
    "tainan_data_url": "https://data.tainan.gov.tw/DataSet/Detail/4ad2dba4-4fed-4224-9456-c6ac776cb1cd",
    "data_titles": ["誘卵桶點位"],
    "update_interval_hours": 6,  # 每6小時更新一次
}

# Selenium 設定
SELENIUM_CONFIG = {
    "headless": True,
    "wait_timeout": 3,
    "scroll_delay": 0.5,
    "max_retries": 10,
}

# =============================================================================
# 風險等級設定
# =============================================================================

# 風險等級顏色
RISK_COLORS = {
    "high": "#ff4757",      # 高風險 - 紅色
    "medium": "#ffa502",    # 中風險 - 橙色
    "low": "#2ed573",       # 低風險 - 綠色
    "very_low": "#3742fa",  # 極低風險 - 藍色
}

# 風險等級閾值 (每萬人病例數)
RISK_THRESHOLDS = {
    "high": 10,      # 高風險:每萬人10例以上
    "medium": 5,     # 中風險:每萬人5-10例
    "low": 1,        # 低風險:每萬人1-5例
    "very_low": 0,   # 極低風險:每萬人1例以下
}

# =============================================================================
# API 設定
# =============================================================================

# 外部 API 設定
EXTERNAL_APIS = {
    "weather_api": {
        "base_url": "https://codis.cwa.gov.tw/api/station",
        "timeout": 30,
        "retry_count": 3,
    }
}

# =============================================================================
# 快取設定
# =============================================================================

CACHE_CONFIG = {
    "enable_cache_busting": True,
    "cache_duration_hours": 1,
    "static_file_cache": True,
}

# =============================================================================
# 日誌設定
# =============================================================================

LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": PROJECT_ROOT / "logs" / "system.log",
    "max_file_size_mb": 10,
    "backup_count": 5,
}

# =============================================================================
# 安全設定
# =============================================================================

SECURITY_CONFIG = {
    "cors_origins": ["*"],
    "cors_methods": ["GET", "POST", "PUT", "DELETE"],
    "cors_headers": ["Content-Type"],
    "rate_limit": {
        "enabled": False,
        "requests_per_minute": 60,
    }
}

# =============================================================================
# 開發模式設定
# =============================================================================

DEBUG_CONFIG = {
    "debug_mode": False,
    "auto_reload": True,
    "show_error_details": True,
    "enable_profiling": False,
}

# =============================================================================
# 工具函數
# =============================================================================

def get_config_value(key_path: str, default=None):
    """
    取得設定值的工具函數
    
    Args:
        key_path: 設定路徑,例如 'MAP_CONFIG.center'
        default: 預設值
    
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

def update_config(key_path: str, new_value):
    """
    更新設定值的工具函數
    
    Args:
        key_path: 設定路徑,例如 'MAP_CONFIG.center'
        new_value: 新值
    """
    keys = key_path.split('.')
    config = globals()
    
    for key in keys[:-1]:
        config = config[key]
    
    config[keys[-1]] = new_value

def validate_config():
    """
    驗證設定檔的有效性
    """
    errors = []
    
    # 檢查必要目錄是否存在
    required_dirs = [DATA_DIR, TEMPLATE_DIR, WEB_DIR]
    for dir_path in required_dirs:
        if not dir_path.exists():
            errors.append(f"目錄不存在: {dir_path}")
    
    # 檢查地圖設定
    if not isinstance(MAP_CONFIG["center"], list) or len(MAP_CONFIG["center"]) != 2:
        errors.append("地圖中心點設定錯誤")
    
    # 檢查風險等級設定
    if not all(isinstance(v, (int, float)) for v in RISK_THRESHOLDS.values()):
        errors.append("風險等級閾值必須為數字")
    
    if errors:
        raise ValueError(f"設定檔驗證失敗: {', '.join(errors)}")
    
    return True

# 自動驗證設定
if __name__ == "__main__":
    try:
        validate_config()
        print("✅ 設定檔驗證通過")
    except ValueError as e:
        print(f"❌ 設定檔驗證失敗: {e}")
