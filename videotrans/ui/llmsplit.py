# LLM智能字幕断句 UI - 基于语义理解

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import (QMetaObject, QSize, Qt)
from PySide6.QtGui import (QCursor)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPlainTextEdit, QPushButton, QComboBox, QCheckBox,
                               QVBoxLayout, QGridLayout)

from videotrans.configure import config


class Ui_llmsplit(object):
    def setupUi(self, llmsplit):
        self.has_done = False
        if not llmsplit.objectName():
            llmsplit.setObjectName(u"llmsplit")
        llmsplit.resize(900, 800)
        llmsplit.setWindowModality(QtCore.Qt.NonModal)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(llmsplit.sizePolicy().hasHeightForWidth())
        llmsplit.setSizePolicy(sizePolicy)

        self.horizontalLayout_main = QHBoxLayout(llmsplit)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        
        # 添加说明标签
        self.info_label = QLabel(llmsplit)
        self.info_label.setObjectName(u"info_label")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { background-color: #e3f2fd; padding: 12px; border-radius: 5px; border: 2px solid #2196f3; }")
        self.verticalLayout.addWidget(self.info_label)
        
        # 文件选择区域
        self.horizontalLayout_file = QHBoxLayout()
        self.horizontalLayout_file.setObjectName(u"horizontalLayout_file")

        self.videoinput = QLineEdit(llmsplit)
        self.videoinput.setObjectName(u"videoinput")
        self.videoinput.setMinimumSize(QSize(0, 35))
        self.videoinput.setReadOnly(True)
        self.horizontalLayout_file.addWidget(self.videoinput)

        self.videobtn = QPushButton(llmsplit)
        self.videobtn.setObjectName(u"videobtn")
        self.videobtn.setMinimumSize(QSize(180, 35))
        self.videobtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.horizontalLayout_file.addWidget(self.videobtn)

        self.verticalLayout.addLayout(self.horizontalLayout_file)
        
        # 使用现有字幕选项
        self.use_existing_srt_checkbox = QCheckBox(llmsplit)
        self.use_existing_srt_checkbox.setObjectName(u"use_existing_srt_checkbox")
        self.use_existing_srt_checkbox.setStyleSheet("QCheckBox { font-weight: bold; color: #ff6f00; }")
        self.verticalLayout.addWidget(self.use_existing_srt_checkbox)
        
        # 字幕文件选择区域（默认隐藏）
        self.horizontalLayout_srt = QHBoxLayout()
        self.horizontalLayout_srt.setObjectName(u"horizontalLayout_srt")
        
        self.srtinput = QLineEdit(llmsplit)
        self.srtinput.setObjectName(u"srtinput")
        self.srtinput.setMinimumSize(QSize(0, 35))
        self.srtinput.setReadOnly(True)
        self.srtinput.setVisible(False)
        self.horizontalLayout_srt.addWidget(self.srtinput)
        
        self.srtbtn = QPushButton(llmsplit)
        self.srtbtn.setObjectName(u"srtbtn")
        self.srtbtn.setMinimumSize(QSize(180, 35))
        self.srtbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.srtbtn.setVisible(False)
        self.horizontalLayout_srt.addWidget(self.srtbtn)
        
        self.verticalLayout.addLayout(self.horizontalLayout_srt)
        
        # 使用 LLM 优化选项
        self.use_llm_checkbox = QCheckBox(llmsplit)
        self.use_llm_checkbox.setObjectName(u"use_llm_checkbox")
        self.use_llm_checkbox.setStyleSheet("QCheckBox { font-weight: bold; color: #1976d2; font-size: 14px; }")
        self.use_llm_checkbox.setChecked(True)  # 默认启用
        self.verticalLayout.addWidget(self.use_llm_checkbox)
        
        # LLM 配置区域
        self.gridLayout_llm = QGridLayout()
        self.gridLayout_llm.setObjectName(u"gridLayout_llm")
        self.gridLayout_llm.setVerticalSpacing(10)
        self.gridLayout_llm.setHorizontalSpacing(15)
        
        # LLM 提供商
        self.llm_provider_label = QLabel(llmsplit)
        self.llm_provider_label.setObjectName(u"llm_provider_label")
        self.gridLayout_llm.addWidget(self.llm_provider_label, 0, 0)
        
        self.llm_provider_combo = QComboBox(llmsplit)
        self.llm_provider_combo.setObjectName(u"llm_provider_combo")
        self.llm_provider_combo.setMinimumHeight(35)
        self.llm_provider_combo.addItems(["OpenAI", "Anthropic", "DeepSeek", "SiliconFlow", "Local"])
        self.gridLayout_llm.addWidget(self.llm_provider_combo, 0, 1)
        
        # API Key
        self.llm_api_key_label = QLabel(llmsplit)
        self.llm_api_key_label.setObjectName(u"llm_api_key_label")
        self.gridLayout_llm.addWidget(self.llm_api_key_label, 1, 0)
        
        self.llm_api_key_input = QLineEdit(llmsplit)
        self.llm_api_key_input.setObjectName(u"llm_api_key_input")
        self.llm_api_key_input.setMinimumHeight(35)
        self.llm_api_key_input.setEchoMode(QLineEdit.Password)
        self.gridLayout_llm.addWidget(self.llm_api_key_input, 1, 1)
        
        # Model - 改为可编辑的下拉框
        self.llm_model_label = QLabel(llmsplit)
        self.llm_model_label.setObjectName(u"llm_model_label")
        self.gridLayout_llm.addWidget(self.llm_model_label, 2, 0)
        
        self.llm_model_combo = QComboBox(llmsplit)
        self.llm_model_combo.setObjectName(u"llm_model_combo")
        self.llm_model_combo.setMinimumHeight(35)
        self.llm_model_combo.setEditable(True)  # 允许用户自己输入
        self.llm_model_combo.addItem("gpt-4o-mini")  # 默认模型
        self.gridLayout_llm.addWidget(self.llm_model_combo, 2, 1)
        
        # Base URL (可选)
        self.llm_base_url_label = QLabel(llmsplit)
        self.llm_base_url_label.setObjectName(u"llm_base_url_label")
        self.gridLayout_llm.addWidget(self.llm_base_url_label, 3, 0)
        
        self.llm_base_url_input = QLineEdit(llmsplit)
        self.llm_base_url_input.setObjectName(u"llm_base_url_input")
        self.llm_base_url_input.setMinimumHeight(35)
        self.gridLayout_llm.addWidget(self.llm_base_url_input, 3, 1)
        
        # 测试连接按钮
        self.llm_test_btn = QPushButton(llmsplit)
        self.llm_test_btn.setObjectName(u"llm_test_btn")
        self.llm_test_btn.setMinimumSize(QSize(0, 35))
        self.llm_test_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.llm_test_btn.setStyleSheet("QPushButton { background-color: #2196f3; color: white; } QPushButton:hover { background-color: #1976d2; }")
        self.gridLayout_llm.addWidget(self.llm_test_btn, 4, 0, 1, 2)
        
        self.verticalLayout.addLayout(self.gridLayout_llm)
        
        # 参数设置区域（网格布局）
        self.gridLayout_params = QGridLayout()
        self.gridLayout_params.setObjectName(u"gridLayout_params")
        self.gridLayout_params.setVerticalSpacing(10)
        self.gridLayout_params.setHorizontalSpacing(15)
        
        # 语言选择
        self.language_label = QLabel(llmsplit)
        self.language_label.setObjectName(u"language_label")
        self.gridLayout_params.addWidget(self.language_label, 0, 0)
        
        self.language_combo = QComboBox(llmsplit)
        self.language_combo.setObjectName(u"language_combo")
        self.language_combo.setMinimumHeight(35)
        self.language_combo.addItems([
            "en=English", "zh=Chinese", "ja=Japanese", "ko=Korean",
            "es=Spanish", "fr=French", "de=German", "ru=Russian",
            "auto=Auto Detect"
        ])
        self.gridLayout_params.addWidget(self.language_combo, 0, 1)
        
        # 模型选择
        self.model_label = QLabel(llmsplit)
        self.model_label.setObjectName(u"model_label")
        self.gridLayout_params.addWidget(self.model_label, 1, 0)
        
        self.model_combo = QComboBox(llmsplit)
        self.model_combo.setObjectName(u"model_combo")
        self.model_combo.setMinimumHeight(35)
        self.model_combo.addItems([
            "large-v3-turbo", "large-v3", "medium", "small", "base"
        ])
        self.gridLayout_params.addWidget(self.model_combo, 1, 1)
        
        # 最大持续时间
        self.duration_label = QLabel(llmsplit)
        self.duration_label.setObjectName(u"duration_label")
        self.gridLayout_params.addWidget(self.duration_label, 2, 0)
        
        self.duration_input = QLineEdit(llmsplit)
        self.duration_input.setObjectName(u"duration_input")
        self.duration_input.setMinimumHeight(35)
        self.duration_input.setText("5")
        self.gridLayout_params.addWidget(self.duration_input, 2, 1)
        
        # 最大词数
        self.words_label = QLabel(llmsplit)
        self.words_label.setObjectName(u"words_label")
        self.gridLayout_params.addWidget(self.words_label, 3, 0)
        
        self.words_input = QLineEdit(llmsplit)
        self.words_input.setObjectName(u"words_input")
        self.words_input.setMinimumHeight(35)
        self.words_input.setText("15")
        self.gridLayout_params.addWidget(self.words_input, 3, 1)
        
        # 设备选择
        self.device_label = QLabel(llmsplit)
        self.device_label.setObjectName(u"device_label")
        self.gridLayout_params.addWidget(self.device_label, 4, 0)
        
        self.device_combo = QComboBox(llmsplit)
        self.device_combo.setObjectName(u"device_combo")
        self.device_combo.setMinimumHeight(35)
        self._setup_device_options(llmsplit)
        self.gridLayout_params.addWidget(self.device_combo, 4, 1)
        
        self.verticalLayout.addLayout(self.gridLayout_params)

        # 开始按钮
        self.startbtn = QPushButton(llmsplit)
        self.startbtn.setObjectName(u"startbtn")
        self.startbtn.setMinimumSize(QSize(0, 45))
        self.startbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.startbtn.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; background-color: #4caf50; color: white; } QPushButton:hover { background-color: #45a049; }")
        self.verticalLayout.addWidget(self.startbtn)
        
        # 日志区域标签
        self.log_title = QLabel(llmsplit)
        self.log_title.setObjectName(u"log_title")
        self.log_title.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; font-size: 13px; }")
        self.verticalLayout.addWidget(self.log_title)

        # 日志显示区域
        self.loglabel = QPlainTextEdit(llmsplit)
        self.loglabel.setObjectName(u"loglabel")
        self.loglabel.setReadOnly(True)
        self.loglabel.setMaximumHeight(150)
        self.loglabel.setStyleSheet("QPlainTextEdit { background-color: #263238; color: #aed581; font-family: 'Consolas', 'Monaco', monospace; }")
        self.verticalLayout.addWidget(self.loglabel)
        
        # 结果预览标签
        self.result_title = QLabel(llmsplit)
        self.result_title.setObjectName(u"result_title")
        self.result_title.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; font-size: 13px; }")
        self.verticalLayout.addWidget(self.result_title)

        # 结果预览区域
        self.resultinput = QPlainTextEdit(llmsplit)
        self.resultinput.setObjectName(u"resultinput")
        self.resultinput.setReadOnly(True)
        self.verticalLayout.addWidget(self.resultinput)

        # 结果文件路径
        self.resultlabel = QLabel(llmsplit)
        self.resultlabel.setObjectName(u"resultlabel")
        self.resultlabel.setWordWrap(True)
        self.resultlabel.setStyleSheet("QLabel { color: green; font-weight: bold; }")
        self.verticalLayout.addWidget(self.resultlabel)

        # 打开目录按钮
        self.resultbtn = QPushButton(llmsplit)
        self.resultbtn.setObjectName(u"resultbtn")
        self.resultbtn.setMinimumSize(QSize(0, 35))
        self.resultbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.resultbtn.setDisabled(True)
        self.verticalLayout.addWidget(self.resultbtn)

        self.horizontalLayout_main.addLayout(self.verticalLayout)

        self.retranslateUi(llmsplit)

        # 连接信号：当提供商改变时自动填充 Base URL 和模型列表
        self.llm_provider_combo.currentTextChanged.connect(self._on_provider_changed)
        
        # 初始化默认提供商的模型列表
        self._on_provider_changed(self.llm_provider_combo.currentText())

        QMetaObject.connectSlotsByName(llmsplit)

    # setupUi
    
    def _on_provider_changed(self, provider_name):
        """当 LLM 提供商改变时，自动填充默认的 Base URL 和模型列表"""
        # Base URL 映射
        base_urls = {
            "SiliconFlow": "https://api.siliconflow.cn/v1/chat/completions",
            "OpenAI": "",  # OpenAI 使用默认，不需要填
            "Anthropic": "",
            "DeepSeek": "",
            "Local": "http://localhost:11434/api/generate"
        }
        
        # 各提供商的模型列表
        provider_models = {
            "SiliconFlow": [
                "Qwen/Qwen2.5-7B-Instruct",
                "deepseek-ai/DeepSeek-V3",
                "deepseek-ai/DeepSeek-R1",
                "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
                "inclusionAI/Ling-1T",
                "Qwen/QwQ-32B",
                "Qwen/Qwen2.5-72B-Instruct"
            ],
            "OpenAI": [
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ],
            "Anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-haiku-20240307",
                "claude-3-opus-20240229"
            ],
            "DeepSeek": [
                "deepseek-chat",
                "deepseek-coder"
            ],
            "Local": [
                "llama3",
                "qwen",
                "mistral",
                "gemma"
            ]
        }
        
        # 设置 Base URL
        if provider_name in base_urls:
            self.llm_base_url_input.setText(base_urls[provider_name])
        
        # 更新模型下拉列表
        self.llm_model_combo.clear()
        if provider_name in provider_models:
            self.llm_model_combo.addItems(provider_models[provider_name])
            # 设置第一个为默认选中
            self.llm_model_combo.setCurrentIndex(0)
    
    def _setup_device_options(self, llmsplit):
        """设置可用的设备选项"""
        import platform
        
        # 默认添加CPU
        self.device_combo.addItem("CPU")
        
        # 检测CUDA
        try:
            import torch
            if torch.cuda.is_available():
                self.device_combo.addItem("CUDA")
        except:
            pass

    def retranslateUi(self, llmsplit):
        llmsplit.setWindowTitle("🤖 LLM智能字幕生成（AI语义理解）" if config.defaulelang == 'zh' else '🤖 LLM Smart Subtitle Generator (AI Semantic)')
        
        info_text = """
        <b>🤖 LLM智能字幕生成和断句工具</b><br>
        <b style="color: #1976d2;">✨ 基于 AI 语义理解的智能断句</b><br><br>
        <b>核心特点：</b><br>
        • 🧠 使用大语言模型理解完整语义<br>
        • 🎯 基于 Faster-Whisper 的词级时间戳<br>
        • 📝 自然的断句位置，接近人工编辑质量<br>
        • 🔄 支持重新分割网上下载的长句字幕<br>
        • 🌍 支持多种 LLM 提供商（OpenAI, Claude, DeepSeek, 本地模型）
        """ if config.defaulelang == 'zh' else """
        <b>🤖 LLM Smart Subtitle Generator</b><br>
        <b style="color: #1976d2;">✨ Based on AI Semantic Understanding</b><br><br>
        <b>Key Features:</b><br>
        • 🧠 Uses Large Language Models for semantic understanding<br>
        • 🎯 Based on Faster-Whisper word-level timestamps<br>
        • 📝 Natural break points, near human-quality<br>
        • 🔄 Re-split long downloaded subtitles<br>
        • 🌍 Multiple LLM providers (OpenAI, Claude, DeepSeek, Local)
        """
        
        self.info_label.setText(info_text)
        
        self.videoinput.setPlaceholderText(
            "请选择视频或音频文件" if config.defaulelang == 'zh' else 'Select video or audio file')
        
        self.videobtn.setText("选择视频/音频" if config.defaulelang == 'zh' else 'Select Video/Audio')
        
        self.use_existing_srt_checkbox.setText(
            "🔄 使用现有字幕文件（重新智能分割长句）" if config.defaulelang == 'zh' else '🔄 Use Existing Subtitle File (Re-split Long Sentences)')
        
        self.srtinput.setPlaceholderText(
            "请选择字幕文件" if config.defaulelang == 'zh' else 'Select subtitle file')
        
        self.srtbtn.setText("选择字幕文件(.srt)" if config.defaulelang == 'zh' else 'Select Subtitle (.srt)')
        
        self.use_llm_checkbox.setText(
            "🤖 启用 LLM 智能断句优化（推荐）" if config.defaulelang == 'zh' else '🤖 Enable LLM Smart Split (Recommended)')
        
        self.llm_provider_label.setText("LLM 提供商:" if config.defaulelang == 'zh' else 'LLM Provider:')
        self.llm_api_key_label.setText("API Key:" if config.defaulelang == 'zh' else 'API Key:')
        self.llm_model_label.setText("模型:" if config.defaulelang == 'zh' else 'Model:')
        self.llm_base_url_label.setText("Base URL (可选):" if config.defaulelang == 'zh' else 'Base URL (Optional):')
        
        self.llm_api_key_input.setPlaceholderText(
            "输入你的 API Key" if config.defaulelang == 'zh' else 'Enter your API Key')
        self.llm_model_combo.setCurrentText("gpt-4o-mini")
        self.llm_base_url_input.setPlaceholderText(
            "可选，用于自定义 API 端点" if config.defaulelang == 'zh' else 'Optional, for custom API endpoint')
        
        self.llm_test_btn.setText(
            "🔍 测试 LLM 连接" if config.defaulelang == 'zh' else '🔍 Test LLM Connection')
        
        self.language_label.setText("语言:" if config.defaulelang == 'zh' else 'Language:')
        self.model_label.setText("Whisper模型:" if config.defaulelang == 'zh' else 'Whisper Model:')
        self.duration_label.setText("最大持续时间(秒):" if config.defaulelang == 'zh' else 'Max Duration (sec):')
        self.words_label.setText("最大词数:" if config.defaulelang == 'zh' else 'Max Words:')
        self.device_label.setText("🚀 加速设备:" if config.defaulelang == 'zh' else '🚀 Device:')
        
        self.startbtn.setText("🎬 开始生成智能字幕" if config.defaulelang == 'zh' else '🎬 Generate Smart Subtitles')
        
        self.log_title.setText("📋 处理日志:" if config.defaulelang == 'zh' else '📋 Processing Log:')
        self.result_title.setText("📄 生成的字幕:" if config.defaulelang == 'zh' else '📄 Generated Subtitles:')
        
        self.resultlabel.setText("")
        self.resultinput.setPlaceholderText(
            "生成的字幕将显示在这里..." if config.defaulelang == 'zh' else "Generated subtitles will be displayed here...")
        self.loglabel.setPlaceholderText(
            "处理日志将显示在这里..." if config.defaulelang == 'zh' else "Processing log will be displayed here...")
        self.resultbtn.setText("📁 打开保存目录" if config.defaulelang == 'zh' else '📁 Open Save Directory')
    # retranslateUi

