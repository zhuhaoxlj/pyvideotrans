"""
Path management utilities
"""

from pathlib import Path
import platform
import os


def get_project_root():
    """Get the project root directory"""
    # Get the directory where this file is located
    current_file = Path(__file__).resolve()
    # Go up two levels: utils -> project root
    project_root = current_file.parent.parent
    return project_root


def get_app_data_dir():
    """Get the application data directory"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    elif system == "Windows":
        base = Path.home() / "AppData" / "Local"
    else:  # Linux
        base = Path.home() / ".local" / "share"
    
    app_dir = base / "Whisper Auto Captions"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_models_dir():
    """Get the models directory in project folder"""
    # Store models in project folder
    project_root = get_project_root()
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def get_temp_dir():
    """Get the temporary directory for processing"""
    temp_dir = get_app_data_dir() / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def setup_whisper_cache():
    """Setup environment variable to use project models directory"""
    models_dir = get_models_dir()
    os.environ['XDG_CACHE_HOME'] = str(models_dir.parent)
    return models_dir

