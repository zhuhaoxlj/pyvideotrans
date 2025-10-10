from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
)

from videotrans.configure import config


class SubtitleSettingsDialog(QDialog):
    def __init__(self, parent=None, cjk_len=40, other_len=80, margin_l=50, margin_r=50):
        super().__init__(parent)
        self.cjk_len = cjk_len
        self.other_len = other_len
        self.margin_l = margin_l
        self.margin_r = margin_r
        self.resize(400, 350)

        # 设置对话框标题
        self.setWindowTitle("设置硬字幕行显示宽度" if config.defaulelang == 'zh' else "Set Subtitle Display Width")
        self.setWindowIcon(QIcon(f"{config.ROOT_DIR}/videotrans/styles/icon.ico"))

        # 创建标签和输入框
        self.cjk_label = QLabel(
            "中日韩硬字幕一行显示宽度:\n(中文1字=2,英文1字=1,建议40)" if config.defaulelang == 'zh' 
            else "CJK Subtitle Width:\n(CJK char=2, Latin=1, suggest 40)"
        )
        self.cjk_input = QLineEdit()
        self.cjk_input.setText(str(self.cjk_len))
        self.cjk_input.setPlaceholderText("40" if config.defaulelang == 'zh' else "40")

        self.other_label = QLabel(
            "其他语言硬字幕一行显示宽度:\n(英文1字=1,中文1字=2,建议80)" if config.defaulelang == 'zh' 
            else "Other Language Width:\n(Latin=1, CJK=2, suggest 80)"
        )
        self.other_input = QLineEdit()
        self.other_input.setText(str(self.other_len))
        self.other_input.setPlaceholderText("80" if config.defaulelang == 'zh' else "80")

        # Margin 左边距
        self.margin_l_label = QLabel(
            "字幕左边距(像素):\n(距离左边缘,建议50)" if config.defaulelang == 'zh' 
            else "Left Margin (pixels):\n(Distance from left, suggest 50)"
        )
        self.margin_l_input = QLineEdit()
        self.margin_l_input.setText(str(self.margin_l))
        self.margin_l_input.setPlaceholderText("50" if config.defaulelang == 'zh' else "50")

        # Margin 右边距
        self.margin_r_label = QLabel(
            "字幕右边距(像素):\n(距离右边缘,建议50)" if config.defaulelang == 'zh' 
            else "Right Margin (pixels):\n(Distance from right, suggest 50)"
        )
        self.margin_r_input = QLineEdit()
        self.margin_r_input.setText(str(self.margin_r))
        self.margin_r_input.setPlaceholderText("50" if config.defaulelang == 'zh' else "50")

        # 创建按钮
        self.ok_button = QPushButton("保存" if config.defaulelang == 'zh' else "Save")
        self.ok_button.clicked.connect(self.accept)  # 点击OK按钮后关闭对话框
        self.ok_button.setFixedHeight(35)

        # 布局
        layout = QVBoxLayout()

        # CJK字符数布局
        cjk_layout = QHBoxLayout()
        cjk_layout.addWidget(self.cjk_label)
        cjk_layout.addWidget(self.cjk_input)
        layout.addLayout(cjk_layout)

        # 其他语言字符数布局
        other_layout = QHBoxLayout()
        other_layout.addWidget(self.other_label)
        other_layout.addWidget(self.other_input)
        layout.addLayout(other_layout)

        # 左边距布局
        margin_l_layout = QHBoxLayout()
        margin_l_layout.addWidget(self.margin_l_label)
        margin_l_layout.addWidget(self.margin_l_input)
        layout.addLayout(margin_l_layout)

        # 右边距布局
        margin_r_layout = QHBoxLayout()
        margin_r_layout.addWidget(self.margin_r_label)
        margin_r_layout.addWidget(self.margin_r_input)
        layout.addLayout(margin_r_layout)

        # OK按钮布局
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_values(self):
        cjk_len = self.cjk_input.text().strip()
        other_len = self.other_input.text().strip()
        margin_l = self.margin_l_input.text().strip()
        margin_r = self.margin_r_input.text().strip()
        
        try:
            cjk_len = int(cjk_len) if cjk_len else 40
            other_len = int(other_len) if other_len else 80
            margin_l = int(margin_l) if margin_l else 50
            margin_r = int(margin_r) if margin_r else 50
        except:
            cjk_len = 40
            other_len = 80
            margin_l = 50
            margin_r = 50
        
        return cjk_len, other_len, margin_l, margin_r
