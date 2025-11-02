"""
Render View - 视频渲染字幕功能
将字幕文件渲染（烧录）到视频中，支持音频合并
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QComboBox, QCheckBox,
    QTextEdit, QScrollArea, QGroupBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QThread, QUrl
from PySide6.QtGui import QDesktopServices
from pathlib import Path
import subprocess
import json
import time
import os


class RenderThread(QThread):
    """渲染线程"""
    progress = Signal(str)  # 进度信息
    status = Signal(str)    # 状态信息
    finished = Signal(str)  # 完成，返回输出文件路径
    error = Signal(str)     # 错误信息
    
    def __init__(self, video_path, audio_path, srt_path, output_path, 
                 font_size, position, use_outline, merge_audio, soft_subtitle):
        super().__init__()
        self.video_path = video_path
        self.audio_path = audio_path
        self.srt_path = srt_path
        self.output_path = output_path
        self.font_size = font_size
        self.position = position
        self.use_outline = use_outline
        self.merge_audio = merge_audio
        self.soft_subtitle = soft_subtitle
        
    def run(self):
        try:
            # 检查 ffmpeg 是否可用
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except FileNotFoundError:
                self.error.emit("未找到 ffmpeg，请确保已安装 ffmpeg 并添加到系统 PATH")
                return
            except subprocess.CalledProcessError:
                self.error.emit("ffmpeg 运行错误")
                return
            
            # 如果有音频需要先合并
            temp_video = self.video_path
            if self.audio_path and self.merge_audio:
                self.status.emit("正在合并音频...")
                temp_video = str(Path(self.output_path).parent / f"temp_{int(time.time())}.mp4")
                
                cmd = [
                    'ffmpeg', '-y',
                    '-i', self.video_path,
                    '-i', self.audio_path,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-map', '0:v:0',
                    '-map', '1:a:0',
                    '-shortest',
                    temp_video
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.error.emit(f"音频合并失败: {result.stderr}")
                    return
            
            # 渲染字幕
            if self.srt_path:
                self.status.emit("正在渲染字幕...")
                
                if self.soft_subtitle:
                    # 软字幕
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', temp_video,
                        '-i', self.srt_path,
                        '-c:v', 'copy',
                        '-c:a', 'copy',
                        '-c:s', 'mov_text',
                        '-metadata:s:s:0', 'language=chi',
                        self.output_path
                    ]
                else:
                    # 硬字幕（烧录）
                    # 字体大小映射
                    font_sizes = {"小": "18", "中": "24", "大": "32", "特大": "48"}
                    size = font_sizes.get(self.font_size, "24")
                    
                    # 位置映射
                    positions = {
                        "底部": "2",  # alignment=2: bottom center
                        "顶部": "8",  # alignment=8: top center
                        "中间": "5"   # alignment=5: middle center
                    }
                    alignment = positions.get(self.position, "2")
                    
                    # 构建字幕滤镜
                    # 转义 Windows 路径
                    srt_escaped = self.srt_path.replace('\\', '/').replace(':', '\\:')
                    
                    # 基本样式
                    subtitle_filter = f"subtitles={srt_escaped}:force_style='FontSize={size},Alignment={alignment}"
                    
                    # 添加描边
                    if self.use_outline:
                        subtitle_filter += ",BorderStyle=1,Outline=2,Shadow=1"
                    
                    subtitle_filter += "'"
                    
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', temp_video,
                        '-vf', subtitle_filter,
                        '-c:v', 'libx264',
                        '-c:a', 'copy',
                        '-crf', '23',
                        '-preset', 'medium',
                        self.output_path
                    ]
                
                # 执行渲染
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # 读取进度
                while True:
                    line = process.stderr.readline()
                    if not line:
                        break
                    # ffmpeg 输出进度信息
                    if "time=" in line:
                        self.progress.emit(line.strip())
                
                process.wait()
                
                if process.returncode != 0:
                    _, stderr = process.communicate()
                    self.error.emit(f"字幕渲染失败: {stderr}")
                    return
            else:
                # 只合并音频，不渲染字幕
                if temp_video != self.video_path:
                    # 已经在音频合并步骤完成了
                    import shutil
                    shutil.move(temp_video, self.output_path)
            
            # 清理临时文件
            if temp_video != self.video_path and Path(temp_video).exists():
                try:
                    os.remove(temp_video)
                except:
                    pass
            
            self.status.emit("渲染完成 ✓")
            self.finished.emit(self.output_path)
            
        except Exception as e:
            self.error.emit(f"渲染过程出错: {str(e)}")


class RenderView(QWidget):
    back_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.video_file = None
        self.audio_file = None
        self.srt_file = None
        self.output_file = None
        self.render_thread = None
        
        # 处理状态标志
        self._processing = False
        
        self.init_ui()
    
    def init_ui(self):
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        
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
            QComboBox, QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
                color: #333;
                min-height: 35px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 2px solid #ff9800;
            }
            QCheckBox {
                color: #333;
                font-size: 14px;
                spacing: 8px;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #f9f9f9;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                color: #333;
            }
        """)
        
        # 标题
        title = QLabel("🎬 视频渲染字幕")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #ff9800; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("将字幕烧录到视频中，支持音频合并")
        desc.setStyleSheet("font-size: 15px; color: #666; padding: 10px; margin-bottom: 10px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # === 文件选择区域 ===
        file_group = QGroupBox("📁 文件选择")
        file_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        file_layout = QGridLayout()
        file_layout.setSpacing(15)
        file_layout.setColumnStretch(1, 1)
        
        # 视频文件（必选）
        label = QLabel("* 视频文件:")
        label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        file_layout.addWidget(label, 0, 0)
        
        self.video_label = QLabel("未选择")
        self.video_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #666; border: 2px solid #e0e0e0;")
        file_layout.addWidget(self.video_label, 0, 1)
        
        video_btn = QPushButton("📂 选择视频")
        video_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                padding: 12px 20px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        video_btn.clicked.connect(self.choose_video)
        file_layout.addWidget(video_btn, 0, 2)
        
        # 音频文件（可选）
        label = QLabel("音频文件:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        file_layout.addWidget(label, 1, 0)
        
        self.audio_label = QLabel("未选择（可选）")
        self.audio_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #999; border: 2px solid #e0e0e0;")
        file_layout.addWidget(self.audio_label, 1, 1)
        
        audio_btn = QPushButton("🎵 选择音频")
        audio_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 12px 20px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        audio_btn.clicked.connect(self.choose_audio)
        file_layout.addWidget(audio_btn, 1, 2)
        
        # 字幕文件（可选）
        label = QLabel("字幕文件:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        file_layout.addWidget(label, 2, 0)
        
        self.srt_label = QLabel("未选择（可选）")
        self.srt_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #999; border: 2px solid #e0e0e0;")
        file_layout.addWidget(self.srt_label, 2, 1)
        
        srt_btn = QPushButton("📝 选择字幕")
        srt_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 12px 20px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        srt_btn.clicked.connect(self.choose_srt)
        file_layout.addWidget(srt_btn, 2, 2)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # === 字幕样式设置 ===
        style_group = QGroupBox("🎨 字幕样式")
        style_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        style_layout = QGridLayout()
        style_layout.setSpacing(15)
        style_layout.setColumnStretch(1, 1)
        
        # 字幕类型
        label = QLabel("字幕类型:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        style_layout.addWidget(label, 0, 0)
        self.subtitle_type_combo = QComboBox()
        self.subtitle_type_combo.addItems(["硬字幕（烧录）", "软字幕（内嵌）"])
        self.subtitle_type_combo.setCurrentText("硬字幕（烧录）")
        self.subtitle_type_combo.currentTextChanged.connect(self._on_subtitle_type_changed)
        style_layout.addWidget(self.subtitle_type_combo, 0, 1)
        
        # 字体大小
        label = QLabel("字体大小:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        style_layout.addWidget(label, 1, 0)
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["小", "中", "大", "特大"])
        self.font_size_combo.setCurrentText("中")
        style_layout.addWidget(self.font_size_combo, 1, 1)
        
        # 字幕位置
        label = QLabel("字幕位置:")
        label.setStyleSheet("font-weight: bold; color: #333;")
        style_layout.addWidget(label, 2, 0)
        self.position_combo = QComboBox()
        self.position_combo.addItems(["底部", "顶部", "中间"])
        self.position_combo.setCurrentText("底部")
        style_layout.addWidget(self.position_combo, 2, 1)
        
        # 选项
        self.outline_check = QCheckBox("✨ 添加字幕描边（提高可读性）")
        self.outline_check.setChecked(True)
        self.outline_check.setStyleSheet("margin-left: 10px; padding: 5px;")
        style_layout.addWidget(self.outline_check, 3, 0, 1, 2)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # === 输出设置 ===
        output_group = QGroupBox("💾 输出设置")
        output_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)
        
        # 音频合并选项
        self.merge_audio_check = QCheckBox("🔊 合并音频到视频（如果选择了音频文件）")
        self.merge_audio_check.setChecked(True)
        self.merge_audio_check.setStyleSheet("margin-left: 10px; padding: 5px;")
        output_layout.addWidget(self.merge_audio_check)
        
        # 输出文件名
        name_layout = QHBoxLayout()
        name_label = QLabel("输出文件名:")
        name_label.setStyleSheet("font-weight: bold; color: #333;")
        name_layout.addWidget(name_label)
        
        self.output_name_input = QLineEdit()
        self.output_name_input.setPlaceholderText("留空则自动生成（原文件名_rendered.mp4）")
        name_layout.addWidget(self.output_name_input)
        
        output_layout.addLayout(name_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # === 进度输出区域 ===
        progress_group = QGroupBox("📊 处理日志")
        progress_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        progress_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("处理日志将显示在这里...")
        self.log_text.setMinimumHeight(150)
        progress_layout.addWidget(self.log_text)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.render_btn = QPushButton("🚀 开始渲染")
        self.render_btn.setEnabled(False)
        self.render_btn.clicked.connect(self.start_render)
        self.render_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        btn_layout.addWidget(self.render_btn)
        
        self.open_btn = QPushButton("📂 打开输出文件夹")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_output_folder)
        self.open_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        btn_layout.addWidget(self.open_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _on_subtitle_type_changed(self, text):
        """字幕类型改变时的处理"""
        is_hard = text == "硬字幕（烧录）"
        self.font_size_combo.setEnabled(is_hard)
        self.position_combo.setEnabled(is_hard)
        self.outline_check.setEnabled(is_hard)
    
    def choose_video(self):
        """选择视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.mov *.avi *.mkv *.flv *.wmv *.webm);;所有文件 (*.*)"
        )
        
        if file_path:
            self.video_file = file_path
            file_name = Path(file_path).name
            self.video_label.setText(f"✓ {file_name}")
            self.video_label.setStyleSheet("padding: 12px; background: #e8f5e9; border-radius: 5px; color: #2e7d32; border: 2px solid #4caf50; font-weight: bold;")
            self._check_ready()
    
    def choose_audio(self):
        """选择音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频文件",
            "",
            "音频文件 (*.mp3 *.wav *.m4a *.aac *.flac *.ogg);;所有文件 (*.*)"
        )
        
        if file_path:
            self.audio_file = file_path
            file_name = Path(file_path).name
            self.audio_label.setText(f"✓ {file_name}")
            self.audio_label.setStyleSheet("padding: 12px; background: #e8f5e9; border-radius: 5px; color: #2e7d32; border: 2px solid #4caf50; font-weight: bold;")
            self._check_ready()
    
    def choose_srt(self):
        """选择字幕文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择字幕文件",
            "",
            "字幕文件 (*.srt *.ass);;所有文件 (*.*)"
        )
        
        if file_path:
            self.srt_file = file_path
            file_name = Path(file_path).name
            self.srt_label.setText(f"✓ {file_name}")
            self.srt_label.setStyleSheet("padding: 12px; background: #e8f5e9; border-radius: 5px; color: #2e7d32; border: 2px solid #4caf50; font-weight: bold;")
            self._check_ready()
    
    def _check_ready(self):
        """检查是否可以开始渲染"""
        # 必须有视频文件，并且至少有音频或字幕之一
        if self.video_file and (self.audio_file or self.srt_file):
            self.render_btn.setEnabled(True)
        else:
            self.render_btn.setEnabled(False)
    
    def start_render(self):
        """开始渲染"""
        if not self.video_file:
            QMessageBox.warning(self, "警告", "请先选择视频文件")
            return
        
        if not self.audio_file and not self.srt_file:
            QMessageBox.warning(self, "警告", "请至少选择音频或字幕文件")
            return
        
        # 标记为正在处理
        self._processing = True
        
        # 生成输出文件路径
        video_path = Path(self.video_file)
        output_name = self.output_name_input.text().strip()
        
        if not output_name:
            output_name = f"{video_path.stem}_rendered{video_path.suffix}"
        elif not output_name.endswith('.mp4'):
            output_name += '.mp4'
        
        output_path = str(video_path.parent / output_name)
        
        # 禁用按钮
        self.render_btn.setEnabled(False)
        self.render_btn.setText("⏳ 渲染中...")
        self.open_btn.setEnabled(False)
        
        # 清空日志
        self.log_text.clear()
        self.log_text.append("🚀 开始渲染...\n")
        self.log_text.append(f"📹 视频: {Path(self.video_file).name}")
        if self.audio_file:
            self.log_text.append(f"🎵 音频: {Path(self.audio_file).name}")
        if self.srt_file:
            self.log_text.append(f"📝 字幕: {Path(self.srt_file).name}")
        self.log_text.append(f"💾 输出: {output_name}\n")
        
        # 创建渲染线程
        self.render_thread = RenderThread(
            video_path=self.video_file,
            audio_path=self.audio_file,
            srt_path=self.srt_file,
            output_path=output_path,
            font_size=self.font_size_combo.currentText(),
            position=self.position_combo.currentText(),
            use_outline=self.outline_check.isChecked(),
            merge_audio=self.merge_audio_check.isChecked(),
            soft_subtitle=self.subtitle_type_combo.currentText() == "软字幕（内嵌）"
        )
        
        # 连接信号
        self.render_thread.progress.connect(self.on_progress)
        self.render_thread.status.connect(self.on_status)
        self.render_thread.finished.connect(self.on_finished)
        self.render_thread.error.connect(self.on_error)
        
        # 启动线程
        self.render_thread.start()
    
    def on_progress(self, text):
        """更新进度"""
        # ffmpeg 的进度输出
        if "time=" in text:
            self.log_text.append(f"⏱️  {text}")
            # 自动滚动到底部
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )
    
    def on_status(self, text):
        """更新状态"""
        self.log_text.append(f"📌 {text}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_finished(self, output_path):
        """渲染完成"""
        self.output_file = output_path
        
        # 重置处理标志
        self._processing = False
        
        self.log_text.append("\n" + "="*50)
        self.log_text.append("✅ 渲染完成！")
        self.log_text.append("="*50)
        self.log_text.append(f"📁 输出文件: {Path(output_path).name}")
        
        self.render_btn.setEnabled(True)
        self.render_btn.setText("🚀 开始渲染")
        self.open_btn.setEnabled(True)
        
        QMessageBox.information(
            self,
            "完成",
            f"渲染完成！\n\n输出文件:\n{output_path}"
        )
    
    def on_error(self, error_msg):
        """渲染出错"""
        # 重置处理标志
        self._processing = False
        
        self.log_text.append("\n" + "="*50)
        self.log_text.append(f"❌ 错误: {error_msg}")
        self.log_text.append("="*50)
        
        self.render_btn.setEnabled(True)
        self.render_btn.setText("🚀 开始渲染")
        
        QMessageBox.critical(self, "错误", f"渲染失败:\n\n{error_msg}")
    
    def open_output_folder(self):
        """打开输出文件夹"""
        if self.output_file and Path(self.output_file).exists():
            folder = Path(self.output_file).parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
    
    def reset(self):
        """重置界面"""
        # 只有在非处理状态时才重置
        if not self._processing:
            self.video_file = None
            self.audio_file = None
            self.srt_file = None
            self.output_file = None
            
            self.video_label.setText("未选择")
            self.video_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #666; border: 2px solid #e0e0e0;")
            
            self.audio_label.setText("未选择（可选）")
            self.audio_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #999; border: 2px solid #e0e0e0;")
            
            self.srt_label.setText("未选择（可选）")
            self.srt_label.setStyleSheet("padding: 12px; background: #f5f5f5; border-radius: 5px; color: #999; border: 2px solid #e0e0e0;")
            
            self.log_text.clear()
            self.output_name_input.clear()
            
            self.render_btn.setEnabled(False)
            self.render_btn.setText("🚀 开始渲染")
            self.open_btn.setEnabled(False)
