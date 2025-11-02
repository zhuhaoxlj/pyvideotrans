#!/bin/bash
# LLM 智能字幕分割启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================="
echo "🤖 启动 LLM 智能字幕分割工具"
echo "=================================="
echo ""

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "✅ 发现虚拟环境 .venv"
    source .venv/bin/activate
    echo "✅ 虚拟环境已激活"
elif [ -d "venv" ]; then
    echo "✅ 发现虚拟环境 venv"
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境，使用系统 Python"
fi

echo ""
echo "🚀 启动程序..."
echo ""

# 运行程序
python llm_split.py

echo ""
echo "=================================="
echo "✅ 程序已退出"
echo "=================================="

