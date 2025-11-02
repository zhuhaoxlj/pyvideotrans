"""
Model Downloader - Downloads Whisper models from Hugging Face
"""

from PySide6.QtCore import QObject, Signal
import urllib.request
import urllib.error
from pathlib import Path
from utils.paths import get_models_dir


class ModelDownloader(QObject):
    progress = Signal(float)
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        # Use the datasets path, same as original Swift app
        self.base_url = "https://huggingface.co/datasets/ggerganov/whisper.cpp/resolve/main"
        
    def download(self):
        """Download the model file"""
        try:
            model_filename = f"ggml-{self.model_name}.bin"
            url = f"{self.base_url}/{model_filename}"
            output_path = get_models_dir() / model_filename
            
            # Check if already exists
            if output_path.exists():
                self.progress.emit(1.0)
                self.finished.emit()
                return
            
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    progress_value = min(downloaded / total_size, 1.0)
                    self.progress.emit(progress_value)
            
            # Add headers to avoid potential issues
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            
            urllib.request.urlretrieve(url, output_path, report_progress)
            self.finished.emit()
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.error.emit(f"Model not found. Please check if '{self.model_name}' is a valid model name.\n\nValid models: tiny, base, small, medium, large")
            else:
                self.error.emit(f"HTTP Error {e.code}: {str(e)}")
        except urllib.error.URLError as e:
            self.error.emit(f"Network error: {str(e)}\n\nPlease check your internet connection.")
        except Exception as e:
            self.error.emit(f"Unexpected error: {str(e)}")

