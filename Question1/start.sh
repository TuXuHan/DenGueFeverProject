#!/bin/bash

echo "======================================"
echo "Question1 地圖展示系統"
echo "======================================"
echo ""

# 檢查是否在 Question1 目錄
if [ ! -f "main.py" ]; then
    echo "錯誤：請在 Question1 目錄下執行此腳本"
    exit 1
fi

# 檢查 bucket.json 是否存在
if [ ! -f "data/bucket.json" ]; then
    echo "警告：data/bucket.json 檔案不存在"
    echo "系統將無法顯示任何位置資料"
fi

# 檢查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "錯誤：未找到 Python3，請先安裝 Python3"
    exit 1
fi

echo "正在檢查依賴套件..."

# 檢查是否安裝了必要的套件
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "正在安裝依賴套件..."
    pip3 install -r requirements.txt
fi

echo ""
echo "啟動伺服器..."
echo "請在瀏覽器中訪問: http://127.0.0.1:8000"
echo "按 Ctrl+C 停止伺服器"
echo "======================================"
echo ""

# 啟動伺服器
python3 main.py

