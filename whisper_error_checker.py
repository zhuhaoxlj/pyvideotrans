#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper 字幕错误检测工具
使用 LLM 分析 Whisper 识别的字幕中可能存在的错误
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QLineEdit, QGroupBox,
    QProgressBar, QFileDialog, QMessageBox, QSplitter, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QTextCharFormat, QColor, QFont

from openai import OpenAI
import httpx


@dataclass
class SubtitleBlock:
    """字幕块"""
    index: int
    start_time: str
    end_time: str
    text: str

    def to_dict(self):
        return {
            'index': self.index,
            'start': self.start_time,
            'end': self.end_time,
            'text': self.text
        }


class SubtitleParser:
    """SRT字幕解析器"""

    @staticmethod
    def parse_srt(file_path: str) -> List[SubtitleBlock]:
        """解析SRT文件"""
        blocks = []
        content = Path(file_path).read_text(encoding='utf-8')

        # 分割成字幕块
        subtitle_blocks = re.split(r'\n\n+', content.strip())

        for block in subtitle_blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue

            try:
                index = int(lines[0])
                time_line = lines[1]
                text = '\n'.join(lines[2:])

                # 解析时间戳
                match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', time_line)
                if match:
                    start_time = match.group(1)
                    end_time = match.group(2)
                    blocks.append(SubtitleBlock(index, start_time, end_time, text))
            except Exception as e:
                print(f"解析字幕块失败: {e}")
                continue

        return blocks


class TestConnectionWorker(QThread):
    """测试LLM连接的后台线程"""
    success = Signal(str)
    error = Signal(str)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    def run(self):
        try:
            http_client = None
            if self.config.get('proxy'):
                http_client = httpx.Client(proxy=self.config['proxy'], timeout=30)

            client = OpenAI(
                api_key=self.config['api_key'],
                base_url=self.config['api_url'],
                http_client=http_client
            )

            response = client.chat.completions.create(
                model=self.config['model'],
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )

            if response.choices:
                self.success.emit("连接成功！LLM响应正常。")
            else:
                self.error.emit("LLM返回为空")
        except Exception as e:
            self.error.emit(f"连接失败: {str(e)}")


