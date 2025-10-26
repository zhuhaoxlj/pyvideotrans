# 字幕断句/分割工具 UI

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import (QMetaObject, QSize, Qt)
from PySide6.QtGui import (QCursor)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPlainTextEdit, QPushButton,
                               QVBoxLayout)

from videotrans.configure import config


class Ui_splitsrt(object):
    def setupUi(self, splitsrt):
        self.has_done = False
        if not splitsrt.objectName():
            splitsrt.setObjectName(u"splitsrt")
        splitsrt.resize(700, 600)
        splitsrt.setWindowModality(QtCore.Qt.NonModal)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(splitsrt.sizePolicy().hasHeightForWidth())
        splitsrt.setSizePolicy(sizePolicy)

        self.horizontalLayout_main = QHBoxLayout(splitsrt)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        
        # 添加说明标签
        self.info_label = QLabel(splitsrt)
        self.info_label.setObjectName(u"info_label")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { background-color: #f0f8ff; padding: 10px; border-radius: 5px; }")
        self.verticalLayout.addWidget(self.info_label)
        
        # 文件选择区域
        self.horizontalLayout_file = QHBoxLayout()
        self.horizontalLayout_file.setObjectName(u"horizontalLayout_file")

        self.srtinput = QLineEdit(splitsrt)
        self.srtinput.setObjectName(u"srtinput")
        self.srtinput.setMinimumSize(QSize(0, 35))
        self.srtinput.setReadOnly(True)
        self.horizontalLayout_file.addWidget(self.srtinput)

        self.srtbtn = QPushButton(splitsrt)
        self.srtbtn.setObjectName(u"srtbtn")
        self.srtbtn.setMinimumSize(QSize(180, 35))
        self.srtbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.horizontalLayout_file.addWidget(self.srtbtn)

        self.verticalLayout.addLayout(self.horizontalLayout_file)
        
        # 参数设置区域
        self.horizontalLayout_params = QHBoxLayout()
        self.horizontalLayout_params.setObjectName(u"horizontalLayout_params")
        
        self.duration_label = QLabel(splitsrt)
        self.duration_label.setObjectName(u"duration_label")
        self.horizontalLayout_params.addWidget(self.duration_label)
        
        self.duration_input = QLineEdit(splitsrt)
        self.duration_input.setObjectName(u"duration_input")
        self.duration_input.setMinimumSize(QSize(0, 35))
        self.duration_input.setMaximumSize(QSize(100, 35))
        self.duration_input.setText("5")
        self.horizontalLayout_params.addWidget(self.duration_input)
        
        self.duration_unit = QLabel(splitsrt)
        self.duration_unit.setObjectName(u"duration_unit")
        self.horizontalLayout_params.addWidget(self.duration_unit)
        
        self.horizontalLayout_params.addStretch()
        self.verticalLayout.addLayout(self.horizontalLayout_params)

        # 开始按钮
        self.startbtn = QPushButton(splitsrt)
        self.startbtn.setObjectName(u"startbtn")
        self.startbtn.setMinimumSize(QSize(0, 40))
        self.startbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.startbtn.setStyleSheet("QPushButton { font-size: 14px; font-weight: bold; }")
        self.verticalLayout.addWidget(self.startbtn)
        
        # 日志区域标签
        self.log_title = QLabel(splitsrt)
        self.log_title.setObjectName(u"log_title")
        self.log_title.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; }")
        self.verticalLayout.addWidget(self.log_title)

        # 日志显示区域
        self.loglabel = QPlainTextEdit(splitsrt)
        self.loglabel.setObjectName(u"loglabel")
        self.loglabel.setReadOnly(True)
        self.loglabel.setMaximumHeight(150)
        self.verticalLayout.addWidget(self.loglabel)
        
        # 结果预览标签
        self.result_title = QLabel(splitsrt)
        self.result_title.setObjectName(u"result_title")
        self.result_title.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; }")
        self.verticalLayout.addWidget(self.result_title)

        # 结果预览区域
        self.resultinput = QPlainTextEdit(splitsrt)
        self.resultinput.setObjectName(u"resultinput")
        self.resultinput.setReadOnly(True)
        self.verticalLayout.addWidget(self.resultinput)

        # 结果文件路径
        self.resultlabel = QLabel(splitsrt)
        self.resultlabel.setObjectName(u"resultlabel")
        self.resultlabel.setWordWrap(True)
        self.resultlabel.setStyleSheet("QLabel { color: green; font-weight: bold; }")
        self.verticalLayout.addWidget(self.resultlabel)

        # 打开目录按钮
        self.resultbtn = QPushButton(splitsrt)
        self.resultbtn.setObjectName(u"resultbtn")
        self.resultbtn.setMinimumSize(QSize(0, 35))
        self.resultbtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.resultbtn.setDisabled(True)
        self.verticalLayout.addWidget(self.resultbtn)

        self.horizontalLayout_main.addLayout(self.verticalLayout)

        self.retranslateUi(splitsrt)

        QMetaObject.connectSlotsByName(splitsrt)

    # setupUi

    def retranslateUi(self, splitsrt):
        splitsrt.setWindowTitle("字幕智能断句/分割工具" if config.defaulelang == 'zh' else 'Smart Subtitle Splitter')
        
        info_text = """
        <b>功能说明：</b><br>
        • 自动将长时间跨度的字幕分割成短句，让每次只显示一句话<br>
        • 支持中英文句子识别，按标点符号智能分割<br>
        • 自动平均分配时间，保持时间轴连续性
        """ if config.defaulelang == 'zh' else """
        <b>Features:</b><br>
        • Automatically split long subtitles into short sentences<br>
        • Support Chinese and English sentence recognition<br>
        • Automatically distribute time and maintain timeline continuity
        """
        
        self.info_label.setText(info_text)
        
        self.srtinput.setPlaceholderText(
            "请选择需要分割的字幕文件(.srt)" if config.defaulelang == 'zh' else 'Select subtitle file to split (.srt)')
        self.srtinput.setToolTip(
            "选择字幕文件" if config.defaulelang == 'zh' else 'Select subtitle file')
        
        self.srtbtn.setText("选择字幕文件" if config.defaulelang == 'zh' else 'Select Subtitle File')
        
        self.duration_label.setText("单条字幕最大持续时间:" if config.defaulelang == 'zh' else 'Max duration per subtitle:')
        self.duration_unit.setText("秒 (推荐: 3-5秒)" if config.defaulelang == 'zh' else 'seconds (Recommend: 3-5s)')
        
        self.startbtn.setText("🚀 开始分割" if config.defaulelang == 'zh' else '🚀 Start Split')
        
        self.log_title.setText("📋 处理日志:" if config.defaulelang == 'zh' else '📋 Processing Log:')
        self.result_title.setText("📄 结果预览:" if config.defaulelang == 'zh' else '📄 Result Preview:')
        
        self.resultlabel.setText("")
        self.resultinput.setPlaceholderText(
            "分割后的字幕内容将显示在这里..." if config.defaulelang == 'zh' else "Split subtitle content will be displayed here...")
        self.loglabel.setPlaceholderText(
            "处理日志将显示在这里..." if config.defaulelang == 'zh' else "Processing log will be displayed here...")
        self.resultbtn.setText("📁 打开保存目录" if config.defaulelang == 'zh' else '📁 Open Save Directory')
    # retranslateUi

