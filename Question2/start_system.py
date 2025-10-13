#!/usr/bin/env python3
"""
登革熱疫情資料系統啟動腳本
這個腳本會自動檢查環境,安裝依賴,配置設定並啟動系統
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """顯示歡迎訊息"""
    print("=" * 60)
    print("🦟 登革熱疫情資料系統 - 自動啟動器")
    print("=" * 60)
    print()

def check_python_version():
    """檢查 Python 版本"""
    print("🔍 檢查 Python 版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 錯誤:需要 Python 3.8 或更高版本")
        print(f"   目前版本:{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python 版本:{version.major}.{version.minor}.{version.micro}")
    return True

def check_and_install_dependencies():
    """檢查並安裝依賴套件"""
    print("\n📦 檢查依賴套件...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'folium', 'geopandas', 
        'pandas', 'selenium', 'requests', 'jinja2', 
        'webdriver-manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安裝)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 安裝缺失的套件:{', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ 套件安裝完成")
        except subprocess.CalledProcessError:
            print("❌ 套件安裝失敗,請手動安裝")
            return False
    else:
        print("✅ 所有依賴套件已安裝")
    
    return True

def setup_config():
    """設定配置檔案"""
    print("\n⚙️ 檢查設定檔...")
    
    config_file = Path("config.py")
    example_config = Path("config_example.py")
    
    if not config_file.exists():
        if example_config.exists():
            print("📋 複製範例設定檔...")
            import shutil
            shutil.copy2(example_config, config_file)
            print("✅ 設定檔已創建")
        else:
            print("❌ 找不到範例設定檔")
            return False
    else:
        print("✅ 設定檔已存在")
    
    # 驗證設定檔
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_file)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        # 檢查必要的變數是否存在
        required_vars = ['DATA_DIR', 'TEMPLATE_DIR', 'WEB_DIR', 'MAP_CONFIG']
        for var in required_vars:
            if not hasattr(config_module, var):
                raise NameError(f"name '{var}' is not defined")
        print("✅ 設定檔驗證通過")
    except Exception as e:
        print(f"❌ 設定檔驗證失敗:{e}")
        return False
    
    return True

def check_data_files():
    """檢查資料檔案"""
    print("\n📁 檢查資料檔案...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data 目錄不存在")
        return False
    
    required_files = [
        "tainan_town.shp",
        "tainan_town.shx"
    ]
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ 缺少檔案:{', '.join(missing_files)}")
        print("   系統仍可啟動,但地圖功能可能受限")
    else:
        print("✅ 所有必要檔案存在")
    
    return True

def check_chrome():
    """檢查 Chrome 瀏覽器"""
    print("\n🌐 檢查 Chrome 瀏覽器...")
    
    system = platform.system()
    chrome_paths = {
        'Windows': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        ],
        'Darwin': [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        ],
        'Linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser'
        ]
    }
    
    paths = chrome_paths.get(system, [])
    chrome_found = False
    
    for path in paths:
        if os.path.exists(path):
            chrome_found = True
            break
    
    if chrome_found:
        print("✅ Chrome 瀏覽器已安裝")
    else:
        print("⚠️ Chrome 瀏覽器未找到")
        print("   資料更新功能可能無法使用")
    
    return True

def start_system():
    """啟動系統"""
    print("\n🚀 啟動系統...")
    print("   系統將在 http://localhost:8000 啟動")
    print("   按 Ctrl+C 停止系統")
    print("-" * 60)
    
    try:
        # 啟動 FastAPI 伺服器
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 系統已停止")
    except Exception as e:
        print(f"\n❌ 啟動失敗:{e}")
        return False
    
    return True

def main():
    """主函數"""
    print_header()
    
    # 檢查步驟
    checks = [
        ("Python 版本", check_python_version),
        ("依賴套件", check_and_install_dependencies),
        ("設定檔", setup_config),
        ("資料檔案", check_data_files),
        ("Chrome 瀏覽器", check_chrome),
    ]
    
    for name, check_func in checks:
        if not check_func():
            print(f"\n❌ {name}檢查失敗,無法啟動系統")
            print("請查看上方錯誤訊息並解決問題後重新運行")
            return False
    
    print("\n✅ 所有檢查通過,準備啟動系統...")
    
    # 啟動系統
    return start_system()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 啟動已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤:{e}")
        sys.exit(1)
