#!/usr/bin/env python3
"""
登革熱疫情資料系統 - 一鍵安裝腳本
自動安裝所有必要的依賴套件和設定
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """顯示安裝橫幅"""
    print("=" * 60)
    print("🦟 登革熱疫情資料系統 - 一鍵安裝")
    print("=" * 60)
    print()

def check_python():
    """檢查 Python 版本"""
    print("🔍 檢查 Python 環境...")
    version = sys.version_info
    print(f"   Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要 Python 3.8 或更高版本")
        print("   請升級 Python 後重新運行此腳本")
        return False
    
    print("✅ Python 版本符合要求")
    return True

def install_requirements():
    """安裝 requirements.txt 中的套件"""
    print("\n📦 安裝 Python 套件...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ 找不到 requirements.txt 檔案")
        return False
    
    try:
        print("   正在安裝套件,這可能需要幾分鐘...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ 套件安裝完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 套件安裝失敗: {e}")
        print("   請手動執行: pip install -r requirements.txt")
        return False

def setup_config():
    """設定配置檔案"""
    print("\n⚙️ 設定配置檔案...")
    
    config_file = Path("config.py")
    example_config = Path("config_example.py")
    
    if not config_file.exists():
        if example_config.exists():
            import shutil
            shutil.copy2(example_config, config_file)
            print("✅ 配置檔案已創建 (config.py)")
        else:
            print("❌ 找不到範例配置檔案")
            return False
    else:
        print("✅ 配置檔案已存在")
    
    return True

def create_directories():
    """創建必要的目錄"""
    print("\n📁 創建必要目錄...")
    
    directories = [
        "logs",
        "data",
        "template",
        "web"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✅ 創建目錄: {dir_name}")
        else:
            print(f"✅ 目錄已存在: {dir_name}")
    
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
        print("   請安裝 Chrome 瀏覽器以使用資料更新功能")
        print("   下載地址: https://www.google.com/chrome/")
    
    return True

def show_next_steps():
    """顯示後續步驟"""
    print("\n" + "=" * 60)
    print("🎉 安裝完成!")
    print("=" * 60)
    print()
    print("📋 後續步驟:")
    print()
    print("1. 啟動系統:")
    print("   Windows: 雙擊 start.bat")
    print("   macOS/Linux: 執行 ./start.sh")
    print("   或手動執行: python start_system.py")
    print()
    print("2. 開啟瀏覽器:")
    print("   訪問 http://localhost:8000")
    print()
    print("3. 自訂設定:")
    print("   編輯 config.py 檔案")
    print()
    print("📚 更多資訊:")
    print("   查看 INSTALLATION_GUIDE.md 獲取詳細說明")
    print("   查看 QUICK_START.md 獲取快速開始指南")
    print()
    print("🆘 需要幫助?")
    print("   查看 CONFIG_README.md 獲取設定說明")
    print()

def main():
    """主安裝流程"""
    print_banner()
    
    # 安裝步驟
    steps = [
        ("Python 環境", check_python),
        ("Python 套件", install_requirements),
        ("配置檔案", setup_config),
        ("目錄結構", create_directories),
        ("Chrome 瀏覽器", check_chrome),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ {step_name}設定失敗")
            print("安裝未完成,請解決問題後重新運行")
            return False
    
    show_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 安裝已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 安裝過程中發生錯誤: {e}")
        sys.exit(1)
