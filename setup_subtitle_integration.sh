#!/bin/bash
# 字幕生成功能集成设置脚本

echo "🎬 PyVideoTrans 字幕生成功能集成设置"
echo "========================================"
echo ""

# 获取当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "项目目录: $SCRIPT_DIR"
echo ""

# 检查 get_srt_zimu 是否存在
if [ -d "$SCRIPT_DIR/get_srt_zimu" ]; then
    echo "✅ 找到 get_srt_zimu 目录"
    echo "   位置: $SCRIPT_DIR/get_srt_zimu"
else
    echo "❌ 未找到 get_srt_zimu 目录"
    echo ""
    echo "请执行以下操作之一："
    echo ""
    echo "选项 1 - 如果 get_srt_zimu 在其他位置，创建软链接："
    echo "   ln -s /path/to/get_srt_zimu $SCRIPT_DIR/get_srt_zimu"
    echo ""
    echo "选项 2 - 将 get_srt_zimu 移动到项目目录："
    echo "   mv /path/to/get_srt_zimu $SCRIPT_DIR/"
    echo ""
    echo "选项 3 - 克隆 get_srt_zimu 项目（如果是 git 仓库）："
    echo "   cd $SCRIPT_DIR"
    echo "   git clone <repo_url> get_srt_zimu"
    echo ""
    exit 1
fi

echo ""
echo "检查必要文件..."

# 检查必要的文件
required_files=(
    "get_srt_zimu/main.py"
    "get_srt_zimu/ui/main_window.py"
    "get_srt_zimu/ui/home_view.py"
    "get_srt_zimu/utils/whisper_processor.py"
)

all_found=true
for file in "${required_files[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
        all_found=false
    fi
done

echo ""

if [ "$all_found" = true ]; then
    echo "✅ 所有必要文件都存在！"
    echo ""
    echo "现在可以运行主程序："
    echo "   cd $SCRIPT_DIR"
    echo "   uv run python main.py"
    echo ""
    echo "或使用 Python 直接运行："
    echo "   python main.py"
else
    echo "❌ 缺少必要文件，请检查 get_srt_zimu 项目是否完整"
    exit 1
fi

echo ""
echo "设置完成！✨"

