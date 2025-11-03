#!/bin/bash
# Whisper字幕错误检测工具 - 启动脚本

echo "========================================="
echo "🤖 Whisper 字幕错误检测工具"
echo "========================================="
echo ""

# 检查依赖
echo "正在检查依赖..."

if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 检查必要的包
echo "检查 Python 包..."
python3 -c "import PySide6" 2>/dev/null || {
    echo "⚠️  缺少 PySide6，正在安装..."
    pip install PySide6 || exit 1
}

python3 -c "import openai" 2>/dev/null || {
    echo "⚠️  缺少 openai，正在安装..."
    pip install openai || exit 1
}

python3 -c "import httpx" 2>/dev/null || {
    echo "⚠️  缺少 httpx，正在安装..."
    pip install httpx || exit 1
}

echo "✅ 依赖检查完成"
echo ""
echo "正在启动工具..."
echo ""

# 启动工具
python3 whisper_error_checker.py

echo ""
echo "程序已退出"

