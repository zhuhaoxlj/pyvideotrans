@echo off
REM LLM 智能字幕分割启动脚本 (Windows)

cd /d "%~dp0"

echo ==================================
echo 🤖 启动 LLM 智能字幕分割工具
echo ==================================
echo.

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo ✅ 发现虚拟环境 .venv
    call .venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else if exist "venv\Scripts\activate.bat" (
    echo ✅ 发现虚拟环境 venv
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未找到虚拟环境，使用系统 Python
)

echo.
echo 🚀 启动程序...
echo.

REM 运行程序
python llm_split.py

echo.
echo ==================================
echo ✅ 程序已退出
echo ==================================
pause

