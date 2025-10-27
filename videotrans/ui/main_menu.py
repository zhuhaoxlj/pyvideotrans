# 主菜单窗口 UI

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (QVBoxLayout, QPushButton, QLabel, QWidget)

from videotrans.configure import config


class Ui_MainMenu(object):
    def setupUi(self, MainMenu):
        MainMenu.setObjectName("MainMenu")
        
        # 获取屏幕尺寸并设置窗口大小
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_height = screen_geometry.height()
            window_height = int(screen_height * 0.7)
            window_width = 800
            MainMenu.resize(window_width, window_height)
        else:
            MainMenu.resize(800, 600)
        
        MainMenu.setWindowModality(QtCore.Qt.NonModal)
        
        # 设置窗口最小尺寸
        MainMenu.setMinimumSize(QSize(700, 500))
        
        # 主布局
        self.centralwidget = QWidget(MainMenu)
        self.centralwidget.setObjectName("centralwidget")
        MainMenu.setCentralWidget(self.centralwidget)
        
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(50, 50, 50, 50)
        self.verticalLayout.setSpacing(30)
        
        # 标题
        self.title_label = QLabel(self.centralwidget)
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("QLabel { color: #2196f3; margin-bottom: 20px; }")
        self.verticalLayout.addWidget(self.title_label)
        
        # 添加一些弹性空间
        self.verticalLayout.addStretch(1)
        
        # 按钮1: AI智能分割字幕
        self.btn_llm_split = QPushButton(self.centralwidget)
        self.btn_llm_split.setObjectName("btn_llm_split")
        self.btn_llm_split.setMinimumHeight(100)
        self.btn_llm_split.setCursor(QCursor(Qt.PointingHandCursor))
        button_font = QFont()
        button_font.setPointSize(18)
        button_font.setBold(True)
        self.btn_llm_split.setFont(button_font)
        self.btn_llm_split.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.verticalLayout.addWidget(self.btn_llm_split)
        
        # 按钮2: AI字幕翻译
        self.btn_ai_translate = QPushButton(self.centralwidget)
        self.btn_ai_translate.setObjectName("btn_ai_translate")
        self.btn_ai_translate.setMinimumHeight(100)
        self.btn_ai_translate.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_ai_translate.setFont(button_font)
        self.btn_ai_translate.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.verticalLayout.addWidget(self.btn_ai_translate)
        
        # 按钮3: 视频渲染字幕
        self.btn_render_subtitle = QPushButton(self.centralwidget)
        self.btn_render_subtitle.setObjectName("btn_render_subtitle")
        self.btn_render_subtitle.setMinimumHeight(100)
        self.btn_render_subtitle.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_render_subtitle.setFont(button_font)
        self.btn_render_subtitle.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
        """)
        self.verticalLayout.addWidget(self.btn_render_subtitle)
        
        # 添加弹性空间
        self.verticalLayout.addStretch(1)
        
        # 底部版本信息
        self.version_label = QLabel(self.centralwidget)
        self.version_label.setObjectName("version_label")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("QLabel { color: #888; font-size: 12px; }")
        self.verticalLayout.addWidget(self.version_label)
        
        self.retranslateUi(MainMenu)
        QtCore.QMetaObject.connectSlotsByName(MainMenu)
    
    def retranslateUi(self, MainMenu):
        MainMenu.setWindowTitle("🎬 PyVideoTrans 工具集" if config.defaulelang == 'zh' else '🎬 PyVideoTrans Tools')
        
        if config.defaulelang == 'zh':
            self.title_label.setText("🎬 PyVideoTrans 工具集")
            self.btn_llm_split.setText("🤖 AI智能分割字幕\n基于大语言模型的智能字幕断句")
            self.btn_ai_translate.setText("🌍 AI字幕翻译\n智能翻译字幕文件")
            self.btn_render_subtitle.setText("🎥 视频渲染字幕\n将字幕渲染到视频中")
            self.version_label.setText("版本 1.0.0 | 选择一个功能开始")
        else:
            self.title_label.setText("🎬 PyVideoTrans Tools")
            self.btn_llm_split.setText("🤖 AI Smart Subtitle Split\nIntelligent subtitle segmentation based on LLM")
            self.btn_ai_translate.setText("🌍 AI Subtitle Translation\nIntelligent subtitle translation")
            self.btn_render_subtitle.setText("🎥 Render Subtitles to Video\nBurn subtitles into video")
            self.version_label.setText("Version 1.0.0 | Choose a feature to start")

