# LLM智能字幕断句 UI - 基于语义理解

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import (QMetaObject, QSize, Qt, QUrl)
from PySide6.QtGui import (QCursor, QDragEnterEvent, QDropEvent)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPlainTextEdit, QPushButton, QComboBox, QCheckBox,
                               QVBoxLayout, QGridLayout, QSplitter, QFrame)

from videotrans.configure import config


class DragDropButton(QPushButton):
    """支持拖放文件的按钮，拖入文件时会高亮显示"""
    
    def __init__(self, text="", parent=None, file_filter=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.file_filter = file_filter or []  # 允许的文件扩展名列表
        self._original_style = ""
        self.selected_file = ""
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖入事件 - 文件进入按钮区域时高亮显示"""
        if event.mimeData().hasUrls():
            # 检查是否是本地文件
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                # 如果没有指定过滤器，或者文件符合过滤器
                if not self.file_filter or any(file_path.lower().endswith(ext) for ext in self.file_filter):
                    event.acceptProposedAction()
                    # 高亮显示：更明显的绿色边框和背景
                    self._original_style = self.styleSheet()
                    self.setStyleSheet(self._original_style + " QPushButton { border: 3px dashed #4caf50; background-color: #4caf50; }")
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖出事件 - 文件离开按钮区域时恢复原样"""
        self.setStyleSheet(self._original_style)
    
    def dropEvent(self, event: QDropEvent):
        """放下事件 - 文件被放下时设置文件路径"""
        self.setStyleSheet(self._original_style)
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                # 如果没有指定过滤器，或者文件符合过滤器
                if not self.file_filter or any(file_path.lower().endswith(ext) for ext in self.file_filter):
                    self.selected_file = file_path
                    event.acceptProposedAction()
                    # 触发点击事件，通知外部文件已选择
                    self.clicked.emit()
                    return
        event.ignore()


class Ui_llmsplit(object):
    def setupUi(self, llmsplit):
        self.has_done = False
        if not llmsplit.objectName():
            llmsplit.setObjectName(u"llmsplit")
        
        # 获取屏幕可用高度和宽度
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_height = screen_geometry.height()
            screen_width = screen_geometry.width()
            # 设置窗口为全屏大小（留一点边距）
            window_height = int(screen_height * 0.95)
            window_width = int(screen_width * 0.95)
            llmsplit.resize(window_width, window_height)
        else:
            # 如果无法获取屏幕信息，使用默认值
            llmsplit.resize(1600, 900)
        
        llmsplit.setWindowModality(QtCore.Qt.NonModal)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(llmsplit.sizePolicy().hasHeightForWidth())
        llmsplit.setSizePolicy(sizePolicy)
        
        # 设置最小尺寸
        llmsplit.setMinimumSize(QSize(1200, 700))

        # 主布局
        self.horizontalLayout_main = QHBoxLayout(llmsplit)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.horizontalLayout_main.setContentsMargins(10, 10, 10, 10)
        
        # 创建分割器（左右分栏）
        self.splitter = QSplitter(Qt.Horizontal, llmsplit)
        self.splitter.setObjectName(u"splitter")
        
        # 检测系统主题（深色/浅色）
        from PySide6.QtGui import QPalette
        palette = llmsplit.palette()
        is_dark_theme = palette.color(QPalette.Window).lightness() < 128
        
        # ================ 左侧面板：输入控件 ================
        self.left_widget = QFrame()
        self.left_widget.setFrameShape(QFrame.StyledPanel)
        
        # 根据主题设置背景色
        if is_dark_theme:
            left_bg_color = "#2b2b2b"  # 深色主题
            self.left_widget.setStyleSheet(f"QFrame {{ background-color: {left_bg_color}; border-radius: 5px; }}")
        else:
            left_bg_color = "#f5f5f5"  # 浅色主题
            self.left_widget.setStyleSheet(f"QFrame {{ background-color: {left_bg_color}; border-radius: 5px; }}")
        
        self.verticalLayout = QVBoxLayout(self.left_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        
        # 保存主题信息供后续使用
        self.is_dark_theme = is_dark_theme
        
        # 添加说明标签
        self.info_label = QLabel(llmsplit)
        self.info_label.setObjectName(u"info_label")
        self.info_label.setWordWrap(True)
        
        # 根据主题设置 info_label 样式
        if is_dark_theme:
            info_style = "QLabel { background-color: #1e3a5f; color: #90caf9; padding: 12px; border-radius: 5px; border: 2px solid #2196f3; }"
        else:
            info_style = "QLabel { background-color: #e3f2fd; color: #1a237e; padding: 12px; border-radius: 5px; border: 2px solid #2196f3; }"
        
        self.info_label.setStyleSheet(info_style)
        self.verticalLayout.addWidget(self.info_label)
        
        # 文件选择区域 - 只保留按钮，支持拖放和点击
        video_filters = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.mp3', '.wav', '.flac', '.m4a']
        self.videobtn = DragDropButton("", llmsplit, file_filter=video_filters)
        self.videobtn.setObjectName(u"videobtn")
        self.videobtn.setMinimumSize(QSize(0, 60))
        self.videobtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.videobtn.setStyleSheet("QPushButton { font-size: 14px; font-weight: bold; }")
        self.verticalLayout.addWidget(self.videobtn)
        
        # 显示已选择的文件路径
        self.videoinput = QLabel(llmsplit)
        self.videoinput.setObjectName(u"videoinput")
        self.videoinput.setWordWrap(True)
        # 适配主题的文件路径颜色
        video_input_color = "#64b5f6" if is_dark_theme else "#2196f3"
        self.videoinput.setStyleSheet(f"QLabel {{ color: {video_input_color}; padding: 5px; }}")
        self.verticalLayout.addWidget(self.videoinput)
        
        # 使用现有字幕选项
        self.use_existing_srt_checkbox = QCheckBox(llmsplit)
        self.use_existing_srt_checkbox.setObjectName(u"use_existing_srt_checkbox")
        # 适配主题的复选框颜色
        checkbox_color = "#ffab40" if is_dark_theme else "#ff6f00"
        self.use_existing_srt_checkbox.setStyleSheet(f"QCheckBox {{ font-weight: bold; color: {checkbox_color}; }}")
        self.verticalLayout.addWidget(self.use_existing_srt_checkbox)
        
        # 字幕文件选择区域（默认隐藏）- 只保留按钮，支持拖放和点击
        srt_filters = ['.srt']
        self.srtbtn = DragDropButton("", llmsplit, file_filter=srt_filters)
        self.srtbtn.setObjectName(u"srtbtn")
        self.srtbtn.setMinimumSize(QSize(0, 60))
        self.srtbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.srtbtn.setStyleSheet("QPushButton { font-size: 14px; font-weight: bold; }")
        self.srtbtn.setVisible(False)
        self.verticalLayout.addWidget(self.srtbtn)
        
        # 显示已选择的字幕文件路径
        self.srtinput = QLabel(llmsplit)
        self.srtinput.setObjectName(u"srtinput")
        self.srtinput.setWordWrap(True)
        # 适配主题的文件路径颜色
        srt_input_color = "#64b5f6" if is_dark_theme else "#2196f3"
        self.srtinput.setStyleSheet(f"QLabel {{ color: {srt_input_color}; padding: 5px; }}")
        self.srtinput.setVisible(False)
        self.verticalLayout.addWidget(self.srtinput)
        
        # 使用 LLM 优化选项
        self.use_llm_checkbox = QCheckBox(llmsplit)
        self.use_llm_checkbox.setObjectName(u"use_llm_checkbox")
        # 适配主题的复选框颜色
        llm_checkbox_color = "#64b5f6" if is_dark_theme else "#1976d2"
        self.use_llm_checkbox.setStyleSheet(f"QCheckBox {{ font-weight: bold; color: {llm_checkbox_color}; font-size: 14px; }}")
        self.use_llm_checkbox.setChecked(True)  # 默认启用
        self.verticalLayout.addWidget(self.use_llm_checkbox)
        
        # 创建水平布局，左侧是LLM配置，右侧是测试按钮
        self.horizontalLayout_llm = QHBoxLayout()
        self.horizontalLayout_llm.setObjectName(u"horizontalLayout_llm")
        
        # LLM 配置区域（左侧）
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
        self.llm_provider_combo.setCurrentText("SiliconFlow")  # 默认选择 SiliconFlow
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
        
        self.horizontalLayout_llm.addLayout(self.gridLayout_llm)
        
        # 测试连接按钮 - 放在右侧，与LLM配置区域等高
        self.llm_test_btn = QPushButton(llmsplit)
        self.llm_test_btn.setObjectName(u"llm_test_btn")
        # 计算高度：4行 × 35px + 3个间距 × 10px = 140px + 30px = 170px
        # 使用固定高度确保对齐
        self.llm_test_btn.setFixedHeight(170)
        self.llm_test_btn.setMinimumWidth(120)
        self.llm_test_btn.setMaximumWidth(150)
        self.llm_test_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.llm_test_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2196f3; 
                color: white; 
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
            } 
            QPushButton:hover { 
                background-color: #1976d2; 
            }
        """)
        self.horizontalLayout_llm.addWidget(self.llm_test_btn, 0, Qt.AlignTop)
        
        self.verticalLayout.addLayout(self.horizontalLayout_llm)
        
        # 创建水平布局，左侧是参数设置，右侧是开始按钮
        self.horizontalLayout_params = QHBoxLayout()
        self.horizontalLayout_params.setObjectName(u"horizontalLayout_params")
        
        # 参数设置区域（网格布局，2列：标签、输入框）
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
        
        self.horizontalLayout_params.addLayout(self.gridLayout_params)
        
        # 开始按钮 - 放在右侧，与参数设置区域等高
        self.startbtn = QPushButton(llmsplit)
        self.startbtn.setObjectName(u"startbtn")
        self.startbtn.setMinimumWidth(120)
        self.startbtn.setMaximumWidth(150)
        # 计算高度：5行 × 35px + 4个间距 × 10px = 175px + 40px = 215px
        # 使用固定高度确保对齐
        self.startbtn.setFixedHeight(215)
        self.startbtn.setCursor(QCursor(Qt.PointingHandCursor))
        # 支持文字换行显示
        self.startbtn.setStyleSheet("""
            QPushButton { 
                font-size: 14px; 
                font-weight: bold; 
                background-color: #4caf50; 
                color: white; 
                padding: 10px;
                text-align: center;
            } 
            QPushButton:hover { 
                background-color: #45a049; 
            }
        """)
        self.horizontalLayout_params.addWidget(self.startbtn, 0, Qt.AlignTop)
        
        self.verticalLayout.addLayout(self.horizontalLayout_params)
        
        # 左侧添加一个弹性空间，将控件推到上方
        self.verticalLayout.addStretch()
        
        # 将左侧 widget 添加到分割器
        self.splitter.addWidget(self.left_widget)
        
        # ================ 右侧面板：日志和结果 ================
        self.right_widget = QFrame()
        self.right_widget.setFrameShape(QFrame.StyledPanel)
        
        # 根据主题设置右侧背景色
        if is_dark_theme:
            right_bg_color = "#1e1e1e"  # 深色主题
            self.right_widget.setStyleSheet(f"QFrame {{ background-color: {right_bg_color}; border-radius: 5px; }}")
        else:
            right_bg_color = "#ffffff"  # 浅色主题
            self.right_widget.setStyleSheet(f"QFrame {{ background-color: {right_bg_color}; border-radius: 5px; }}")
        
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setObjectName(u"right_layout")
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(10)
        
        # --------- 上半部分：处理日志 ---------
        self.log_title = QLabel(self.right_widget)
        self.log_title.setObjectName(u"log_title")
        # 标题颜色适配主题
        log_title_color = "#64b5f6" if is_dark_theme else "#1976d2"
        self.log_title.setStyleSheet(f"QLabel {{ font-weight: bold; font-size: 15px; color: {log_title_color}; }}")
        self.right_layout.addWidget(self.log_title)

        # 日志显示区域（占右侧上半部分）
        self.loglabel = QPlainTextEdit(self.right_widget)
        self.loglabel.setObjectName(u"loglabel")
        self.loglabel.setReadOnly(True)
        self.loglabel.setFocusPolicy(Qt.NoFocus)
        
        # 日志区域样式适配主题（保持深色终端风格，但微调）
        if is_dark_theme:
            log_style = "QPlainTextEdit { background-color: #1a1a1a; color: #aed581; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; padding: 10px; border-radius: 5px; border: 1px solid #3a3a3a; }"
        else:
            log_style = "QPlainTextEdit { background-color: #263238; color: #aed581; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; padding: 10px; border-radius: 5px; }"
        
        self.loglabel.setStyleSheet(log_style)
        self.right_layout.addWidget(self.loglabel, 1)  # 权重为 1
        
        # --------- 下半部分：生成的字幕 ---------
        self.result_title = QLabel(self.right_widget)
        self.result_title.setObjectName(u"result_title")
        # 标题颜色适配主题
        result_title_color = "#81c784" if is_dark_theme else "#4caf50"
        self.result_title.setStyleSheet(f"QLabel {{ font-weight: bold; font-size: 15px; color: {result_title_color}; margin-top: 10px; }}")
        self.right_layout.addWidget(self.result_title)

        # 结果预览区域（占右侧下半部分）
        self.resultinput = QPlainTextEdit(self.right_widget)
        self.resultinput.setObjectName(u"resultinput")
        self.resultinput.setReadOnly(True)
        self.resultinput.setFocusPolicy(Qt.NoFocus)
        
        # 结果区域样式适配主题
        if is_dark_theme:
            result_style = "QPlainTextEdit { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; padding: 10px; border: 1px solid #3a3a3a; border-radius: 5px; }"
        else:
            result_style = "QPlainTextEdit { background-color: #f9f9f9; color: #212121; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; padding: 10px; border: 1px solid #e0e0e0; border-radius: 5px; }"
        
        self.resultinput.setStyleSheet(result_style)
        self.right_layout.addWidget(self.resultinput, 1)  # 权重为 1

        # 结果文件路径和打开按钮的布局
        self.result_bottom_layout = QHBoxLayout()
        
        # 结果文件路径
        self.resultlabel = QLabel(self.right_widget)
        self.resultlabel.setObjectName(u"resultlabel")
        self.resultlabel.setWordWrap(True)
        # 适配主题的颜色
        result_label_color = "#81c784" if is_dark_theme else "#4caf50"
        self.resultlabel.setStyleSheet(f"QLabel {{ color: {result_label_color}; font-weight: bold; }}")
        self.result_bottom_layout.addWidget(self.resultlabel, 1)

        # 打开目录按钮
        self.resultbtn = QPushButton(self.right_widget)
        self.resultbtn.setObjectName(u"resultbtn")
        self.resultbtn.setMinimumSize(QSize(150, 40))
        self.resultbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.resultbtn.setDisabled(True)
        self.resultbtn.setStyleSheet("""
            QPushButton { 
                background-color: #4caf50; 
                color: white; 
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
            } 
            QPushButton:hover { 
                background-color: #45a049; 
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.result_bottom_layout.addWidget(self.resultbtn)
        
        self.right_layout.addLayout(self.result_bottom_layout)
        
        # 将右侧 widget 添加到分割器
        self.splitter.addWidget(self.right_widget)
        
        # 设置分割器的初始比例（左:右 = 1:1）
        self.splitter.setSizes([800, 800])
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        # 将分割器添加到主布局
        self.horizontalLayout_main.addWidget(self.splitter)

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
        
        self.videobtn.setText(
            "📁 点击选择视频/音频文件，或直接拖放文件到此处" if config.defaulelang == 'zh' else '📁 Click to Select Video/Audio or Drag & Drop Here')
        
        self.videoinput.setText(
            "未选择文件" if config.defaulelang == 'zh' else 'No file selected')
        
        self.use_existing_srt_checkbox.setText(
            "🔄 使用现有字幕文件（重新智能分割长句）" if config.defaulelang == 'zh' else '🔄 Use Existing Subtitle File (Re-split Long Sentences)')
        
        self.srtbtn.setText(
            "📄 点击选择字幕文件(.srt)，或直接拖放文件到此处" if config.defaulelang == 'zh' else '📄 Click to Select Subtitle (.srt) or Drag & Drop Here')
        
        self.srtinput.setText(
            "未选择字幕文件" if config.defaulelang == 'zh' else 'No subtitle file selected')
        
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
            "🔍\n测试连接" if config.defaulelang == 'zh' else '🔍\nTest\nConnection')
        
        self.language_label.setText("语言:" if config.defaulelang == 'zh' else 'Language:')
        self.model_label.setText("Whisper模型:" if config.defaulelang == 'zh' else 'Whisper Model:')
        self.duration_label.setText("最大持续时间(秒):" if config.defaulelang == 'zh' else 'Max Duration (sec):')
        self.words_label.setText("最大词数:" if config.defaulelang == 'zh' else 'Max Words:')
        self.device_label.setText("🚀 加速设备:" if config.defaulelang == 'zh' else '🚀 Device:')
        
        self.startbtn.setText("🎬\n开始生成\n智能字幕" if config.defaulelang == 'zh' else '🎬\nGenerate\nSubtitles')
        
        self.log_title.setText("📋 处理日志:" if config.defaulelang == 'zh' else '📋 Processing Log:')
        self.result_title.setText("📄 生成的字幕:" if config.defaulelang == 'zh' else '📄 Generated Subtitles:')
        
        self.resultlabel.setText("")
        self.resultinput.setPlainText(
            "生成的字幕将显示在这里..." if config.defaulelang == 'zh' else "Generated subtitles will be displayed here...")
        self.loglabel.setPlainText(
            "处理日志将显示在这里..." if config.defaulelang == 'zh' else "Processing log will be displayed here...")
        self.resultbtn.setText("📁 打开保存目录" if config.defaulelang == 'zh' else '📁 Open Save Directory')
    # retranslateUi

