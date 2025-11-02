"""
Home View - Main interface for file selection and settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QFileDialog, QProgressBar,
    QMessageBox, QCheckBox
)
from PySide6.QtCore import Signal, QThread, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import os
import subprocess
import json
from pathlib import Path
from utils.model_downloader import ModelDownloader


class HomeView(QWidget):
    start_processing = Signal(dict)
    
    # Language mapping
    LANGUAGES = [
        "Arabic", "Azerbaijani", "Armenian", "Albanian", "Afrikaans", "Amharic", 
        "Assamese", "Bulgarian", "Bengali", "Breton", "Basque", "Bosnian", 
        "Belarusian", "Bashkir", "Chinese Simplified", "Chinese Traditional", 
        "Catalan", "Czech", "Croatian", "Dutch", "Danish", "English", "Estonian", 
        "French", "Finnish", "Faroese", "German", "Greek", "Galician", "Georgian", 
        "Gujarati", "Hindi", "Hebrew", "Hungarian", "Haitian creole", "Hawaiian", 
        "Hausa", "Italian", "Indonesian", "Icelandic", "Japanese", "Javanese", 
        "Korean", "Kannada", "Kazakh", "Khmer", "Lithuanian", "Latin", "Latvian", 
        "Lao", "Luxembourgish", "Lingala", "Malay", "Maori", "Malayalam", 
        "Macedonian", "Mongolian", "Marathi", "Maltese", "Myanmar", "Malagasy", 
        "Norwegian", "Nepali", "Nynorsk", "Occitan", "Portuguese", "Polish", 
        "Persian", "Punjabi", "Pashto", "Russian", "Romanian", "Spanish", "Swedish", 
        "Slovak", "Serbian", "Slovenian", "Swahili", "Sinhala", "Shona", "Somali", 
        "Sindhi", "Sanskrit", "Sundanese", "Turkish", "Tamil", "Thai", "Telugu", 
        "Tajik", "Turkmen", "Tibetan", "Tagalog", "Tatar", "Ukrainian", "Urdu", 
        "Uzbek", "Vietnamese", "Welsh", "Yoruba", "Yiddish"
    ]
    
    LANGUAGE_CODES = {
        "Arabic": "ar", "Azerbaijani": "az", "Armenian": "hy", "Albanian": "sq",
        "Afrikaans": "af", "Amharic": "am", "Assamese": "as", "Bulgarian": "bg",
        "Bengali": "bn", "Breton": "br", "Basque": "eu", "Bosnian": "bs",
        "Belarusian": "be", "Bashkir": "ba", "Chinese Simplified": "zh",
        "Chinese Traditional": "zh", "Catalan": "ca", "Czech": "cs", "Croatian": "hr",
        "Dutch": "nl", "Danish": "da", "English": "en", "Estonian": "et",
        "French": "fr", "Finnish": "fi", "Faroese": "fo", "German": "de",
        "Greek": "el", "Galician": "gl", "Georgian": "ka", "Gujarati": "gu",
        "Hindi": "hi", "Hebrew": "he", "Hungarian": "hu", "Haitian creole": "ht",
        "Hawaiian": "haw", "Hausa": "ha", "Italian": "it", "Indonesian": "id",
        "Icelandic": "is", "Japanese": "ja", "Javanese": "jw", "Korean": "ko",
        "Kannada": "kn", "Kazakh": "kk", "Khmer": "km", "Lithuanian": "lt",
        "Latin": "la", "Latvian": "lv", "Lao": "lo", "Luxembourgish": "lb",
        "Lingala": "ln", "Malay": "ms", "Maori": "mi", "Malayalam": "ml",
        "Macedonian": "mk", "Mongolian": "mn", "Marathi": "mr", "Maltese": "mt",
        "Myanmar": "my", "Malagasy": "mg", "Norwegian": "no", "Nepali": "ne",
        "Nynorsk": "nn", "Occitan": "oc", "Portuguese": "pt", "Polish": "pl",
        "Persian": "fa", "Punjabi": "pa", "Pashto": "ps", "Russian": "ru",
        "Romanian": "ro", "Spanish": "es", "Swedish": "sv", "Slovak": "sk",
        "Serbian": "sr", "Slovenian": "sl", "Swahili": "sw", "Sinhala": "si",
        "Shona": "sn", "Somali": "so", "Sindhi": "sd", "Sanskrit": "sa",
        "Sundanese": "su", "Turkish": "tr", "Tamil": "ta", "Thai": "th",
        "Telugu": "te", "Tajik": "tg", "Turkmen": "tk", "Tibetan": "bo",
        "Tagalog": "tl", "Tatar": "tt", "Ukrainian": "uk", "Urdu": "ur",
        "Uzbek": "uz", "Vietnamese": "vi", "Welsh": "cy", "Yoruba": "yo",
        "Yiddish": "yi"
    }
    
    MODELS = ["Large-v3", "Large-v3-Turbo", "Large", "Medium", "Small", "Base", "Tiny"]
    
    # Model name mapping for whisper
    MODEL_MAPPING = {
        "Large-v3": "large-v3",
        "Large-v3-Turbo": "large-v3-turbo", 
        "Large": "large",
        "Medium": "medium",
        "Small": "small",
        "Base": "base",
        "Tiny": "tiny"
    }
    
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.download_thread = None
        self.model_downloader = None
        
        # 处理状态标志
        self._processing = False
        
        self.init_ui()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 设置全局样式
        self.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
                color: #333;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2196f3;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Drag and drop hint
        drag_hint = QLabel("💡 提示: 拖放 MP4/MP3 文件到这里可自动检测帧率")
        drag_hint.setStyleSheet("color: #0066cc; font-size: 13px; padding: 12px; background-color: #e3f2fd; border-radius: 5px; border: 1px solid #90caf9;")
        drag_hint.setWordWrap(True)
        drag_hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(drag_hint)
        
        # Create grid for form
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        grid.setHorizontalSpacing(10)
        
        # Audio File Selection
        row = 0
        label = QLabel("音频/视频文件:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        grid.addWidget(label, row, 0)
        file_layout = QHBoxLayout()
        self.choose_file_btn = QPushButton("选择文件")
        self.choose_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.choose_file_btn.clicked.connect(self.choose_file)
        file_layout.addWidget(self.choose_file_btn)
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #666; padding: 8px;")
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        grid.addLayout(file_layout, row, 1)
        
        # Frame Rate
        row += 1
        label = QLabel("帧率 (FPS):")
        label.setStyleSheet("font-weight: bold; color: #333;")
        grid.addWidget(label, row, 0)
        self.fps_input = QLineEdit()
        self.fps_input.setPlaceholderText("例如: 30, 29.97")
        self.fps_input.setMaximumWidth(200)
        grid.addWidget(self.fps_input, row, 1)
        
        # Model Selection
        row += 1
        label = QLabel("Whisper 模型:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        grid.addWidget(label, row, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.MODELS)
        self.model_combo.setCurrentText("Large-v3-Turbo")
        self.model_combo.setMaximumWidth(220)
        grid.addWidget(self.model_combo, row, 1)
        
        # Cache Enable Checkbox
        row += 1
        label = QLabel("词级缓存:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        grid.addWidget(label, row, 0)
        cache_layout = QHBoxLayout()
        self.enable_cache_checkbox = QCheckBox("启用词级时间戳缓存（推荐）")
        self.enable_cache_checkbox.setChecked(True)  # 默认启用
        self.enable_cache_checkbox.setStyleSheet("""
            QCheckBox {
                color: #333;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        cache_layout.addWidget(self.enable_cache_checkbox)
        cache_layout.addStretch()
        cache_hint = QLabel("💡 启用后可在智能分割时秒级复用")
        cache_hint.setStyleSheet("color: #666; font-size: 12px;")
        cache_layout.addWidget(cache_hint)
        grid.addLayout(cache_layout, row, 1)
        
        # Language Selection
        row += 1
        label = QLabel("语言:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        grid.addWidget(label, row, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.LANGUAGES)
        self.language_combo.setCurrentText("Chinese Simplified")
        self.language_combo.setMaximumWidth(220)
        grid.addWidget(self.language_combo, row, 1)
        
        layout.addLayout(grid)
        layout.addSpacing(20)
        
        # Create Button (centered)
        create_layout = QHBoxLayout()
        create_layout.addStretch()
        self.create_btn = QPushButton("开始生成字幕")
        self.create_btn.setMinimumWidth(150)
        self.create_btn.setMinimumHeight(45)
        self.create_btn.setEnabled(False)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.create_btn.clicked.connect(self.on_create_clicked)
        create_layout.addWidget(self.create_btn)
        create_layout.addStretch()
        layout.addLayout(create_layout)
        
        # Info label with model location
        from utils.paths import get_models_dir
        models_path = get_models_dir()
        info_label = QLabel(
            f"💾 模型将下载到:\n{models_path}\n"
            "下载进度会在输出窗口显示"
        )
        info_label.setStyleSheet("""
            color: #666; 
            font-size: 12px; 
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        """)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        info_layout = QHBoxLayout()
        info_layout.addStretch()
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Connect validation
        self.fps_input.textChanged.connect(self.validate_form)
        
    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Audio/Video File",
            "",
            "Media Files (*.mp3 *.wav *.m4a *.flac *.mp4 *.mov *.avi *.mkv);;All Files (*.*)"
        )
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path):
        """Load a media file and detect frame rate if it's a video"""
        self.file_path = file_path
        file_name = os.path.basename(file_path)
        self.file_label.setText(file_name)
        
        # Check if it's a video file
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.flv', '.wmv']
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in video_extensions:
            # Auto-detect frame rate for video files
            fps = self.detect_video_fps(file_path)
            if fps:
                self.fps_input.setText(str(fps))
                self.file_label.setText(f"{file_name} (FPS: {fps})")
        
        self.validate_form()
        
    def detect_video_fps(self, video_path):
        """Detect video frame rate using ffprobe"""
        try:
            # Try to use ffprobe to get video info
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                '-select_streams', 'v:0',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if 'streams' in data and len(data['streams']) > 0:
                    stream = data['streams'][0]
                    
                    # Try to get frame rate from different fields
                    if 'r_frame_rate' in stream:
                        fps_str = stream['r_frame_rate']
                        # Parse fraction like "30000/1001" or "30/1"
                        if '/' in fps_str:
                            num, den = fps_str.split('/')
                            fps = float(num) / float(den)
                            # Round to common frame rates
                            if abs(fps - 23.976) < 0.01:
                                return "23.976"
                            elif abs(fps - 29.97) < 0.01:
                                return "29.97"
                            elif abs(fps - 59.94) < 0.01:
                                return "59.94"
                            else:
                                return str(round(fps, 2))
                    
                    if 'avg_frame_rate' in stream:
                        fps_str = stream['avg_frame_rate']
                        if '/' in fps_str and fps_str != '0/0':
                            num, den = fps_str.split('/')
                            fps = float(num) / float(den)
                            return str(round(fps, 2))
            
            return None
            
        except subprocess.TimeoutExpired:
            print("ffprobe timeout")
            return None
        except FileNotFoundError:
            QMessageBox.warning(
                self,
                "FFmpeg Not Found",
                "Could not detect frame rate automatically.\n\n"
                "Please install FFmpeg to enable auto-detection:\n"
                "  macOS: brew install ffmpeg\n"
                "  Linux: sudo apt install ffmpeg\n\n"
                "Or enter the frame rate manually."
            )
            return None
        except Exception as e:
            print(f"Error detecting FPS: {e}")
            return None
    
    def validate_form(self):
        has_file = self.file_path is not None
        has_fps = len(self.fps_input.text().strip()) > 0
        self.create_btn.setEnabled(has_file and has_fps)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs is a media file
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                ext = Path(file_path).suffix.lower()
                if ext in ['.mp3', '.wav', '.m4a', '.flac', '.mp4', '.mov', '.avi', '.mkv', '.m4v', '.flv', '.wmv']:
                    event.acceptProposedAction()
                    return
        event.ignore()
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                ext = Path(file_path).suffix.lower()
                if ext in ['.mp3', '.wav', '.m4a', '.flac', '.mp4', '.mov', '.avi', '.mkv', '.m4v', '.flv', '.wmv']:
                    self.load_file(file_path)
                    event.acceptProposedAction()
                    return
        event.ignore()
        
    def on_create_clicked(self):
        """Handle create button click"""
        print("\n" + "=" * 60)
        print("🎬 on_create_clicked() 被调用")
        print("=" * 60)
        
        # 标记为正在处理
        self._processing = True
        print("✓ 设置 _processing = True")
        
        # Whisper package will auto-download models on first use
        # No need to check or pre-download
        print("调用 start_whisper_process()...")
        try:
            self.start_whisper_process()
            print("✓ start_whisper_process() 调用成功")
        except Exception as e:
            import traceback
            print(f"❌ start_whisper_process() 失败: {str(e)}")
            print(traceback.format_exc())
            
        
    def start_whisper_process(self):
        """Start the whisper processing"""
        print("\n📋 准备处理数据...")
        
        selected_model = self.model_combo.currentText()
        model_name = self.MODEL_MAPPING.get(selected_model, selected_model.lower())
        enable_cache = self.enable_cache_checkbox.isChecked()
        
        print(f"   选择的模型: {selected_model} -> {model_name}")
        print(f"   文件路径: {self.file_path}")
        print(f"   FPS: {self.fps_input.text().strip()}")
        print(f"   启用缓存: {enable_cache}")
        
        data = {
            'file_path': self.file_path,
            'fps': float(self.fps_input.text().strip()),
            'model': model_name,
            'model_display': selected_model,
            'enable_cache': enable_cache,
            'language': self.language_combo.currentText(),
            'language_code': self.LANGUAGE_CODES[self.language_combo.currentText()],
            'project_name': Path(self.file_path).stem
        }
        
        print(f"✓ 数据准备完成")
        print(f"📡 发射 start_processing 信号...")
        
        try:
            self.start_processing.emit(data)
            print(f"✓ 信号发射成功\n")
        except Exception as e:
            import traceback
            print(f"❌ 信号发射失败: {str(e)}")
            print(traceback.format_exc())
        
    def reset(self):
        """Reset the form"""
        # 只有在非处理状态时才重置
        if not self._processing:
            self.file_path = None
            self.file_label.setText("")
            self.fps_input.clear()
            self.model_combo.setCurrentText("Large-v3")
            self.language_combo.setCurrentText("English")
            self.validate_form()

