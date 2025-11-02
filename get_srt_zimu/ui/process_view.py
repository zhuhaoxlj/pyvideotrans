"""
Process View - Shows processing progress and output
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QGroupBox
)
from PySide6.QtCore import Signal, QThread, Qt
from PySide6.QtGui import QFont
from utils.whisper_processor import WhisperProcessor
import subprocess
import platform
from pathlib import Path


class ProcessView(QWidget):
    reset_requested = Signal()
    split_requested = Signal(str)  # 新增：请求跳转到分割页面，传递 SRT 路径
    
    def __init__(self):
        super().__init__()
        self.processor = None
        self.process_thread = None
        self.init_ui()
        
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
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
                font-size: 13px;
                color: #333;
                font-family: 'Monaco', 'Courier New', monospace;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            QGroupBox {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #333;
                font-size: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                background-color: #f5f5f5;
                color: #333;
                font-weight: bold;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 3px;
            }
        """)
        
        # Header with project name and reset button
        header_layout = QHBoxLayout()
        self.project_label = QLabel("项目: ")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.project_label.setFont(font)
        self.project_label.setStyleSheet("color: #2196f3; font-size: 18px;")
        header_layout.addWidget(self.project_label)
        header_layout.addStretch()
        
        self.reset_btn = QPushButton("🔄 重新开始")
        self.reset_btn.setEnabled(False)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        header_layout.addWidget(self.reset_btn)
        layout.addLayout(header_layout)
        
        # Status Label
        self.status_label = QLabel("当前状态: 初始化中...")
        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #4caf50; font-size: 15px; padding: 10px; background-color: #f1f8f4; border-radius: 5px; border: 1px solid #c8e6c9;")
        layout.addWidget(self.status_label)
        
        # Output Text Area
        output_group = QGroupBox("📄 输出日志")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(300)
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Download Buttons Group
        download_group = QGroupBox("💾 下载文件")
        download_layout = QHBoxLayout()
        download_layout.setSpacing(10)
        
        self.download_srt_btn = QPushButton("⬇ 下载 SRT 文件")
        self.download_srt_btn.setEnabled(False)
        self.download_srt_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.download_srt_btn.clicked.connect(self.download_srt)
        download_layout.addWidget(self.download_srt_btn)
        
        self.download_fcpxml_btn = QPushButton("⬇ 下载 FCPXML 文件")
        self.download_fcpxml_btn.setEnabled(False)
        self.download_fcpxml_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.download_fcpxml_btn.clicked.connect(self.download_fcpxml)
        download_layout.addWidget(self.download_fcpxml_btn)
        
        self.download_all_btn = QPushButton("📁 下载全部")
        self.download_all_btn.setEnabled(False)
        self.download_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.download_all_btn.clicked.connect(self.download_all)
        download_layout.addWidget(self.download_all_btn)
        
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)
        
        # 下一步：智能分割按钮
        next_step_layout = QHBoxLayout()
        next_step_layout.addStretch()
        
        self.goto_split_btn = QPushButton("✂️ 继续智能分割字幕")
        self.goto_split_btn.setEnabled(False)
        self.goto_split_btn.setMinimumHeight(45)
        self.goto_split_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-size: 16px;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        self.goto_split_btn.clicked.connect(self.goto_split)
        next_step_layout.addWidget(self.goto_split_btn)
        next_step_layout.addStretch()
        layout.addLayout(next_step_layout)
        
        # Open in FCPX (macOS only)
        if platform.system() == "Darwin":
            fcpx_layout = QHBoxLayout()
            fcpx_label = QLabel("🎬 打开 Final Cut Pro:")
            fcpx_label.setStyleSheet("font-weight: bold; color: #333; font-size: 14px;")
            fcpx_layout.addWidget(fcpx_label)
            
            self.open_fcpx_btn = QPushButton("在 Final Cut Pro X 中打开")
            self.open_fcpx_btn.setEnabled(False)
            self.open_fcpx_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9c27b0;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background-color: #7b1fa2;
                }
            """)
            self.open_fcpx_btn.clicked.connect(self.open_in_fcpx)
            fcpx_layout.addWidget(self.open_fcpx_btn)
            fcpx_layout.addStretch()
            layout.addLayout(fcpx_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(35)
        layout.addWidget(self.progress_bar)
        
        # Progress Info Label
        self.progress_info_label = QLabel("批次 (··· / ···): 0% 已完成 - 剩余时间 00:00")
        self.progress_info_label.setAlignment(Qt.AlignCenter)
        self.progress_info_label.setStyleSheet("color: #666; font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.progress_info_label)
        
        self.setLayout(layout)
        
        # Store file paths
        self.srt_path = None
        self.fcpxml_path = None
        
    def start_processing(self, data):
        """Start the whisper processing with given data"""
        print("=" * 60)
        print("🚀 start_processing() 被调用")
        print("=" * 60)
        print(f"data = {data}")
        
        self.project_label.setText(f"项目: {data['project_name']}")
        self.output_text.clear()
        self.output_text.append("🔍 初始化处理流程...\n")
        
        self.progress_bar.setValue(0)
        self.status_label.setText("当前状态: 正在处理音频文件...")
        
        print("1. 禁用按钮...")
        # Disable buttons
        self.reset_btn.setEnabled(False)
        self.download_srt_btn.setEnabled(False)
        self.download_fcpxml_btn.setEnabled(False)
        self.download_all_btn.setEnabled(False)
        self.goto_split_btn.setEnabled(False)
        if platform.system() == "Darwin":
            self.open_fcpx_btn.setEnabled(False)
        
        print("2. 创建线程...")
        # Create processor and thread
        self.process_thread = QThread()
        print("   ✓ QThread 创建成功")
        
        print("3. 创建 WhisperProcessor...")
        try:
            self.processor = WhisperProcessor(data)
            print("   ✓ WhisperProcessor 创建成功")
        except Exception as e:
            import traceback
            error_msg = f"❌ 创建 WhisperProcessor 失败: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            self.output_text.append(error_msg)
            return
        
        print("4. 移动到线程...")
        try:
            self.processor.moveToThread(self.process_thread)
            print("   ✓ moveToThread 成功")
        except Exception as e:
            import traceback
            error_msg = f"❌ moveToThread 失败: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            self.output_text.append(error_msg)
            return
        
        print("5. 连接信号...")
        # Connect signals
        self.process_thread.started.connect(self.processor.process)
        self.processor.progress.connect(self.on_progress_update)
        self.processor.status.connect(self.on_status_update)
        self.processor.output.connect(self.on_output_update)
        self.processor.batch_info.connect(self.on_batch_info_update)
        self.processor.finished.connect(self.on_processing_finished)
        self.processor.error.connect(self.on_processing_error)
        self.processor.finished.connect(self.process_thread.quit)
        self.processor.error.connect(self.process_thread.quit)
        print("   ✓ 信号连接成功")
        
        print("6. 启动线程...")
        # Start processing
        try:
            self.process_thread.start()
            print("   ✓ 线程启动成功")
            print("=" * 60)
        except Exception as e:
            import traceback
            error_msg = f"❌ 线程启动失败: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            self.output_text.append(error_msg)
            return
        
    def on_progress_update(self, progress):
        """Update progress bar"""
        self.progress_bar.setValue(int(progress * 100))
        
    def on_status_update(self, status):
        """Update status label"""
        self.status_label.setText(f"当前状态: {status}")
        
    def on_output_update(self, output):
        """Append output to text area"""
        self.output_text.append(output)
        
    def on_batch_info_update(self, current, total, percentage, remaining):
        """Update batch information"""
        self.progress_info_label.setText(
            f"批次 ({current} / {total}): {percentage}% 已完成 - 剩余时间 {remaining}"
        )
        
    def on_processing_finished(self, srt_path, fcpxml_path):
        """Processing completed successfully"""
        self.srt_path = srt_path
        self.fcpxml_path = fcpxml_path
        
        self.status_label.setText("当前状态: 完成 ✓")
        self.status_label.setStyleSheet("color: #4caf50; font-size: 15px; padding: 10px; background-color: #e8f5e9; border-radius: 5px; border: 2px solid #4caf50; font-weight: bold;")
        self.progress_bar.setValue(100)
        self.output_text.append("\n✓ 处理完成！")
        self.output_text.append("\n⏳ 5秒后自动跳转到智能分割页面...")
        
        # 重置处理标志
        parent_window = self.window()
        if hasattr(parent_window, 'home_view'):
            parent_window.home_view._processing = False
        
        # Enable buttons
        self.reset_btn.setEnabled(True)
        self.download_srt_btn.setEnabled(True)
        self.download_fcpxml_btn.setEnabled(True)
        self.download_all_btn.setEnabled(True)
        self.goto_split_btn.setEnabled(True)
        if platform.system() == "Darwin":
            self.open_fcpx_btn.setEnabled(True)
        
        # 5秒后自动跳转到智能分割
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self._auto_goto_split())
        
    def on_processing_error(self, error_msg):
        """Processing failed"""
        self.status_label.setText("当前状态: 错误 ✗")
        self.status_label.setStyleSheet("color: #f44336; font-size: 15px; padding: 10px; background-color: #ffebee; border-radius: 5px; border: 2px solid #f44336; font-weight: bold;")
        self.output_text.append(f"\n✗ 错误: {error_msg}")
        
        # 重置处理标志
        parent_window = self.window()
        if hasattr(parent_window, 'home_view'):
            parent_window.home_view._processing = False
        
        self.reset_btn.setEnabled(True)
        
    def download_srt(self):
        """Open the folder containing the SRT file"""
        if self.srt_path:
            self._open_file_location(self.srt_path)
            
    def download_fcpxml(self):
        """Open the folder containing the FCPXML file"""
        if self.fcpxml_path:
            self._open_file_location(self.fcpxml_path)
            
    def download_all(self):
        """Open the folder containing both files"""
        if self.srt_path:
            self._open_file_location(self.srt_path)
            
    def _open_file_location(self, file_path):
        """Open the file location in the system file browser"""
        file_path = Path(file_path)
        folder_path = file_path.parent
        
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", "-R", str(file_path)])
        elif system == "Windows":
            subprocess.run(["explorer", "/select,", str(file_path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(folder_path)])
            
    def open_in_fcpx(self):
        """Open the FCPXML file in Final Cut Pro X (macOS only)"""
        if self.fcpxml_path and platform.system() == "Darwin":
            applescript = f'''
            tell application "Final Cut Pro"
                launch
                activate
                open POSIX file "{self.fcpxml_path}"
            end tell
            '''
            subprocess.run(["osascript", "-e", applescript])
            
    def goto_split(self):
        """跳转到智能分割页面（手动点击）"""
        if self.srt_path:
            self.split_requested.emit(self.srt_path)
    
    def _auto_goto_split(self):
        """自动跳转到智能分割页面，并传递所有数据"""
        if self.srt_path and hasattr(self, 'processor') and self.processor:
            # 获取原始视频文件路径
            video_file = self.processor.data.get('file_path', '')
            
            # 构建完整的数据包
            from PySide6.QtCore import QTimer
            
            # 通过父窗口跳转，并传递完整数据
            parent_window = self.window()
            if hasattr(parent_window, 'show_split_with_full_data'):
                parent_window.show_split_with_full_data(
                    video_file=video_file,
                    srt_file=self.srt_path
                )
            else:
                # 回退方案：只传递字幕文件
                self.split_requested.emit(self.srt_path)
    
    def on_reset_clicked(self):
        """Reset and go back to home view"""
        self.output_text.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("当前状态: 初始化中...")
        self.status_label.setStyleSheet("color: #4caf50; font-size: 15px; padding: 10px; background-color: #f1f8f4; border-radius: 5px; border: 1px solid #c8e6c9;")
        self.progress_info_label.setText("批次 (··· / ···): 0% 已完成 - 剩余时间 00:00")
        self.srt_path = None
        self.fcpxml_path = None
        
        # 获取父窗口的 home_view 并重置处理标志
        parent_window = self.window()
        if hasattr(parent_window, 'home_view'):
            parent_window.home_view._processing = False
        
        self.reset_requested.emit()

