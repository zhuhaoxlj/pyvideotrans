#!/bin/bash

# 字幕处理和渲染一键脚本
# 使用方法：./process_and_render.sh <视频文件> <字幕文件>

set -e

echo "=================================================="
echo "🎬 字幕处理和渲染工具"
echo "=================================================="

if [ "$#" -lt 2 ]; then
    echo ""
    echo "用法: $0 <视频文件> <字幕文件> [最大持续时间(秒)]"
    echo ""
    echo "示例:"
    echo "  $0 video.mp4 subtitle.srt"
    echo "  $0 video.mp4 subtitle.srt 3"
    echo ""
    echo "或者只使用 Whisper 重新生成字幕:"
    echo "  $0 video.mp4 auto [语言代码] [模型大小]"
    echo ""
    echo "示例:"
    echo "  $0 video.mp4 auto en base"
    echo "  $0 video.mp4 auto zh small"
    echo ""
    exit 1
fi

VIDEO_FILE="$1"
SUBTITLE_FILE="$2"
MAX_DURATION="${3:-3}"  # 默认3秒

# 检查视频文件是否存在
if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ 错误: 视频文件不存在: $VIDEO_FILE"
    exit 1
fi

echo ""
echo "📹 视频文件: $VIDEO_FILE"

# 如果字幕参数是 "auto"，使用 Whisper 生成
if [ "$SUBTITLE_FILE" = "auto" ]; then
    LANGUAGE="${3:-en}"
    MODEL="${4:-base}"
    
    echo "🤖 使用 Whisper AI 生成字幕..."
    echo "   语言: $LANGUAGE"
    echo "   模型: $MODEL"
    echo ""
    
    python regenerate_subtitles.py "$VIDEO_FILE" "$LANGUAGE" "$MODEL"
    
    # 查找生成的字幕文件
    BASENAME="${VIDEO_FILE%.*}"
    GENERATED_SRT="${BASENAME}_whisper.srt"
    
    if [ ! -f "$GENERATED_SRT" ]; then
        echo "❌ 错误: Whisper 字幕生成失败"
        exit 1
    fi
    
    SUBTITLE_FILE="$GENERATED_SRT"
    echo ""
    echo "✅ 字幕生成完成: $SUBTITLE_FILE"
else
    # 检查字幕文件是否存在
    if [ ! -f "$SUBTITLE_FILE" ]; then
        echo "❌ 错误: 字幕文件不存在: $SUBTITLE_FILE"
        exit 1
    fi
    
    echo "📝 原始字幕: $SUBTITLE_FILE"
    echo "⏱️  最大持续时间: ${MAX_DURATION}秒"
    echo ""
    
    # 分割字幕
    echo "🔧 正在分割字幕..."
    python split_subtitles.py "$SUBTITLE_FILE" "$MAX_DURATION"
    
    # 查找分割后的字幕文件
    BASENAME="${SUBTITLE_FILE%.*}"
    EXTENSION="${SUBTITLE_FILE##*.}"
    SPLIT_SRT="${BASENAME}_split.${EXTENSION}"
    
    if [ ! -f "$SPLIT_SRT" ]; then
        echo "❌ 错误: 字幕分割失败"
        exit 1
    fi
    
    SUBTITLE_FILE="$SPLIT_SRT"
    echo ""
    echo "✅ 字幕分割完成: $SUBTITLE_FILE"
fi

echo ""
echo "=================================================="
echo "✅ 准备完成！"
echo "=================================================="
echo ""
echo "📁 处理后的字幕文件:"
echo "   $SUBTITLE_FILE"
echo ""
echo "💡 下一步操作:"
echo "   1. 运行: python sp_vas.py"
echo "   2. 选择视频: $VIDEO_FILE"
echo "   3. 选择字幕: $SUBTITLE_FILE"
echo "   4. 点击'开始执行'"
echo ""
echo "🚀 自动启动字幕合并工具..."
echo ""

# 可选：自动启动 sp_vas.py
python sp_vas.py

