# LLM字幕翻译 UI

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import (QMetaObject, QSize, Qt)
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPlainTextEdit, QPushButton, QComboBox, QCheckBox,
                               QVBoxLayout, QGridLayout, QSplitter, QFrame, QSpinBox)

from videotrans.configure import config


class Ui_llmtrans(object):
    def setupUi(self, llmtrans):
        self.has_done = False
        if not llmtrans.objectName():
            llmtrans.setObjectName(u"llmtrans")
        
        # 获取屏幕可用高度和宽度
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_height = screen_geometry.height()
            screen_width = screen_geometry.width()
            # 设置窗口为全屏大小（留一点边距）
            window_height = int(screen_height * 0.9)
            window_width = int(screen_width * 0.9)
            llmtrans.resize(window_width, window_height)
        else:
            # 如果无法获取屏幕信息，使用默认值
            llmtrans.resize(1400, 800)
        
        llmtrans.setWindowModality(QtCore.Qt.NonModal)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(llmtrans.sizePolicy().hasHeightForWidth())
        llmtrans.setSizePolicy(sizePolicy)
        
        # 设置最小尺寸
        llmtrans.setMinimumSize(QSize(1000, 600))

        # 主布局
        self.main_layout = QVBoxLayout(llmtrans)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # 标题区域
        self.title_label = QLabel(llmtrans)
        self.title_label.setObjectName(u"title_label")
        from PySide6.QtGui import QFont
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("QLabel { color: #2196f3; padding: 10px; }")
        self.main_layout.addWidget(self.title_label)
        
        # 配置区域
        self.config_frame = QFrame(llmtrans)
        self.config_frame.setObjectName(u"config_frame")
        self.config_frame.setFrameShape(QFrame.StyledPanel)
        self.config_frame.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 5px; padding: 10px; }")
        
        self.config_layout = QGridLayout(self.config_frame)
        self.config_layout.setObjectName(u"config_layout")
        self.config_layout.setSpacing(10)
        
        # LLM提供商
        row = 0
        self.provider_label = QLabel(self.config_frame)
        self.provider_label.setObjectName(u"provider_label")
        self.config_layout.addWidget(self.provider_label, row, 0)
        
        self.provider_combo = QComboBox(self.config_frame)
        self.provider_combo.setObjectName(u"provider_combo")
        self.provider_combo.setMinimumHeight(35)
        self.config_layout.addWidget(self.provider_combo, row, 1)
        
        # API Key
        self.api_key_label = QLabel(self.config_frame)
        self.api_key_label.setObjectName(u"api_key_label")
        self.config_layout.addWidget(self.api_key_label, row, 2)
        
        self.api_key_input = QLineEdit(self.config_frame)
        self.api_key_input.setObjectName(u"api_key_input")
        self.api_key_input.setMinimumHeight(35)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.config_layout.addWidget(self.api_key_input, row, 3)
        
        # 模型选择
        row += 1
        self.model_label = QLabel(self.config_frame)
        self.model_label.setObjectName(u"model_label")
        self.config_layout.addWidget(self.model_label, row, 0)
        
        self.model_combo = QComboBox(self.config_frame)
        self.model_combo.setObjectName(u"model_combo")
        self.model_combo.setMinimumHeight(35)
        self.model_combo.setEditable(True)
        self.config_layout.addWidget(self.model_combo, row, 1)
        
        # API Base URL
        self.base_url_label = QLabel(self.config_frame)
        self.base_url_label.setObjectName(u"base_url_label")
        self.config_layout.addWidget(self.base_url_label, row, 2)
        
        self.base_url_input = QLineEdit(self.config_frame)
        self.base_url_input.setObjectName(u"base_url_input")
        self.base_url_input.setMinimumHeight(35)
        self.config_layout.addWidget(self.base_url_input, row, 3)
        
        # 源语言和目标语言
        row += 1
        self.source_lang_label = QLabel(self.config_frame)
        self.source_lang_label.setObjectName(u"source_lang_label")
        self.config_layout.addWidget(self.source_lang_label, row, 0)
        
        self.source_lang_combo = QComboBox(self.config_frame)
        self.source_lang_combo.setObjectName(u"source_lang_combo")
        self.source_lang_combo.setMinimumHeight(35)
        self.config_layout.addWidget(self.source_lang_combo, row, 1)
        
        self.target_lang_label = QLabel(self.config_frame)
        self.target_lang_label.setObjectName(u"target_lang_label")
        self.config_layout.addWidget(self.target_lang_label, row, 2)
        
        self.target_lang_combo = QComboBox(self.config_frame)
        self.target_lang_combo.setObjectName(u"target_lang_combo")
        self.target_lang_combo.setMinimumHeight(35)
        self.config_layout.addWidget(self.target_lang_combo, row, 3)
        
        # 批次大小和双语字幕选项
        row += 1
        self.batch_size_label = QLabel(self.config_frame)
        self.batch_size_label.setObjectName(u"batch_size_label")
        self.config_layout.addWidget(self.batch_size_label, row, 0)
        
        self.batch_size_spin = QSpinBox(self.config_frame)
        self.batch_size_spin.setObjectName(u"batch_size_spin")
        self.batch_size_spin.setMinimumHeight(35)
        self.batch_size_spin.setMinimum(1)
        self.batch_size_spin.setMaximum(50)
        self.batch_size_spin.setValue(10)
        self.config_layout.addWidget(self.batch_size_spin, row, 1)
        
        # 双语字幕勾选框
        self.bilingual_checkbox = QCheckBox(self.config_frame)
        self.bilingual_checkbox.setObjectName(u"bilingual_checkbox")
        self.bilingual_checkbox.setMinimumHeight(35)
        self.bilingual_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.bilingual_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border-color: #2196f3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:hover {
                border-color: #2196f3;
            }
        """)
        self.config_layout.addWidget(self.bilingual_checkbox, row, 2, 1, 2)
        
        # 网络代理
        row += 1
        self.proxy_label = QLabel(self.config_frame)
        self.proxy_label.setObjectName(u"proxy_label")
        self.config_layout.addWidget(self.proxy_label, row, 0)
        
        self.proxy_input = QLineEdit(self.config_frame)
        self.proxy_input.setObjectName(u"proxy_input")
        self.proxy_input.setMinimumHeight(35)
        self.proxy_input.setPlaceholderText("http://127.0.0.1:7890")
        self.config_layout.addWidget(self.proxy_input, row, 1, 1, 3)
        
        # 测试连接按钮
        row += 1
        self.test_btn = QPushButton(self.config_frame)
        self.test_btn.setObjectName(u"test_btn")
        self.test_btn.setMinimumHeight(40)
        self.test_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.config_layout.addWidget(self.test_btn, row, 0, 1, 4)
        
        self.main_layout.addWidget(self.config_frame)
        
        # 文件选择和操作按钮区域
        self.file_layout = QHBoxLayout()
        self.file_layout.setObjectName(u"file_layout")
        self.file_layout.setSpacing(10)
        
        self.select_file_btn = QPushButton(llmtrans)
        self.select_file_btn.setObjectName(u"select_file_btn")
        self.select_file_btn.setMinimumHeight(40)
        self.select_file_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.select_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.file_layout.addWidget(self.select_file_btn)
        
        self.selected_file_label = QLabel(llmtrans)
        self.selected_file_label.setObjectName(u"selected_file_label")
        self.selected_file_label.setStyleSheet("QLabel { color: #666; padding: 5px; }")
        self.file_layout.addWidget(self.selected_file_label, 1)
        
        self.main_layout.addLayout(self.file_layout)
        
        # 操作按钮区域
        self.action_layout = QHBoxLayout()
        self.action_layout.setObjectName(u"action_layout")
        self.action_layout.setSpacing(15)
        
        self.start_btn = QPushButton(llmtrans)
        self.start_btn.setObjectName(u"start_btn")
        self.start_btn.setMinimumHeight(45)
        self.start_btn.setMinimumWidth(150)
        self.start_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.action_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton(llmtrans)
        self.stop_btn.setObjectName(u"stop_btn")
        self.stop_btn.setMinimumHeight(45)
        self.stop_btn.setMinimumWidth(150)
        self.stop_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_btn.setDisabled(True)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.action_layout.addWidget(self.stop_btn)
        
        self.open_result_btn = QPushButton(llmtrans)
        self.open_result_btn.setObjectName(u"open_result_btn")
        self.open_result_btn.setMinimumHeight(45)
        self.open_result_btn.setMinimumWidth(150)
        self.open_result_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.open_result_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
        """)
        self.action_layout.addWidget(self.open_result_btn)
        
        self.action_layout.addStretch()
        
        self.main_layout.addLayout(self.action_layout)
        
        # 进度显示区域
        self.progress_label = QLabel(llmtrans)
        self.progress_label.setObjectName(u"progress_label")
        self.progress_label.setMinimumHeight(30)
        self.progress_label.setStyleSheet("QLabel { color: #2196f3; font-weight: bold; padding: 5px; }")
        self.main_layout.addWidget(self.progress_label)
        
        # 分割器（左右分栏）
        self.splitter = QSplitter(Qt.Horizontal, llmtrans)
        self.splitter.setObjectName(u"splitter")
        
        # 左侧：原文
        self.source_widget = QFrame(self.splitter)
        self.source_widget.setObjectName(u"source_widget")
        self.source_widget.setFrameShape(QFrame.StyledPanel)
        
        self.source_layout = QVBoxLayout(self.source_widget)
        self.source_layout.setObjectName(u"source_layout")
        self.source_layout.setContentsMargins(5, 5, 5, 5)
        
        self.source_title_label = QLabel(self.source_widget)
        self.source_title_label.setObjectName(u"source_title_label")
        from PySide6.QtGui import QFont
        source_font = QFont()
        source_font.setPointSize(12)
        source_font.setBold(True)
        self.source_title_label.setFont(source_font)
        self.source_title_label.setStyleSheet("QLabel { color: #4caf50; padding: 5px; }")
        self.source_layout.addWidget(self.source_title_label)
        
        self.source_text = QPlainTextEdit(self.source_widget)
        self.source_text.setObjectName(u"source_text")
        self.source_text.setReadOnly(True)
        self.source_text.setStyleSheet("QPlainTextEdit { border: 1px solid #ddd; border-radius: 3px; }")
        self.source_layout.addWidget(self.source_text)
        
        self.splitter.addWidget(self.source_widget)
        
        # 右侧：译文
        self.target_widget = QFrame(self.splitter)
        self.target_widget.setObjectName(u"target_widget")
        self.target_widget.setFrameShape(QFrame.StyledPanel)
        
        self.target_layout = QVBoxLayout(self.target_widget)
        self.target_layout.setObjectName(u"target_layout")
        self.target_layout.setContentsMargins(5, 5, 5, 5)
        
        self.target_title_label = QLabel(self.target_widget)
        self.target_title_label.setObjectName(u"target_title_label")
        target_font = QFont()
        target_font.setPointSize(12)
        target_font.setBold(True)
        self.target_title_label.setFont(target_font)
        self.target_title_label.setStyleSheet("QLabel { color: #2196f3; padding: 5px; }")
        self.target_layout.addWidget(self.target_title_label)
        
        self.target_text = QPlainTextEdit(self.target_widget)
        self.target_text.setObjectName(u"target_text")
        self.target_text.setReadOnly(True)
        self.target_text.setStyleSheet("QPlainTextEdit { border: 1px solid #ddd; border-radius: 3px; }")
        self.target_layout.addWidget(self.target_text)
        
        self.splitter.addWidget(self.target_widget)
        
        # 设置分割器初始比例
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        self.main_layout.addWidget(self.splitter)
        
        self.retranslateUi(llmtrans)
        
        QMetaObject.connectSlotsByName(llmtrans)
    
    def retranslateUi(self, llmtrans):
        if config.defaulelang == 'zh':
            llmtrans.setWindowTitle("🌍 AI字幕翻译 - 基于大语言模型")
            self.title_label.setText("🌍 AI字幕翻译 - 智能翻译字幕文件")
            self.provider_label.setText("LLM提供商:")
            self.api_key_label.setText("API Key:")
            self.model_label.setText("模型:")
            self.base_url_label.setText("API地址:")
            self.source_lang_label.setText("源语言:")
            self.target_lang_label.setText("目标语言:")
            self.batch_size_label.setText("批次大小:")
            self.bilingual_checkbox.setText("🌏 生成双语字幕（原文+译文）")
            self.proxy_label.setText("网络代理:")
            self.test_btn.setText("🔍 测试连接")
            self.select_file_btn.setText("📁 选择字幕文件 (.srt)")
            self.selected_file_label.setText("未选择文件")
            self.start_btn.setText("🚀 开始翻译")
            self.stop_btn.setText("⏹ 停止")
            self.open_result_btn.setText("📂 打开结果文件夹")
            self.progress_label.setText("就绪")
            self.source_title_label.setText("📄 原文字幕")
            self.target_title_label.setText("🌐 翻译结果")
            self.base_url_input.setPlaceholderText("可选，留空使用默认地址")
            self.api_key_input.setPlaceholderText("输入你的API Key")
        else:
            llmtrans.setWindowTitle("🌍 AI Subtitle Translation - Based on LLM")
            self.title_label.setText("🌍 AI Subtitle Translation - Intelligent subtitle translation")
            self.provider_label.setText("LLM Provider:")
            self.api_key_label.setText("API Key:")
            self.model_label.setText("Model:")
            self.base_url_label.setText("API Base URL:")
            self.source_lang_label.setText("Source Language:")
            self.target_lang_label.setText("Target Language:")
            self.batch_size_label.setText("Batch Size:")
            self.bilingual_checkbox.setText("🌏 Bilingual Subtitles (Source + Translation)")
            self.proxy_label.setText("Proxy:")
            self.test_btn.setText("🔍 Test Connection")
            self.select_file_btn.setText("📁 Select Subtitle File (.srt)")
            self.selected_file_label.setText("No file selected")
            self.start_btn.setText("🚀 Start Translation")
            self.stop_btn.setText("⏹ Stop")
            self.open_result_btn.setText("📂 Open Result Folder")
            self.progress_label.setText("Ready")
            self.source_title_label.setText("📄 Source Subtitle")
            self.target_title_label.setText("🌐 Translation Result")
            self.base_url_input.setPlaceholderText("Optional, leave blank to use default")
            self.api_key_input.setPlaceholderText("Enter your API Key")

