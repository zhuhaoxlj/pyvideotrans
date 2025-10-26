# AI智能字幕生成和断句工具 UI - 基于词级时间戳

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import (QMetaObject, QSize, Qt)
from PySide6.QtGui import (QCursor)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPlainTextEdit, QPushButton, QComboBox, QCheckBox,
                               QVBoxLayout, QGridLayout)

from videotrans.configure import config


class Ui_smartsplit(object):
    def setupUi(self, smartsplit):
        self.has_done = False
        if not smartsplit.objectName():
            smartsplit.setObjectName(u"smartsplit")
        smartsplit.resize(800, 700)
        smartsplit.setWindowModality(QtCore.Qt.NonModal)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(smartsplit.sizePolicy().hasHeightForWidth())
        smartsplit.setSizePolicy(sizePolicy)

        self.horizontalLayout_main = QHBoxLayout(smartsplit)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        
        # 添加说明标签
        self.info_label = QLabel(smartsplit)
        self.info_label.setObjectName(u"info_label")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { background-color: #e3f2fd; padding: 12px; border-radius: 5px; border: 2px solid #2196f3; }")
        self.verticalLayout.addWidget(self.info_label)
        
        # 文件选择区域
        self.horizontalLayout_file = QHBoxLayout()
        self.horizontalLayout_file.setObjectName(u"horizontalLayout_file")

        self.videoinput = QLineEdit(smartsplit)
        self.videoinput.setObjectName(u"videoinput")
        self.videoinput.setMinimumSize(QSize(0, 35))
        self.videoinput.setReadOnly(True)
        self.horizontalLayout_file.addWidget(self.videoinput)

        self.videobtn = QPushButton(smartsplit)
        self.videobtn.setObjectName(u"videobtn")
        self.videobtn.setMinimumSize(QSize(180, 35))
        self.videobtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.horizontalLayout_file.addWidget(self.videobtn)

        self.verticalLayout.addLayout(self.horizontalLayout_file)
        
        # 使用现有字幕选项
        self.use_existing_srt_checkbox = QCheckBox(smartsplit)
        self.use_existing_srt_checkbox.setObjectName(u"use_existing_srt_checkbox")
        self.use_existing_srt_checkbox.setStyleSheet("QCheckBox { font-weight: bold; color: #ff6f00; }")
        self.verticalLayout.addWidget(self.use_existing_srt_checkbox)
        
        # 字幕文件选择区域（默认隐藏）
        self.horizontalLayout_srt = QHBoxLayout()
        self.horizontalLayout_srt.setObjectName(u"horizontalLayout_srt")
        
        self.srtinput = QLineEdit(smartsplit)
        self.srtinput.setObjectName(u"srtinput")
        self.srtinput.setMinimumSize(QSize(0, 35))
        self.srtinput.setReadOnly(True)
        self.srtinput.setVisible(False)
        self.horizontalLayout_srt.addWidget(self.srtinput)
        
        self.srtbtn = QPushButton(smartsplit)
        self.srtbtn.setObjectName(u"srtbtn")
        self.srtbtn.setMinimumSize(QSize(180, 35))
        self.srtbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.srtbtn.setVisible(False)
        self.horizontalLayout_srt.addWidget(self.srtbtn)
        
        self.verticalLayout.addLayout(self.horizontalLayout_srt)
        
        # 参数设置区域（网格布局）
        self.gridLayout_params = QGridLayout()
        self.gridLayout_params.setObjectName(u"gridLayout_params")
        self.gridLayout_params.setVerticalSpacing(10)
        self.gridLayout_params.setHorizontalSpacing(15)
        
        # 语言选择
        self.language_label = QLabel(smartsplit)
        self.language_label.setObjectName(u"language_label")
        self.gridLayout_params.addWidget(self.language_label, 0, 0)
        
        self.language_combo = QComboBox(smartsplit)
        self.language_combo.setObjectName(u"language_combo")
        self.language_combo.setMinimumHeight(35)
        self.language_combo.addItems([
            "en=English", "zh=Chinese", "ja=Japanese", "ko=Korean",
            "es=Spanish", "fr=French", "de=German", "ru=Russian",
            "auto=Auto Detect"
        ])
        self.gridLayout_params.addWidget(self.language_combo, 0, 1)
        
        # 模型选择
        self.model_label = QLabel(smartsplit)
        self.model_label.setObjectName(u"model_label")
        self.gridLayout_params.addWidget(self.model_label, 1, 0)
        
        self.model_combo = QComboBox(smartsplit)
        self.model_combo.setObjectName(u"model_combo")
        self.model_combo.setMinimumHeight(35)
        self.model_combo.addItems([
            "large-v3-turbo", "large-v3", "medium", "small", "base"
        ])
        self.gridLayout_params.addWidget(self.model_combo, 1, 1)
        
        # 最大持续时间
        self.duration_label = QLabel(smartsplit)
        self.duration_label.setObjectName(u"duration_label")
        self.gridLayout_params.addWidget(self.duration_label, 2, 0)
        
        self.duration_input = QLineEdit(smartsplit)
        self.duration_input.setObjectName(u"duration_input")
        self.duration_input.setMinimumHeight(35)
        self.duration_input.setText("5")
        self.gridLayout_params.addWidget(self.duration_input, 2, 1)
        
        # 最大词数
        self.words_label = QLabel(smartsplit)
        self.words_label.setObjectName(u"words_label")
        self.gridLayout_params.addWidget(self.words_label, 3, 0)
        
        self.words_input = QLineEdit(smartsplit)
        self.words_input.setObjectName(u"words_input")
        self.words_input.setMinimumHeight(35)
        self.words_input.setText("15")
        self.gridLayout_params.addWidget(self.words_input, 3, 1)
        
        # 设备选择
        self.device_label = QLabel(smartsplit)
        self.device_label.setObjectName(u"device_label")
        self.gridLayout_params.addWidget(self.device_label, 4, 0)
        
        self.device_combo = QComboBox(smartsplit)
        self.device_combo.setObjectName(u"device_combo")
        self.device_combo.setMinimumHeight(35)
        # 根据系统自动添加可用设备
        self._setup_device_options(smartsplit)
        self.gridLayout_params.addWidget(self.device_combo, 4, 1)
        
        self.verticalLayout.addLayout(self.gridLayout_params)

        # 开始按钮
        self.startbtn = QPushButton(smartsplit)
        self.startbtn.setObjectName(u"startbtn")
        self.startbtn.setMinimumSize(QSize(0, 45))
        self.startbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.startbtn.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; background-color: #4caf50; color: white; } QPushButton:hover { background-color: #45a049; }")
        self.verticalLayout.addWidget(self.startbtn)
        
        # 日志区域标签
        self.log_title = QLabel(smartsplit)
        self.log_title.setObjectName(u"log_title")
        self.log_title.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; font-size: 13px; }")
        self.verticalLayout.addWidget(self.log_title)

        # 日志显示区域
        self.loglabel = QPlainTextEdit(smartsplit)
        self.loglabel.setObjectName(u"loglabel")
        self.loglabel.setReadOnly(True)
        self.loglabel.setMaximumHeight(150)
        self.loglabel.setStyleSheet("QPlainTextEdit { background-color: #263238; color: #aed581; font-family: 'Consolas', 'Monaco', monospace; }")
        self.verticalLayout.addWidget(self.loglabel)
        
        # 结果预览标签
        self.result_title = QLabel(smartsplit)
        self.result_title.setObjectName(u"result_title")
        self.result_title.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; font-size: 13px; }")
        self.verticalLayout.addWidget(self.result_title)

        # 结果预览区域
        self.resultinput = QPlainTextEdit(smartsplit)
        self.resultinput.setObjectName(u"resultinput")
        self.resultinput.setReadOnly(True)
        self.verticalLayout.addWidget(self.resultinput)

        # 结果文件路径
        self.resultlabel = QLabel(smartsplit)
        self.resultlabel.setObjectName(u"resultlabel")
        self.resultlabel.setWordWrap(True)
        self.resultlabel.setStyleSheet("QLabel { color: green; font-weight: bold; }")
        self.verticalLayout.addWidget(self.resultlabel)

        # 打开目录按钮
        self.resultbtn = QPushButton(smartsplit)
        self.resultbtn.setObjectName(u"resultbtn")
        self.resultbtn.setMinimumSize(QSize(0, 35))
        self.resultbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.resultbtn.setDisabled(True)
        self.verticalLayout.addWidget(self.resultbtn)

        self.horizontalLayout_main.addLayout(self.verticalLayout)

        self.retranslateUi(smartsplit)

        QMetaObject.connectSlotsByName(smartsplit)

    # setupUi
    
    def _setup_device_options(self, smartsplit):
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
        
        # 注意：faster-whisper 暂不支持 MPS
        # 如果选择MPS，程序会自动回退到CPU
        # 检测MPS (Apple Silicon) - 暂时注释掉，因为faster-whisper不支持
        # if platform.system() == 'Darwin':  # macOS
        #     try:
        #         import torch
        #         if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        #             self.device_combo.addItem("MPS (实验性)")
        #     except:
        #         pass

    def retranslateUi(self, smartsplit):
        smartsplit.setWindowTitle("AI智能字幕生成（词级时间戳）" if config.defaulelang == 'zh' else 'AI Smart Subtitle Generator (Word-Level)')
        
        info_text = """
        <b>🤖 AI智能字幕生成和断句工具</b><br>
        <b style="color: #2196f3;">✨ 基于 Faster-Whisper 的词级时间戳</b><br><br>
        <b>特点：</b><br>
        • 🎯 精确到每个词的时间戳，不是简单的平均分配<br>
        • 🧠 智能识别句子和从句边界<br>
        • ⚡ 自动优化字幕长度和持续时间<br>
        • 🌍 支持多种语言，自动语音识别
        """ if config.defaulelang == 'zh' else """
        <b>🤖 AI Smart Subtitle Generator</b><br>
        <b style="color: #2196f3;">✨ Based on Faster-Whisper Word-Level Timestamps</b><br><br>
        <b>Features:</b><br>
        • 🎯 Accurate word-level timestamps<br>
        • 🧠 Smart sentence and clause boundary detection<br>
        • ⚡ Auto-optimized subtitle length and duration<br>
        • 🌍 Multi-language support with auto-detection
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
        
        self.language_label.setText("语言:" if config.defaulelang == 'zh' else 'Language:')
        self.model_label.setText("模型:" if config.defaulelang == 'zh' else 'Model:')
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

