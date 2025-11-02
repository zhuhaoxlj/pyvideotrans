#!/usr/bin/env python3
"""
Whisper 词级时间戳检测工具 - get_srt_zimu 专用版本

功能：
1. 读取 get_srt_zimu 生成的 Whisper 缓存词级时间戳
2. 显示所有单词及其时间戳
3. 点击单词跳转到视频对应位置播放
4. 验证时间戳是否准确
"""

import sys
import pickle
import hashlib
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QScrollArea,
    QGridLayout, QMessageBox, QSlider, QStyle
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class WordButton(QPushButton):
    """单词按钮，显示单词和时间戳"""
    
    def __init__(self, word_data, index, is_dark_theme=False):
        super().__init__()
        self.word_data = word_data
        self.index = index
        self.is_dark_theme = is_dark_theme
        
        word = word_data['word'].strip()
        start = word_data['start']
        end = word_data['end']
        
        # 格式化显示
        self.setText(f"{word}\n{self.format_time(start)}")
        
        # 设置样式
        self.setMinimumHeight(60)
        self.setMaximumWidth(150)
        
        # 根据主题设置样式
        if is_dark_theme:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #37474f;
                    border: 2px solid #64b5f6;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                    color: #e3f2fd;
                }
                QPushButton:hover {
                    background-color: #455a64;
                    border-color: #90caf9;
                }
                QPushButton:pressed {
                    background-color: #1976d2;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #90caf9;
                }
                QPushButton:pressed {
                    background-color: #1976d2;
                    color: white;
                }
            """)
        
        # 工具提示
        self.setToolTip(f"单词: {word}\n开始: {self.format_time(start)}\n结束: {self.format_time(end)}\n持续: {end-start:.3f}秒")
    
    def format_time(self, seconds):
        """格式化时间显示"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"


