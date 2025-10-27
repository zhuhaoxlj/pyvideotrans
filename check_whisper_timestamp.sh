#!/bin/bash

# Whisper 时间戳检测工具启动脚本

cd "$(dirname "$0")"

echo "🔍 启动 Whisper 词级时间戳检测工具..."
echo ""

python whisper_timestamp_checker.py

