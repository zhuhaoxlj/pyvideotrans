"""
Main Window - Container for all views with navigation
"""

from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
    QPushButton, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt
from ui.home_view import HomeView
from ui.process_view import ProcessView
from ui.split_view import SplitView
from ui.render_view import RenderView


class SidebarButton(QPushButton):
    """侧边栏按钮"""
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.setText(f"{icon} {text}")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(50)
        self.update_style(False)
    
    def update_style(self, is_active):
        """更新按钮样式"""
        if is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 20px;
                    text-align: left;
                    font-size: 15px;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 20px;
                    text-align: left;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)


class Sidebar(QWidget):
    """左侧导航栏"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🎬 Whisper\nAuto Captions")
        title.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #ffffff;
            margin-bottom: 10px;
            background-color: transparent;
            border: none;
        """)
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)
        
        subtitle = QLabel("AI 字幕工具集")
        subtitle.setStyleSheet("font-size: 13px; color: #cccccc; margin-bottom: 20px; background-color: transparent; border: none;")
        layout.addWidget(subtitle)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #555555;")
        layout.addWidget(line)
        
        layout.addSpacing(10)
        
        # 功能按钮
        self.btn_generate = SidebarButton("🎙️", "生成字幕")
        self.btn_split = SidebarButton("✂️", "智能分割")
        self.btn_render = SidebarButton("🎥", "视频渲染")
        
        self.buttons = [self.btn_generate, self.btn_split, self.btn_render]
        
        layout.addWidget(self.btn_generate)
        layout.addWidget(self.btn_split)
        layout.addWidget(self.btn_render)
        
        layout.addStretch()
        
        # 版本信息
        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #888888; font-size: 11px; background-color: transparent; border: none;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        self.setLayout(layout)
        self.setFixedWidth(220)
        self.setStyleSheet("background-color: #2c3e50;")
    
    def set_active_button(self, button):
        """设置活动按钮"""
        for btn in self.buttons:
            btn.update_style(btn == button)
            btn.setChecked(btn == button)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Whisper Auto Captions")
        self.resize(1200, 750)
        
        # 创建主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局：左右分栏
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧边栏
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # 右侧内容区域
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.stacked_widget, 1)  # 1 表示占据剩余空间
        
        # Create views
        self.home_view = HomeView()
        self.process_view = ProcessView()
        self.split_view = SplitView()
        self.render_view = RenderView()
        
        # Add views to stack
        self.stacked_widget.addWidget(self.home_view)      # 0 - 生成字幕
        self.stacked_widget.addWidget(self.process_view)   # 1 - 处理中
        self.stacked_widget.addWidget(self.split_view)     # 2 - 分割字幕
        self.stacked_widget.addWidget(self.render_view)    # 3 - 渲染视频
        
        # Connect sidebar signals
        self.sidebar.btn_generate.clicked.connect(self.show_generate_view)
        self.sidebar.btn_split.clicked.connect(self.show_split_view)
        self.sidebar.btn_render.clicked.connect(self.show_render_view)
        
        # Connect other signals
        self.home_view.start_processing.connect(self.show_process_view)
        self.process_view.reset_requested.connect(self.show_generate_view)
        self.process_view.split_requested.connect(self.show_split_with_file)
        
        # 默认显示生成字幕页面
        self.show_generate_view()
        
    def show_generate_view(self):
        """显示生成字幕视图"""
        # 检查是否有正在进行的处理
        try:
            is_processing = (self.process_view.processor is not None and 
                           hasattr(self.process_view.processor, 'isRunning') and
                           self.process_view.processor.isRunning())
        except:
            is_processing = False
        
        # 也检查 home_view 的处理标志
        if not is_processing and hasattr(self.home_view, '_processing'):
            is_processing = self.home_view._processing
        
        if is_processing:
            # 如果正在处理，显示处理页面而不是首页
            self.stacked_widget.setCurrentWidget(self.process_view)
            self.sidebar.set_active_button(self.sidebar.btn_generate)
        else:
            # 否则显示首页
            self.stacked_widget.setCurrentWidget(self.home_view)
            self.sidebar.set_active_button(self.sidebar.btn_generate)
            # 只有在没有处理时才重置
            if not hasattr(self.home_view, '_processing') or not self.home_view._processing:
                self.home_view.reset()
        
    def show_split_view(self):
        """显示分割字幕视图"""
        self.stacked_widget.setCurrentWidget(self.split_view)
        self.sidebar.set_active_button(self.sidebar.btn_split)
        # 只有在非处理状态时才重置
        if not hasattr(self.split_view, '_processing') or not self.split_view._processing:
            self.split_view.reset()
    
    def show_split_with_file(self, srt_path):
        """显示分割字幕视图并预填充文件"""
        self.stacked_widget.setCurrentWidget(self.split_view)
        self.split_view.load_srt_file(srt_path)
        self.sidebar.set_active_button(self.sidebar.btn_split)
    
    def show_split_with_full_data(self, video_file, srt_file):
        """显示分割字幕视图并预填充视频和字幕文件"""
        self.stacked_widget.setCurrentWidget(self.split_view)
        # 先加载视频文件
        if video_file:
            self.split_view.load_video_file(video_file)
        # 再加载字幕文件，并自动勾选"使用现有字幕"
        if srt_file:
            self.split_view.use_existing_srt.setChecked(True)
            self.split_view.load_srt_file(srt_file)
        self.sidebar.set_active_button(self.sidebar.btn_split)
        
    def show_render_view(self):
        """显示渲染视频视图"""
        self.stacked_widget.setCurrentWidget(self.render_view)
        self.sidebar.set_active_button(self.sidebar.btn_render)
        # 只有在非处理状态时才重置
        if not hasattr(self.render_view, '_processing') or not self.render_view._processing:
            self.render_view.reset()
        
    def show_process_view(self, data):
        """Switch to process view with data"""
        self.process_view.start_processing(data)
        self.stacked_widget.setCurrentWidget(self.process_view)
        # 处理页面保持当前侧边栏按钮高亮