class LLMWorker(QThread):
    """LLM处理线程"""
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, subtitles: List[SubtitleBlock], prompt: str, config: dict):
        super().__init__()
        self.subtitles = subtitles
        self.prompt = prompt
        self.config = config

    def run(self):
        try:
            # 准备字幕数据
            subtitle_texts = []
            for sub in self.subtitles:
                subtitle_texts.append(f"[{sub.index}] {sub.text}")

            # 将字幕分批处理
            batch_size = self.config.get('batch_size', 50)
            all_results = []

            total_batches = (len(subtitle_texts) + batch_size - 1) // batch_size
            
            for i in range(0, len(subtitle_texts), batch_size):
                batch = subtitle_texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                self.progress.emit(f"📦 处理批次 {batch_num}/{total_batches}...")

                result = self._call_llm(batch)
                if result:
                    all_results.extend(result)
                    self.progress.emit(f"✅ 批次 {batch_num}/{total_batches} 完成，累计发现 {len(all_results)} 处错误")

            self.finished.emit({'corrections': all_results, 'subtitles': self.subtitles})

        except Exception as e:
            self.error.emit(f"LLM处理错误: {str(e)}")

    def _call_llm(self, subtitle_batch: List[str]) -> List[Dict]:
        """调用LLM API（流式输出）"""
        api_url = self.config['api_url']
        api_key = self.config['api_key']
        model = self.config['model']
        proxy = self.config.get('proxy', '')

        # 准备消息
        subtitle_text = '\n'.join(subtitle_batch)
        system_prompt = self.prompt
        user_content = f"""请分析以下字幕文本，找出可能是Whisper语音识别错误的单词或短语。

字幕内容：
{subtitle_text}

请以JSON格式返回结果，格式如下：
{{
  "corrections": [
    {{
      "subtitle_index": 1,
      "original": "错误的词",
      "corrected": "正确的词",
      "reason": "修正原因"
    }}
  ]
}}

如果没有发现错误，返回空数组。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # 创建OpenAI客户端
        http_client = None
        if proxy:
            http_client = httpx.Client(proxy=proxy, timeout=300)

        client = OpenAI(
            api_key=api_key,
            base_url=api_url,
            http_client=http_client
        )

        # 调用流式API
        self.progress.emit(f"🚀 开始调用LLM API（流式输出）...")
        
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=float(self.config.get('temperature', 0.7)),
                max_tokens=int(self.config.get('max_tokens', 4096)),
                stream=True,  # 启用流式输出
                response_format={"type": "json_object"} if self.config.get('json_mode', True) else None
            )

            # 接收流式响应
            full_response = ""
            chunk_count = 0
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    chunk_count += 1
                    
                    # 每收到10个chunk更新一次进度
                    if chunk_count % 10 == 0:
                        preview = full_response[-100:] if len(full_response) > 100 else full_response
                        self.progress.emit(f"📥 接收中... ({len(full_response)} 字符)")
            
            self.progress.emit(f"✅ 接收完成，共 {len(full_response)} 字符")

            if not full_response:
                raise RuntimeError("LLM返回为空")

            # 解析JSON
            try:
                result = json.loads(full_response)
                corrections = result.get('corrections', [])
                self.progress.emit(f"🔍 解析完成，发现 {len(corrections)} 处可能错误")
                return corrections
            except json.JSONDecodeError as e:
                self.progress.emit(f"❌ JSON解析错误: {e}")
                self.progress.emit(f"原始响应: {full_response[:200]}...")
                # 尝试提取corrections数组
                import re
                match = re.search(r'"corrections"\s*:\s*\[(.*?)\]', full_response, re.DOTALL)
                if match:
                    try:
                        corrections_json = f'{{"corrections":[{match.group(1)}]}}'
                        result = json.loads(corrections_json)
                        return result.get('corrections', [])
                    except:
                        pass
                return []
                
        except Exception as e:
            self.progress.emit(f"❌ API调用失败: {str(e)}")
            raise


class WhisperErrorCheckerGUI(QMainWindow):
    """Whisper错误检测GUI主窗口"""

    def __init__(self):
        super().__init__()
        self.subtitles: List[SubtitleBlock] = []
        self.current_file = None
        self.worker = None
        self.test_worker = None
        self.corrections = []
        self.prompt_templates = {}

        self.init_ui()
        self.load_prompt_templates()
        self.load_default_prompt()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Whisper 字幕错误检测工具")
        self.setGeometry(100, 100, 1400, 900)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 文件选择区域
        file_group = QGroupBox("字幕文件")
        file_layout = QHBoxLayout()
        self.file_label = QLabel("拖入字幕文件或点击选择...")
        self.file_label.setStyleSheet("QLabel { padding: 10px; border: 2px dashed #ccc; background: #f9f9f9; }")
        self.file_label.setAcceptDrops(True)
        self.file_label.dragEnterEvent = self.drag_enter_event
        self.file_label.dropEvent = self.drop_event
        file_layout.addWidget(self.file_label)
        btn_select_file = QPushButton("选择文件")
        btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(btn_select_file)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # LLM配置区域
        llm_group = QGroupBox("LLM 配置")
        llm_layout = QVBoxLayout()

        # Provider 选择
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(['OpenAI', 'DeepSeek', 'SiliconFlow', 'Custom'])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        llm_layout.addLayout(provider_layout)

        # API URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("API URL:"))
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.openai.com/v1")
        url_layout.addWidget(self.api_url_input)
        llm_layout.addLayout(url_layout)

        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("输入你的API Key")
        key_layout.addWidget(self.api_key_input)
        llm_layout.addLayout(key_layout)

        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_input = QComboBox()
        self.model_input.setEditable(True)
        model_layout.addWidget(self.model_input)
        llm_layout.addLayout(model_layout)

        # 高级选项
        advanced_layout = QHBoxLayout()
        advanced_layout.addWidget(QLabel("Temperature:"))
        self.temperature_input = QLineEdit("0.7")
        self.temperature_input.setMaximumWidth(80)
        advanced_layout.addWidget(self.temperature_input)
        advanced_layout.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_input = QLineEdit("4096")
        self.max_tokens_input.setMaximumWidth(100)
        advanced_layout.addWidget(self.max_tokens_input)
        advanced_layout.addWidget(QLabel("Batch Size:"))
        self.batch_size_input = QLineEdit("30")
        self.batch_size_input.setMaximumWidth(80)
        advanced_layout.addWidget(self.batch_size_input)
        self.json_mode_check = QCheckBox("JSON Mode")
        self.json_mode_check.setChecked(True)
        advanced_layout.addWidget(self.json_mode_check)
        advanced_layout.addStretch()
        llm_layout.addLayout(advanced_layout)

        # Proxy
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(QLabel("Proxy (可选):"))
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:7890")
        proxy_layout.addWidget(self.proxy_input)
        llm_layout.addLayout(proxy_layout)

        # 测试连接按钮
        btn_test = QPushButton("测试 LLM 连接")
        btn_test.clicked.connect(self.test_llm_connection)
        llm_layout.addWidget(btn_test)

        llm_group.setLayout(llm_layout)
        main_layout.addWidget(llm_group)

        # Prompt区域
        prompt_group = QGroupBox("LLM Prompt (系统提示词)")
        prompt_layout = QVBoxLayout()
        
        # Prompt模板选择
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("预设模板:"))
        self.prompt_template_combo = QComboBox()
        self.prompt_template_combo.currentTextChanged.connect(self.load_prompt_template)
        template_layout.addWidget(self.prompt_template_combo)
        btn_reload_templates = QPushButton("🔄 重新加载")
        btn_reload_templates.setMaximumWidth(100)
        btn_reload_templates.clicked.connect(self.load_prompt_templates)
        template_layout.addWidget(btn_reload_templates)
        template_layout.addStretch()
        prompt_layout.addLayout(template_layout)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(150)
        prompt_layout.addWidget(self.prompt_input)
        prompt_group.setLayout(prompt_layout)
        main_layout.addWidget(prompt_group)

        # 执行按钮
        btn_layout = QHBoxLayout()
        self.btn_execute = QPushButton("🚀 开始分析")
        self.btn_execute.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; background: #4CAF50; color: white; }")
        self.btn_execute.clicked.connect(self.execute_analysis)
        btn_layout.addWidget(self.btn_execute)
        main_layout.addLayout(btn_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # 结果显示区域 - 使用分割器
        results_splitter = QSplitter(Qt.Horizontal)

        # 左侧：修正列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("检测到的错误:"))
        self.corrections_display = QTextEdit()
        self.corrections_display.setReadOnly(True)
        left_layout.addWidget(self.corrections_display)
        results_splitter.addWidget(left_widget)

        # 右侧：对比视图
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("修正后的字幕:"))
        self.comparison_display = QTextEdit()
        self.comparison_display.setReadOnly(True)
        right_layout.addWidget(self.comparison_display)
        results_splitter.addWidget(right_widget)

        results_splitter.setStretchFactor(0, 1)
        results_splitter.setStretchFactor(1, 2)

        main_layout.addWidget(results_splitter, stretch=1)

        # 导出按钮
        export_layout = QHBoxLayout()
        btn_export_srt = QPushButton("导出修正后的字幕")
        btn_export_srt.clicked.connect(self.export_corrected_srt)
        export_layout.addWidget(btn_export_srt)
        btn_export_report = QPushButton("导出错误报告")
        btn_export_report.clicked.connect(self.export_error_report)
        export_layout.addWidget(btn_export_report)
        main_layout.addLayout(export_layout)

        # 设置默认Provider
        self.on_provider_changed('OpenAI')

    def load_prompt_templates(self):
        """加载Prompt模板"""
        template_file = Path(__file__).parent / "whisper_checker_prompts.json"
        
        self.prompt_templates = {}
        if template_file.exists():
            try:
                data = json.loads(template_file.read_text(encoding='utf-8'))
                self.prompt_templates = data
            except Exception as e:
                print(f"加载模板失败: {e}")
        
        # 更新下拉列表
        self.prompt_template_combo.clear()
        self.prompt_template_combo.addItem("自定义", "custom")
        
        for key, template in self.prompt_templates.items():
            name = template.get('name', key)
            self.prompt_template_combo.addItem(name, key)
        
        if not self.prompt_templates:
            self.status_label.setText("⚠️ 未找到预设模板文件 whisper_checker_prompts.json")
    
    def load_prompt_template(self, template_name: str):
        """加载选中的模板"""
        current_data = self.prompt_template_combo.currentData()
        if current_data == "custom" or not current_data:
            return
        
        if current_data in self.prompt_templates:
            prompt = self.prompt_templates[current_data].get('prompt', '')
            self.prompt_input.setText(prompt)
    
    def load_default_prompt(self):
        """加载默认Prompt"""
        # 尝试加载预设的default模板
        if 'default' in self.prompt_templates:
            prompt = self.prompt_templates['default'].get('prompt', '')
            self.prompt_input.setText(prompt)
        else:
            # 使用硬编码的默认提示
            default_prompt = """你是一个专业的字幕校对助手，专门分析Whisper语音识别可能出现的错误。