class WhisperTimestampChecker(QMainWindow):
    """Whisper 时间戳检测器主窗口 - get_srt_zimu 版"""
    
    def __init__(self):
        super().__init__()
        self.video_file = None
        self.cache_file = None
        self.words_data = []
        self.current_word_index = -1
        
        # get_srt_zimu 的缓存目录
        self.cache_dir = Path.home() / 'Videos' / 'pyvideotrans' / 'get_srt_zimu' / 'whisper_cache'
        
        self.setWindowTitle("🔍 Whisper 词级时间戳检测工具 (get_srt_zimu)")
        self.setMinimumSize(1400, 900)
        
        # 检测主题
        palette = self.palette()
        self.is_dark_theme = palette.color(QPalette.Window).lightness() < 128
        
        # 初始化媒体播放器
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # 连接信号
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel("🔍 Whisper 词级时间戳精确度检测器 (get_srt_zimu)")
        if self.is_dark_theme:
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #90caf9;
                    padding: 10px;
                    background-color: #263238;
                    border-radius: 5px;
                }
            """)
        else:
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #1976d2;
                    padding: 10px;
                    background-color: #e3f2fd;
                    border-radius: 5px;
                }
            """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 说明
        info_label = QLabel(
            "📝 使用说明：\n"
            "1. 选择已处理过的视频文件\n"
            "2. 工具会自动在缓存目录中查找对应的 Whisper 词级时间戳\n"
            f"3. 缓存目录：{self.cache_dir}\n"
            "4. 点击任意单词，视频会跳转到该单词的时间戳位置\n"
            "5. 观察视频中实际说这个词的时间是否和时间戳一致"
        )
        if self.is_dark_theme:
            info_label.setStyleSheet("""
                QLabel {
                    background-color: #3e2723;
                    color: #ffcc80;
                    padding: 10px;
                    border-radius: 5px;
                    border: 2px solid #ff9800;
                }
            """)
        else:
            info_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3e0;
                    color: #e65100;
                    padding: 10px;
                    border-radius: 5px;
                    border: 2px solid #ff9800;
                }
            """)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # 文件选择按钮
        btn_layout = QHBoxLayout()
        
        self.select_video_btn = QPushButton("📁 选择视频文件")
        self.select_video_btn.setMinimumHeight(50)
        self.select_video_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.select_video_btn.clicked.connect(self.select_video)
        btn_layout.addWidget(self.select_video_btn)
        
        self.video_file_label = QLabel("未选择视频文件")
        label_color = "#999" if self.is_dark_theme else "#666"
        self.video_file_label.setStyleSheet(f"QLabel {{ color: {label_color}; padding: 10px; }}")
        btn_layout.addWidget(self.video_file_label, 1)
        
        main_layout.addLayout(btn_layout)
        
        # 创建水平分割：左侧视频，右侧单词列表
        content_layout = QHBoxLayout()
        
        # 左侧：视频播放器
        video_layout = QVBoxLayout()
        
        video_label = QLabel("📹 视频播放器")
        title_color = "#90caf9" if self.is_dark_theme else "#1976d2"
        video_label.setStyleSheet(f"QLabel {{ font-weight: bold; font-size: 14px; color: {title_color}; }}")
        video_layout.addWidget(video_label)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 480)
        self.video_widget.setStyleSheet("QVideoWidget { background-color: black; }")
        self.media_player.setVideoOutput(self.video_widget)
        video_layout.addWidget(self.video_widget)
        
        # 播放控制
        controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn)
        
        self.position_label = QLabel("00:00.000")
        self.position_label.setMinimumWidth(100)
        controls_layout.addWidget(self.position_label)
        
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.setEnabled(False)
        controls_layout.addWidget(self.position_slider)
        
        self.duration_label = QLabel("00:00.000")
        self.duration_label.setMinimumWidth(100)
        controls_layout.addWidget(self.duration_label)
        
        video_layout.addLayout(controls_layout)
        
        # 当前单词信息
        self.current_word_label = QLabel("点击单词查看详情")
        if self.is_dark_theme:
            self.current_word_label.setStyleSheet("""
                QLabel {
                    background-color: #263238;
                    color: #e0e0e0;
                    padding: 15px;
                    border-radius: 5px;
                    border: 2px solid #64b5f6;
                    font-size: 14px;
                }
            """)
        else:
            self.current_word_label.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    color: #000000;
                    padding: 15px;
                    border-radius: 5px;
                    border: 2px solid #2196f3;
                    font-size: 14px;
                }
            """)
        self.current_word_label.setAlignment(Qt.AlignCenter)
        self.current_word_label.setMinimumHeight(100)
        video_layout.addWidget(self.current_word_label)
        
        content_layout.addLayout(video_layout, 1)
        
        # 右侧：单词列表
        words_layout = QVBoxLayout()
        
        words_label = QLabel("📝 单词列表（点击跳转）")
        words_label.setStyleSheet(f"QLabel {{ font-weight: bold; font-size: 14px; color: {title_color}; }}")
        words_layout.addWidget(words_label)
        
        self.stats_label = QLabel("等待加载...")
        stats_color = "#999" if self.is_dark_theme else "#666"
        self.stats_label.setStyleSheet(f"QLabel {{ color: {stats_color}; padding: 5px; }}")
        words_layout.addWidget(self.stats_label)
        
        # 滚动区域显示单词
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_border = "#455a64" if self.is_dark_theme else "#e0e0e0"
        scroll.setStyleSheet(f"QScrollArea {{ border: 2px solid {scroll_border}; border-radius: 5px; }}")
        
        self.words_container = QWidget()
        self.words_layout = QGridLayout(self.words_container)
        self.words_layout.setSpacing(5)
        self.words_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.words_container)
        words_layout.addWidget(scroll)
        
        content_layout.addLayout(words_layout, 1)
        
        main_layout.addLayout(content_layout)
        
        # 状态栏
        self.status_label = QLabel("👋 欢迎使用 Whisper 时间戳检测工具")
        if self.is_dark_theme:
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #1b5e20;
                    color: #a5d6a7;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e9;
                    color: #2e7d32;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
        main_layout.addWidget(self.status_label)
    
    def select_video(self):
        """选择视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            str(Path.home() / 'Downloads'),
            "视频文件 (*.mp4 *.mkv *.avi *.mov);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        self.video_file = file_path
        self.video_file_label.setText(f"✅ {Path(file_path).name}")
        
        # 尝试加载缓存
        self.try_load_cache()
    
    def try_load_cache(self):
        """尝试加载缓存"""
        if not self.video_file:
            return
        
        # 查找缓存
        if self.find_cache():
            # 加载缓存
            if self.load_cache():
                # 加载视频
                self.load_video()
                # 显示单词
                self.display_words()
                
                self.status_label.setText(f"✅ 成功加载！点击任意单词开始检测")
                if self.is_dark_theme:
                    self.status_label.setStyleSheet("""
                        QLabel {
                            background-color: #1b5e20;
                            color: #a5d6a7;
                            padding: 10px;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                    """)
                else:
                    self.status_label.setStyleSheet("""
                        QLabel {
                            background-color: #e8f5e9;
                            color: #2e7d32;
                            padding: 10px;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                    """)
        else:
            QMessageBox.warning(
                self,
                "未找到缓存",
                f"未找到该视频的 Whisper 缓存文件。\n\n"
                f"可能原因：\n"
                f"1. 还没有用 get_srt_zimu 生成字幕工具处理该视频\n"
                f"2. 缓存已被清空\n\n"
                f"缓存目录：{self.cache_dir}\n\n"
                f"请先在主界面生成字幕，并确保启用了缓存功能。"
            )
    
    def find_cache(self):
        """查找对应的缓存文件"""
        # 计算视频文件哈希
        video_hash = self.get_file_hash(self.video_file)
        if not video_hash:
            return False
        
        # 检查缓存目录
        if not self.cache_dir.exists():
            return False
        
        # 查找缓存文件
        cache_file = self.cache_dir / f"{video_hash}.pkl"
        
        if cache_file.exists():
            self.cache_file = cache_file
            return True
        
        return False
    
    def get_file_hash(self, filepath):
        """计算文件哈希"""
        hash_obj = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"计算哈希失败: {e}")
            return None
    
    def load_cache(self):
        """加载缓存数据"""
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.words_data = cache_data['all_words']
            language = cache_data['language']
            
            self.stats_label.setText(
                f"📊 统计：共 {len(self.words_data)} 个单词 | 语言：{language}"
            )
            
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "加载失败",
                f"无法加载缓存文件：\n{str(e)}"
            )
            return False
    
    def load_video(self):
        """加载视频"""
        self.media_player.setSource(QUrl.fromLocalFile(self.video_file))
        self.play_btn.setEnabled(True)
        self.position_slider.setEnabled(True)
    
    def display_words(self):
        """显示所有单词"""
        # 清空现有单词
        while self.words_layout.count():
            item = self.words_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加单词按钮
        cols = 6  # 每行显示6个单词
        for i, word_data in enumerate(self.words_data):
            btn = WordButton(word_data, i, self.is_dark_theme)
            btn.clicked.connect(lambda checked, idx=i: self.word_clicked(idx))
            
            row = i // cols
            col = i % cols
            self.words_layout.addWidget(btn, row, col)
    
    def word_clicked(self, index):
        """单词被点击"""
        self.current_word_index = index
        word_data = self.words_data[index]
        
        word = word_data['word'].strip()
        start = word_data['start']
        end = word_data['end']
        duration = end - start
        
        # 更新当前单词信息
        self.current_word_label.setText(
            f"🎯 当前单词：{word}\n"
            f"⏰ 开始时间：{self.format_time_display(start)}\n"
            f"⏱️  结束时间：{self.format_time_display(end)}\n"
            f"⌛ 持续时长：{duration:.3f} 秒\n"
            f"📍 位置：第 {index + 1} / {len(self.words_data)} 个单词"
        )
        
        # 跳转到该时间并播放
        position_ms = int(start * 1000)
        self.media_player.setPosition(position_ms)
        self.media_player.play()
        
        self.status_label.setText(
            f"🎬 正在播放单词 '{word}' | 时间：{self.format_time_display(start)} | "
            f"请注意观察视频中实际说这个词的时间是否匹配"
        )
        if self.is_dark_theme:
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #3e2723;
                    color: #ffcc80;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3e0;
                    color: #e65100;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
    
    def toggle_play(self):
        """切换播放/暂停"""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
    
    def position_changed(self, position):
        """播放位置改变"""
        self.position_slider.setValue(position)
        self.position_label.setText(self.format_time_display(position / 1000))
    
    def duration_changed(self, duration):
        """视频时长改变"""
        self.position_slider.setRange(0, duration)
        self.duration_label.setText(self.format_time_display(duration / 1000))
    
    def set_position(self, position):
        """设置播放位置"""
        self.media_player.setPosition(position)
    
    def format_time_display(self, seconds):
        """格式化时间显示（分:秒.毫秒）"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = WhisperTimestampChecker()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

