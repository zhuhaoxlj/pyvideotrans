"""
Custom Model Loader with Progress Tracking
"""

import os
import urllib.request
import hashlib
from pathlib import Path
from typing import Callable, Optional
from PySide6.QtCore import QObject, Signal


class ProgressHook:
    """Hook for tracking download progress"""
    def __init__(self, progress_callback: Callable[[int, int], None]):
        self.progress_callback = progress_callback
        self.last_percentage = 0
        
    def __call__(self, block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percentage = int((downloaded / total_size) * 100)
            # Only report when percentage changes to avoid too many updates
            if percentage != self.last_percentage:
                self.progress_callback(downloaded, total_size)
                self.last_percentage = percentage


def download_model_with_progress(
    url: str, 
    output_path: Path, 
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> None:
    """
    Download a file with progress tracking
    
    Args:
        url: URL to download from
        output_path: Path to save the file
        progress_callback: Callback function(downloaded_bytes, total_bytes)
    """
    if output_path.exists():
        return
    
    # Create directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Download with progress
    if progress_callback:
        hook = ProgressHook(progress_callback)
        urllib.request.urlretrieve(url, output_path, hook)
    else:
        urllib.request.urlretrieve(url, output_path)


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def get_model_url(model_name: str) -> str:
    """Get the download URL for a Whisper model"""
    # Whisper model URLs from OpenAI
    base_url = "https://openaipublic.azureedge.net/main/whisper/models"
    
    # Model hashes and URLs
    models = {
        "tiny": "65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9",
        "base": "25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead",
        "small": "9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794",
        "medium": "345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1",
        "large": "e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a",
        "large-v2": "81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524",
        "large-v3": "e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb",
    }
    
    # For turbo models, use the v3 hash for now (they share similar structure)
    if "turbo" in model_name:
        model_name = "large-v3"
    
    if model_name not in models:
        model_name = "medium"  # fallback
    
    model_hash = models[model_name]
    return f"{base_url}/{model_hash}/{model_name}.pt"