请注意以下常见的Whisper识别错误类型：
1. 同音词混淆（如：their/there/they're, your/you're, its/it's）
2. 专有名词识别错误（人名、地名、品牌名）
3. 技术术语或行业术语错误
4. 语法不通顺的地方
5. 上下文语义不连贯

请基于上下文语义分析，只标注那些明显可能是识别错误的地方。
不要过度修正，保持原文风格。"""
            self.prompt_input.setText(default_prompt)

    def on_provider_changed(self, provider: str):
        """Provider改变时更新默认配置"""
        if provider == 'OpenAI':
            self.api_url_input.setText('https://api.openai.com/v1')
            self.model_input.clear()
            self.model_input.addItems(['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'])
            self.model_input.setCurrentText('gpt-4o-mini')
        elif provider == 'DeepSeek':
            self.api_url_input.setText('https://api.deepseek.com/v1')
            self.model_input.clear()
            self.model_input.addItems(['deepseek-chat', 'deepseek-reasoner'])
            self.model_input.setCurrentText('deepseek-chat')
        elif provider == 'SiliconFlow':
            self.api_url_input.setText('https://api.siliconflow.cn/v1')
            self.model_input.clear()
            self.model_input.addItems(['Qwen/Qwen2.5-7B-Instruct', 'Qwen/Qwen2-7B-Instruct'])
            self.model_input.setCurrentText('Qwen/Qwen2.5-7B-Instruct')
        elif provider == 'Custom':
            self.api_url_input.setText('')
            self.model_input.clear()

    def drag_enter_event(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(self, event: QDropEvent):
        """拖拽释放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.srt'):
                self.load_subtitle_file(file_path)
            else:
                QMessageBox.warning(self, "错误", "请拖入.srt字幕文件")

    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择字幕文件",
            "",
            "SRT 字幕文件 (*.srt)"
        )
        if file_path:
            self.load_subtitle_file(file_path)

    def load_subtitle_file(self, file_path: str):
        """加载字幕文件"""
        try:
            self.subtitles = SubtitleParser.parse_srt(file_path)
            self.current_file = file_path
            self.file_label.setText(f"已加载: {Path(file_path).name} ({len(self.subtitles)} 条字幕)")
            self.status_label.setText(f"✅ 成功加载 {len(self.subtitles)} 条字幕")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载字幕文件失败: {str(e)}")

    def test_llm_connection(self):
        """测试LLM连接（使用后台线程避免UI冻结）"""
        config = self.get_llm_config()
        
        # 验证配置
        if not config['api_key']:
            QMessageBox.warning(self, "错误", "请先输入API Key")
            return
        if not config['api_url']:
            QMessageBox.warning(self, "错误", "请先输入API URL")
            return
        if not config['model']:
            QMessageBox.warning(self, "错误", "请先选择模型")
            return
        
        # 禁用按钮，显示进度
        self.status_label.setText("⏳ 正在测试连接，请稍候...")
        QApplication.setOverrideCursor(Qt.WaitCursor)  # 设置等待光标
        
        # 创建并启动测试线程
        self.test_worker = TestConnectionWorker(config)
        self.test_worker.success.connect(self.on_test_success)
        self.test_worker.error.connect(self.on_test_error)
        self.test_worker.finished.connect(lambda: QApplication.restoreOverrideCursor())  # 恢复光标
        self.test_worker.start()
    
    def on_test_success(self, message: str):
        """测试成功"""
        QApplication.restoreOverrideCursor()
        QMessageBox.information(self, "成功", f"✅ {message}")
        self.status_label.setText(f"✅ {message}")
    
    def on_test_error(self, error_msg: str):
        """测试失败"""
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(self, "错误", f"❌ {error_msg}")
        self.status_label.setText(f"❌ {error_msg}")

    def get_llm_config(self) -> dict:
        """获取LLM配置"""
        return {
            'api_url': self.api_url_input.text().strip(),
            'api_key': self.api_key_input.text().strip(),
            'model': self.model_input.currentText().strip(),
            'temperature': self.temperature_input.text().strip(),
            'max_tokens': self.max_tokens_input.text().strip(),
            'batch_size': int(self.batch_size_input.text().strip() or 30),
            'proxy': self.proxy_input.text().strip(),
            'json_mode': self.json_mode_check.isChecked()
        }

    def execute_analysis(self):
        """执行分析"""
        if not self.subtitles:
            QMessageBox.warning(self, "错误", "请先加载字幕文件")
            return

        config = self.get_llm_config()
        if not config['api_key']:
            QMessageBox.warning(self, "错误", "请输入API Key")
            return
        if not config['api_url']:
            QMessageBox.warning(self, "错误", "请输入API URL")
            return
        if not config['model']:
            QMessageBox.warning(self, "错误", "请选择模型")
            return

        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "错误", "请输入Prompt")
            return

        # 禁用按钮，显示进度条
        self.btn_execute.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定模式
        QApplication.setOverrideCursor(Qt.WaitCursor)  # 设置等待光标

        # 清空之前的结果
        self.corrections_display.clear()
        self.comparison_display.clear()

        # 创建并启动工作线程
        self.worker = LLMWorker(self.subtitles, prompt, config)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, message: str):
        """进度更新"""
        self.status_label.setText(message)

    def on_finished(self, result: dict):
        """分析完成"""
        QApplication.restoreOverrideCursor()  # 恢复光标
        self.btn_execute.setEnabled(True)
        self.progress_bar.setVisible(False)

        corrections = result['corrections']
        self.corrections = corrections
        self.subtitles = result['subtitles']

        if not corrections:
            self.status_label.setText("✅ 分析完成，未发现明显错误")
            QMessageBox.information(self, "完成", "未发现明显的识别错误")
            return

        # 显示修正列表
        corrections_text = f"发现 {len(corrections)} 处可能的错误:\n\n"
        for i, corr in enumerate(corrections, 1):
            corrections_text += f"{i}. 字幕 [{corr.get('subtitle_index', '?')}]\n"
            corrections_text += f"   原文: {corr.get('original', '')}\n"
            corrections_text += f"   修正: {corr.get('corrected', '')}\n"
            corrections_text += f"   原因: {corr.get('reason', '')}\n\n"

        self.corrections_display.setPlainText(corrections_text)

        # 生成对比视图
        self.generate_comparison_view(corrections)

        self.status_label.setText(f"✅ 分析完成，发现 {len(corrections)} 处可能的错误")

    def on_error(self, error_msg: str):
        """处理错误"""
        QApplication.restoreOverrideCursor()  # 恢复光标
        self.btn_execute.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ 错误: {error_msg}")
        QMessageBox.critical(self, "错误", error_msg)

    def generate_comparison_view(self, corrections: List[Dict]):
        """生成对比视图，高亮修改的单词"""
        # 创建修正映射
        correction_map = {}
        for corr in corrections:
            idx = corr.get('subtitle_index')
            if idx:
                if idx not in correction_map:
                    correction_map[idx] = []
                correction_map[idx].append(corr)

        # 生成HTML格式的对比
        self.comparison_display.clear()
        html_parts = []
        html_parts.append("<html><body style='font-family: monospace;'>")

        for sub in self.subtitles:
            if sub.index in correction_map:
                # 有修正的字幕
                html_parts.append(f"<div style='margin-bottom: 20px; padding: 10px; background: #fff9e6; border-left: 4px solid #ff9800;'>")
                html_parts.append(f"<div style='color: #666; font-size: 12px;'>[{sub.index}] {sub.start_time} --> {sub.end_time}</div>")

                # 原文
                original_text = sub.text
                html_parts.append(f"<div style='margin-top: 5px;'><strong>原文:</strong> {original_text}</div>")

                # 修正后的文本
                corrected_text = original_text
                for corr in correction_map[sub.index]:
                    original = corr.get('original', '')
                    corrected = corr.get('corrected', '')
                    if original and corrected:
                        # 高亮修改
                        corrected_text = corrected_text.replace(
                            original,
                            f"<span style='background: #ffeb3b; color: #d32f2f; font-weight: bold;'>{corrected}</span>"
                        )

                html_parts.append(f"<div style='margin-top: 5px;'><strong>修正:</strong> {corrected_text}</div>")
                html_parts.append("</div>")
            else:
                # 无修正的字幕（可选择性显示）
                # html_parts.append(f"<div style='margin-bottom: 10px; color: #999;'>")
                # html_parts.append(f"<div style='font-size: 12px;'>[{sub.index}] {sub.start_time} --> {sub.end_time}</div>")
                # html_parts.append(f"<div>{sub.text}</div>")
                # html_parts.append("</div>")
                pass

        html_parts.append("</body></html>")
        self.comparison_display.setHtml(''.join(html_parts))

    def export_corrected_srt(self):
        """导出修正后的字幕"""
        if not self.corrections:
            QMessageBox.warning(self, "提示", "没有可导出的修正")
            return

        # 创建修正映射
        correction_map = {}
        for corr in self.corrections:
            idx = corr.get('subtitle_index')
            if idx:
                if idx not in correction_map:
                    correction_map[idx] = []
                correction_map[idx].append(corr)

        # 应用修正
        corrected_subtitles = []
        for sub in self.subtitles:
            text = sub.text
            if sub.index in correction_map:
                for corr in correction_map[sub.index]:
                    original = corr.get('original', '')
                    corrected = corr.get('corrected', '')
                    if original and corrected:
                        text = text.replace(original, corrected)

            corrected_subtitles.append(f"{sub.index}\n{sub.start_time} --> {sub.end_time}\n{text}\n")

        # 保存文件
        if self.current_file:
            default_name = Path(self.current_file).stem + "_corrected.srt"
        else:
            default_name = "corrected.srt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存修正后的字幕",
            default_name,
            "SRT 字幕文件 (*.srt)"
        )

        if file_path:
            try:
                Path(file_path).write_text('\n'.join(corrected_subtitles), encoding='utf-8')
                QMessageBox.information(self, "成功", f"已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def export_error_report(self):
        """导出错误报告"""
        if not self.corrections:
            QMessageBox.warning(self, "提示", "没有可导出的报告")
            return

        # 生成报告
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("Whisper 字幕识别错误报告")
        report_lines.append("=" * 60)
        report_lines.append(f"源文件: {self.current_file}")
        report_lines.append(f"总字幕数: {len(self.subtitles)}")
        report_lines.append(f"发现错误数: {len(self.corrections)}")
        report_lines.append("=" * 60)
        report_lines.append("")

        for i, corr in enumerate(self.corrections, 1):
            report_lines.append(f"{i}. 字幕 [{corr.get('subtitle_index', '?')}]")
            report_lines.append(f"   原文: {corr.get('original', '')}")
            report_lines.append(f"   修正: {corr.get('corrected', '')}")
            report_lines.append(f"   原因: {corr.get('reason', '')}")
            report_lines.append("")

        # 保存报告
        if self.current_file:
            default_name = Path(self.current_file).stem + "_error_report.txt"
        else:
            default_name = "error_report.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存错误报告",
            default_name,
            "文本文件 (*.txt)"
        )

        if file_path:
            try:
                Path(file_path).write_text('\n'.join(report_lines), encoding='utf-8')
                QMessageBox.information(self, "成功", f"已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Whisper 字幕错误检测工具")

    # 设置应用样式
    app.setStyle("Fusion")

    window = WhisperErrorCheckerGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

