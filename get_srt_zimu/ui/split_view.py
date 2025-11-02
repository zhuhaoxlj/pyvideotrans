"""
Split View - AI智能分割字幕功能
使用 LLM 对字幕进行智能断句优化
支持：从视频生成字幕、重新分割现有字幕、缓存机制等

完整迁移自 videotrans.winform.fn_llm_split
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QComboBox, QLineEdit,
    QGridLayout, QGroupBox, QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QTextCursor
from pathlib import Path
import os


class SplitView(QWidget):
    back_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.video_file_path = None
        self.srt_file_path = None
        self.output_file = None
        self.processor = None
        
        # 处理状态标志
        self._processing = False
        
        self.init_ui()
    
    def init_ui(self):
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: white; }")
        
        # 主容器
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 设置全局样式
        self.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
                color: #333;
                min-height: 35px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #4caf50;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
                font-size: 13px;
                color: #333;
                font-family: 'Monaco', 'Courier New', monospace;
            }
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QCheckBox {
                font-size: 14px;
                color: #333;
            }
            QGroupBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                color: #333;
                font-size: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: #f5f5f5;
                border-radius: 4px;
                color: #4caf50;
            }
        """)
        
        # 标题
        title = QLabel("✂️ AI智能字幕生成与分割")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4caf50; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("从视频生成字幕或重新分割现有字幕，使用 LLM 进行智能断句优化")
        desc.setStyleSheet("font-size: 15px; color: #666; padding: 10px; margin-bottom: 15px;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # ===== 视频文件选择区域 =====
        video_group = QGroupBox("🎥 视频/音频文件")
        video_layout = QVBoxLayout()
        
        video_select_layout = QHBoxLayout()
        video_select_layout.setSpacing(10)
        
        choose_video_btn = QPushButton("📂 选择视频/音频")
        choose_video_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        choose_video_btn.clicked.connect(self.choose_video_file)
        video_select_layout.addWidget(choose_video_btn)
        
        self.video_label = QLabel("未选择文件（可选，用于生成新字幕或获取词级时间戳）")
        self.video_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #666; border: 2px solid #e0e0e0;")
        video_select_layout.addWidget(self.video_label, 1)
        
        video_layout.addLayout(video_select_layout)
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # ===== 字幕文件选择区域 =====
        srt_group = QGroupBox("📁 字幕文件（可选）")
        srt_layout = QVBoxLayout()
        
        # 复选框：使用现有字幕
        self.use_existing_srt = QCheckBox("使用现有字幕进行重新分割")
        self.use_existing_srt.setStyleSheet("font-weight: bold;")
        self.use_existing_srt.stateChanged.connect(self.toggle_srt_input)
        srt_layout.addWidget(self.use_existing_srt)
        
        srt_select_layout = QHBoxLayout()
        srt_select_layout.setSpacing(10)
        
        self.choose_srt_btn = QPushButton("📂 选择 SRT 文件")
        self.choose_srt_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.choose_srt_btn.clicked.connect(self.choose_srt_file)
        self.choose_srt_btn.setVisible(False)
        srt_select_layout.addWidget(self.choose_srt_btn)
        
        self.srt_label = QLabel("未选择字幕文件")
        self.srt_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #666; border: 2px solid #e0e0e0;")
        self.srt_label.setVisible(False)
        srt_select_layout.addWidget(self.srt_label, 1)
        
        srt_layout.addLayout(srt_select_layout)
        srt_group.setLayout(srt_layout)
        layout.addWidget(srt_group)
        
        # ===== Whisper 设置区域 =====
        whisper_group = QGroupBox("🎤 Whisper 设置")
        whisper_layout = QGridLayout()
        whisper_layout.setSpacing(15)
        whisper_layout.setColumnStretch(1, 1)
        
        row = 0
        # 语言
        label = QLabel("识别语言:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        whisper_layout.addWidget(label, row, 0)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "en=English",
            "zh=Chinese",
            "ja=Japanese",
            "ko=Korean",
            "es=Spanish",
            "fr=French",
            "de=German",
            "ru=Russian",
            "auto=Auto Detect"
        ])
        whisper_layout.addWidget(self.language_combo, row, 1)
        
        row += 1
        # 模型大小
        label = QLabel("模型大小:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        whisper_layout.addWidget(label, row, 0)
        
        self.model_size_combo = QComboBox()
        self.model_size_combo.addItems([
            "large-v3-turbo",
            "large-v3",
            "large-v2",
            "medium",
            "small",
            "base",
            "tiny"
        ])
        whisper_layout.addWidget(self.model_size_combo, row, 1)
        
        row += 1
        # 设备
        label = QLabel("计算设备:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        whisper_layout.addWidget(label, row, 0)
        
        self.device_combo = QComboBox()
        import platform
        if platform.system() == "Darwin":  # macOS
            self.device_combo.addItems(["CPU", "MPS"])
        elif platform.system() == "Windows":
            self.device_combo.addItems(["CPU", "CUDA"])
        else:
            self.device_combo.addItems(["CPU", "CUDA"])
        whisper_layout.addWidget(self.device_combo, row, 1)
        
        row += 1
        # 缓存选项
        label = QLabel("词级缓存:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        whisper_layout.addWidget(label, row, 0)
        
        cache_widget = QWidget()
        cache_layout = QHBoxLayout()
        cache_layout.setContentsMargins(0, 0, 0, 0)
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
        cache_hint = QLabel("💡 秒级加载已处理过的视频")
        cache_hint.setStyleSheet("color: #666; font-size: 12px;")
        cache_layout.addWidget(cache_hint)
        cache_widget.setLayout(cache_layout)
        whisper_layout.addWidget(cache_widget, row, 1)
        
        whisper_group.setLayout(whisper_layout)
        layout.addWidget(whisper_group)
        
        # ===== LLM 配置区域 =====
        llm_group = QGroupBox("🤖 LLM 配置")
        llm_layout = QGridLayout()
        llm_layout.setSpacing(15)
        llm_layout.setColumnStretch(1, 1)
        
        row = 0
        # LLM 提供商
        label = QLabel("提供商:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        llm_layout.addWidget(label, row, 0)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "SiliconFlow",
            "OpenAI",
            "Claude",
            "DeepSeek"
        ])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        llm_layout.addWidget(self.provider_combo, row, 1)
        
        row += 1
        # API Key
        label = QLabel("API Key:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        llm_layout.addWidget(label, row, 0)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入 API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.textChanged.connect(self.save_api_key)
        self.api_key_input.textChanged.connect(self.update_process_button)
        llm_layout.addWidget(self.api_key_input, row, 1)
        
        row += 1
        # 模型
        label = QLabel("模型:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        llm_layout.addWidget(label, row, 0)
        
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        llm_layout.addWidget(self.model_combo, row, 1)
        
        row += 1
        # Base URL (可选)
        label = QLabel("Base URL:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        self.base_url_label = label
        llm_layout.addWidget(label, row, 0)
        
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("可选，留空使用默认")
        llm_layout.addWidget(self.base_url_input, row, 1)
        
        llm_group.setLayout(llm_layout)
        layout.addWidget(llm_group)
        
        # ===== 日志输出区域 =====
        log_group = QGroupBox("📄 处理日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("处理日志将显示在这里...")
        self.log_text.setMinimumHeight(250)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # ===== 按钮区域 =====
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.process_btn = QPushButton("✨ 开始处理")
        self.process_btn.setEnabled(False)
        self.process_btn.setMinimumWidth(160)
        self.process_btn.setMinimumHeight(50)
        self.process_btn.clicked.connect(self.start_process)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        btn_layout.addWidget(self.process_btn)
        
        self.open_btn = QPushButton("📂 打开输出文件夹")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_output_folder)
        self.open_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        btn_layout.addWidget(self.open_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        # 设置滚动区域
        scroll.setWidget(container)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # 初始化提供商配置
        self.on_provider_changed(self.provider_combo.currentText())
        
        # 从环境变量或配置加载 API Key
        self.load_api_key()
    
    def toggle_srt_input(self):
        """切换字幕文件输入的显示"""
        is_checked = self.use_existing_srt.isChecked()
        self.choose_srt_btn.setVisible(is_checked)
        self.srt_label.setVisible(is_checked)
        if not is_checked:
            self.srt_file_path = None
            self.srt_label.setText("未选择字幕文件")
        self.update_process_button()
    
    def on_provider_changed(self, provider):
        """提供商改变时更新模型列表"""
        self.model_combo.clear()
        
        if provider == "SiliconFlow":
            self.model_combo.addItems([
                "Qwen/Qwen2.5-7B-Instruct",
                "deepseek-ai/DeepSeek-V3.1-Terminus",
                "Pro/Qwen/Qwen2.5-72B-Instruct",
                "meta-llama/Meta-Llama-3.1-70B-Instruct"
            ])
            self.base_url_input.setPlaceholderText("https://api.siliconflow.cn/v1/chat/completions")
        elif provider == "OpenAI":
            self.model_combo.addItems([
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ])
            self.base_url_input.setPlaceholderText("https://api.openai.com/v1/chat/completions")
        elif provider == "Claude":
            self.model_combo.addItems([
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229"
            ])
            self.base_url_input.setPlaceholderText("https://api.anthropic.com/v1/messages")
        elif provider == "DeepSeek":
            self.model_combo.addItems([
                "deepseek-chat",
                "deepseek-coder"
            ])
            self.base_url_input.setPlaceholderText("https://api.deepseek.com/v1/chat/completions")
        
        # 加载对应提供商的 API Key
        self.load_api_key()
    
    def load_api_key(self):
        """从环境变量或 .env 文件加载 API Key"""
        provider = self.provider_combo.currentText().upper()
        env_key = f"{provider}_API_KEY"
        
        # 从环境变量读取
        api_key = os.environ.get(env_key, '')
        
        # 如果没有，从 .env 文件读取
        if not api_key:
            env_file = Path.home() / 'Videos' / 'pyvideotrans' / 'get_srt_zimu' / '.env'
            if env_file.exists():
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    if key.strip() == env_key:
                                        api_key = value.strip().strip('"').strip("'")
                                        break
                except Exception:
                    pass
        
        if api_key:
            self.api_key_input.setText(api_key)
    
    def save_api_key(self):
        """保存 API Key 到 .env 文件"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            return
        
        provider = self.provider_combo.currentText().upper()
        env_key = f"{provider}_API_KEY"
        
        # 确保目录存在
        env_dir = Path.home() / 'Videos' / 'pyvideotrans' / 'get_srt_zimu'
        env_dir.mkdir(parents=True, exist_ok=True)
        
        env_file = env_dir / '.env'
        
        # 读取现有内容
        lines = []
        key_exists = False
        
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 查找并更新
                for i, line in enumerate(lines):
                    if line.strip().startswith(f'{env_key}='):
                        lines[i] = f'{env_key}={api_key}\n'
                        key_exists = True
                        break
            except Exception:
                pass
        
        # 如果不存在，添加
        if not key_exists:
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            lines.append(f'{env_key}={api_key}\n')
        
        # 写回文件
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception:
            pass
    
    def choose_video_file(self):
        """选择视频/音频文件"""
        formats = ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'mp3', 'wav', 'flac', 'm4a']
        format_str = ' '.join([f'*.{f}' for f in formats])
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频或音频文件",
            "",
            f"Video/Audio files({format_str})"
        )
        
        if file_path:
            self.video_file_path = file_path
            file_name = Path(file_path).name
            self.video_label.setText(f"✓ {file_name}")
            self.video_label.setStyleSheet("padding: 12px; background: #e3f2fd; border-radius: 5px; color: #1976d2; border: 2px solid #2196f3; font-weight: bold;")
            self.update_process_button()
    
    def choose_srt_file(self):
        """选择字幕文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 SRT 字幕文件",
            "",
            "字幕文件 (*.srt);;所有文件 (*.*)"
        )
        
        if file_path:
            self.load_srt_file(file_path)
    
    def load_video_file(self, file_path):
        """加载视频文件（用于外部调用）"""
        if file_path and Path(file_path).exists():
            self.video_file_path = file_path
            file_name = Path(file_path).name
            self.video_label.setText(f"✓ {file_name}")
            self.video_label.setStyleSheet("padding: 12px; background: #e3f2fd; border-radius: 5px; color: #1976d2; border: 2px solid #2196f3; font-weight: bold;")
            self.update_process_button()
    
    def load_srt_file(self, file_path):
        """加载 SRT 文件（用于外部调用）"""
        if file_path and Path(file_path).exists():
            self.srt_file_path = file_path
            file_name = Path(file_path).name
            self.srt_label.setText(f"✓ {file_name}")
            self.srt_label.setStyleSheet("padding: 12px; background: #e3f2fd; border-radius: 5px; color: #1976d2; border: 2px solid #2196f3; font-weight: bold;")
            
            # 检查是否可以开始处理
            self.update_process_button()
            
            # 显示提示
            if self.video_file_path:
                self.log_text.setText(
                    f"✅ 已加载视频文件: {Path(self.video_file_path).name}\n"
                    f"✅ 已加载字幕文件: {file_name}\n\n"
                    f"🚀 模式：使用视频+现有字幕（Whisper词级+LLM）\n"
                    f"💡 由于视频已处理过，将直接使用缓存的词级时间戳\n\n"
                    f"📌 请配置 LLM 设置后点击「开始处理」"
                )
            else:
                self.log_text.setText(f"✅ 已加载字幕文件: {file_name}\n\n📌 请配置 LLM 设置后点击「开始处理」")
    
    def update_process_button(self):
        """更新处理按钮状态"""
        has_video = self.video_file_path is not None
        has_srt = self.srt_file_path is not None
        has_api_key = len(self.api_key_input.text().strip()) > 0
        
        # 至少需要视频或字幕文件之一，且需要 API Key
        can_process = (has_video or has_srt) and has_api_key
        
        self.process_btn.setEnabled(can_process)
    
    def start_process(self):
        """开始处理"""
        # 验证输入
        if not self.video_file_path and not self.srt_file_path:
            QMessageBox.warning(self, "警告", "请至少选择视频文件或字幕文件")
            return
        
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入 API Key")
            return
        
        # 标记为正在处理
        self._processing = True
        
        # 禁用按钮
        self.process_btn.setEnabled(False)
        self.process_btn.setText("⏳ 处理中...")
        
        # 清空日志
        self.log_text.clear()
        self.log_text.append("🚀 开始处理...\n")
        
        # 创建处理器
        from utils.llm_processor import LLMProcessor
        
        provider = self.provider_combo.currentText().lower()
        model = self.model_combo.currentText()
        base_url = self.base_url_input.text().strip()
        
        # Whisper 设置
        language = self.language_combo.currentText().split('=')[0]
        model_size = self.model_size_combo.currentText()
        device = self.device_combo.currentText().lower()
        enable_cache = self.enable_cache_checkbox.isChecked()
        
        self.processor = LLMProcessor(
            video_file=self.video_file_path,
            srt_file=self.srt_file_path if self.use_existing_srt.isChecked() else None,
            llm_provider=provider,
            llm_api_key=api_key,
            llm_model=model,
            llm_base_url=base_url,
            language=language,
            model_size=model_size,
            device=device,
            enable_cache=enable_cache
        )
        
        # 连接信号
        self.processor.progress.connect(self.on_progress)
        self.processor.stream.connect(self.on_stream)
        self.processor.finished_signal.connect(self.on_finished)
        self.processor.error.connect(self.on_error)
        
        # 启动处理
        self.processor.start()
    
    def on_progress(self, message):
        """处理进度更新"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_stream(self, content):
        """处理流式输出"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(content)
        self.log_text.setTextCursor(cursor)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_finished(self, output_file):
        """处理完成"""
        self.output_file = output_file
        
        # 重置处理标志
        self._processing = False
        
        self.process_btn.setEnabled(True)
        self.process_btn.setText("✨ 开始处理")
        self.open_btn.setEnabled(True)
        
        self.log_text.append("\n\n" + "="*50)
        self.log_text.append("✅ 处理完成！")
        self.log_text.append("="*50)
        
        QMessageBox.information(
            self,
            "完成",
            f"字幕处理完成！\n\n输出文件:\n{output_file}"
        )
    
    def on_error(self, error_msg):
        """处理错误"""
        # 重置处理标志
        self._processing = False
        
        self.process_btn.setEnabled(True)
        self.process_btn.setText("✨ 开始处理")
        
        self.log_text.append("\n\n" + "="*50)
        self.log_text.append(f"❌ 错误:\n{error_msg}")
        self.log_text.append("="*50)
        
        QMessageBox.critical(
            self,
            "错误",
            f"处理失败:\n\n{error_msg[:500]}"
        )
    
    def open_output_folder(self):
        """打开输出文件夹"""
        if self.output_file and Path(self.output_file).exists():
            folder = Path(self.output_file).parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
    
    def reset(self):
        """重置界面"""
        # 只有在非处理状态时才重置
        if not self._processing:
            self.video_file_path = None
            self.srt_file_path = None
            self.output_file = None
            self.video_label.setText("未选择文件（可选，用于生成新字幕或获取词级时间戳）")
            self.video_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #666; border: 2px solid #e0e0e0;")
            self.srt_label.setText("未选择字幕文件")
            self.srt_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #666; border: 2px solid #e0e0e0;")
            self.log_text.clear()
            self.process_btn.setEnabled(False)
            self.process_btn.setText("✨ 开始处理")
            self.open_btn.setEnabled(False)
            self.use_existing_srt.setChecked(False)

