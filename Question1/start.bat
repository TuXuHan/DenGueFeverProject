@echo off
chcp 65001 >nul
echo ======================================
echo Question1 地圖展示系統
echo ======================================
echo.

REM 檢查是否在 Question1 目錄
if not exist "main.py" (
    echo 錯誤：請在 Question1 目錄下執行此腳本
    pause
    exit /b 1
)

REM 檢查 bucket.json 是否存在
if not exist "data\bucket.json" (
    echo 警告：data\bucket.json 檔案不存在
    echo 系統將無法顯示任何位置資料
)

REM 檢查 Python 是否安裝
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 錯誤：未找到 Python，請先安裝 Python
    pause
    exit /b 1
)

echo 正在檢查依賴套件...

REM 檢查是否安裝了必要的套件
python -c "import fastapi" 2>nul
if %ERRORLEVEL% neq 0 (
    echo 正在安裝依賴套件...
    pip install -r requirements.txt
)

echo.
echo 啟動伺服器...
echo 請在瀏覽器中訪問: http://127.0.0.1:8000
echo 按 Ctrl+C 停止伺服器
echo ======================================
echo.

REM 啟動伺服器
python main.py
pause

