#!/bin/bash
# 更新 GeoJSON 測試頁面
# 自動掃描並生成包含所有 .geojson 檔案的測試頁面

# 切換到腳本所在目錄
cd "$(dirname "$0")"

echo "🔄 正在生成測試頁面..."
python3 generate_test_page.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 完成！現在可以用瀏覽器開啟 test_geojson.html"
else
    echo "❌ 生成失敗"
    exit 1
fi

