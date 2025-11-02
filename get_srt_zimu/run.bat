@echo off
REM Whisper Auto Captions - Windows Launcher Script (using uv)

echo.
echo ========================================
echo   Whisper Auto Captions - Python Edition
echo ========================================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo Installing uv package manager...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    REM Refresh PATH
    call refreshenv
    
    uv --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Failed to install uv
        echo Please install manually from https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
    echo uv installed successfully
)

echo Found uv
uv --version

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Warning: FFmpeg is not installed
    echo Please install FFmpeg for audio processing:
    echo   Download from https://ffmpeg.org/
    echo.
)

REM Sync dependencies (create venv if needed, install packages)
echo.
echo Syncing dependencies...
uv sync

echo.
echo Starting Whisper Auto Captions...
echo.

REM Run the application with uv
uv run python main.py

pause
