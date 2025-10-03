@echo off
chcp 65001 >nul
title 登革熱疫情資料系統

echo.
echo ========================================
echo 🦟 登革熱疫情資料系統 - Windows 啟動器
echo ========================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python
    echo    請先安裝 Python 3.8 或更高版本
    echo    下載地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安裝
echo.

REM 啟動系統
echo 🚀 啟動系統...
echo    系統將在 http://localhost:8000 啟動
echo    按 Ctrl+C 停止系統
echo.

python start_system.py

echo.
echo 👋 系統已停止
pause
