@echo off
chcp 65001 >nul
echo 🚀 啟動台南市行政區相似度分析 - 本地端伺服器
echo ================================================
echo.
echo 📁 伺服器目錄: %CD%
echo 🌐 伺服器地址: http://localhost:8000
echo 📄 主要頁面: http://localhost:8000/enhanced_interactive_map.html
echo.
echo 💡 使用說明:
echo 1. 在瀏覽器中打開: http://localhost:8000/enhanced_interactive_map.html
echo 2. 點擊地圖上的行政區查看相似度分析
echo 3. 使用左側搜索功能查找特定區域
echo.
echo ⚠️  注意: 請保持此視窗開啟，關閉會停止伺服器
echo 🛑 停止伺服器: 按 Ctrl+C
echo.
echo 正在啟動伺服器...

python -m http.server 8000
