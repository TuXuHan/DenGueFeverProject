#!/bin/bash

# 登革熱疫情資料系統 - macOS/Linux 啟動器

echo ""
echo "========================================"
echo "🦟 登革熱疫情資料系統 - macOS/Linux 啟動器"
echo "========================================"
echo ""

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 錯誤：未找到 Python"
        echo "   請先安裝 Python 3.8 或更高版本"
        echo "   macOS: brew install python3"
        echo "   Ubuntu: sudo apt install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python 已安裝"
echo ""

# 設定執行權限
chmod +x start_system.py

# 啟動系統
echo "🚀 啟動系統..."
echo "   系統將在 http://localhost:8000 啟動"
echo "   按 Ctrl+C 停止系統"
echo ""

$PYTHON_CMD start_system.py

echo ""
echo "👋 系統已停止"
