@echo off
REM Whisper字幕错误检测工具 - Windows启动脚本

echo =========================================
echo 🤖 Whisper 字幕错误检测工具
echo =========================================
echo.

echo 正在检查依赖...

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python
    pause
    exit /b 1
)

echo 检查 Python 包...

REM 检查并安装依赖
python -c "import PySide6" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  缺少 PySide6，正在安装...
    pip install PySide6
)

python -c "import openai" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  缺少 openai，正在安装...
    pip install openai
)

python -c "import httpx" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  缺少 httpx，正在安装...
    pip install httpx
)

echo ✅ 依赖检查完成
echo.
echo 正在启动工具...
echo.

REM 启动工具
python whisper_error_checker.py

echo.
echo 程序已退出
pause

