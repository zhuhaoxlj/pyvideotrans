"""
LLM 智能字幕分割处理器
基于大语言模型的语义理解进行智能断句
支持：从视频生成字幕、重新分割现有字幕、缓存机制等

完整迁移自 videotrans.winform.fn_llm_split
"""

import json
import re
import hashlib
import pickle
import time
import difflib
from pathlib import Path
from PySide6.QtCore import QThread, Signal


class LLMProcessor(QThread):
    """LLM 字幕分割处理线程"""
    progress = Signal(str)  # 进度信息
    stream = Signal(str)    # 流式输出
    finished_signal = Signal(str)  # 完成信号，传递输出文件路径
    error = Signal(str)     # 错误信号
    
    def __init__(self, video_file=None, srt_file=None, llm_provider='siliconflow', 
                 llm_api_key='', llm_model='Qwen/Qwen2.5-7B-Instruct', llm_base_url='',
                 language='en', model_size='large-v3-turbo', max_duration=5.0, 
                 max_words=15, device='cpu', output_dir=None, models_dir=None, enable_cache=True):
        """
        初始化 LLM 处理器
        
        Args:
            video_file: 视频文件路径（用于生成新字幕）
            srt_file: SRT 文件路径（用于重新分割现有字幕）
            llm_provider: LLM 提供商
            llm_api_key: LLM API Key
            llm_model: LLM 模型
            llm_base_url: LLM Base URL（可选）
            language: Whisper 识别语言
            model_size: Whisper 模型大小
            max_duration: 最大持续时间
            max_words: 最大词数
            device: 计算设备（cpu/cuda/mps）
            output_dir: 输出目录
            models_dir: Whisper模型目录
            enable_cache: 是否启用词级时间戳缓存
        """
        super().__init__()
        self.video_file = video_file
        self.srt_file = srt_file
        self.llm_provider = llm_provider.lower()
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model
        self.llm_base_url = llm_base_url
        self.language = language
        self.model_size = model_size
        self.max_duration = max_duration
        self.max_words = max_words
        self.device = device
        self.enable_cache = enable_cache
        
        # 设置输出目录和文件
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.home() / 'Videos' / 'pyvideotrans' / 'get_srt_zimu' / 'output'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存目录
        self.cache_dir = Path.home() / 'Videos' / 'pyvideotrans' / 'get_srt_zimu' / 'whisper_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Whisper模型目录
        if models_dir:
            self.models_dir = Path(models_dir)
        else:
            # 尝试使用get_srt_zimu的models目录，如果不存在则使用主项目的
            local_models = Path(__file__).parent.parent / 'models'
            main_models = Path(__file__).parent.parent.parent / 'models'
            self.models_dir = local_models if local_models.exists() else main_models
        
        # 确定输出文件名
        if video_file:
            base_name = Path(video_file).stem
            suffix = '_llm_resplit.srt' if srt_file else '_llm_smart.srt'
        elif srt_file:
            base_name = Path(srt_file).stem
            suffix = '_llm_split.srt'
        else:
            raise ValueError("必须提供 video_file 或 srt_file")
        
        self.output_file = str(self.output_dir / f"{base_name}{suffix}")
    
    def run(self):
        """主处理流程"""
        try:
            if self.srt_file and not self.video_file:
                # 模式1：仅重新分割现有字幕（简单模式）
                self.progress.emit('🤖 模式: 重新分割现有字幕（仅LLM）')
                self.process_srt_only()
            elif self.video_file and self.srt_file:
                # 模式2：使用视频+现有字幕重新分割
                self.progress.emit('🤖 模式: 使用视频+现有字幕（Whisper词级+LLM）')
                self.process_with_video_and_srt()
            elif self.video_file:
                # 模式3：从视频生成新字幕
                self.progress.emit('🤖 模式: 从视频生成新字幕（Whisper+LLM）')
                self.process_new_transcription()
            else:
                self.error.emit("必须提供视频文件或字幕文件")
                return
                
        except Exception as e:
            import traceback
            self.error.emit(f"处理失败: {str(e)}\n{traceback.format_exc()}")
    
    def process_srt_only(self):
        """处理模式1：仅重新分割现有字幕（简单LLM分割）"""
        # 1. 读取 SRT 文件
        self.progress.emit("📖 读取字幕文件...")
        subtitles = self.parse_srt(self.srt_file)
        if not subtitles:
            self.error.emit("无法解析字幕文件")
            return
        
        self.progress.emit(f"✅ 读取到 {len(subtitles)} 条字幕")
        
        # 2. 提取文本
        full_text = ' '.join([sub['text'] for sub in subtitles])
        self.progress.emit(f"📝 文本长度: {len(full_text)} 字符")
        
        # 3. 调用 LLM 进行智能分割
        self.progress.emit("🤖 正在调用 LLM 进行智能分割...")
        self.progress.emit(f"   提供商: {self.llm_provider}")
        self.progress.emit(f"   模型: {self.llm_model}")
        
        new_segments = self.llm_split_simple(full_text)
        
        if not new_segments:
            self.error.emit("LLM 分割失败")
            return
        
        self.progress.emit(f"✅ LLM 返回 {len(new_segments)} 个分段")
        
        # 4. 映射到时间戳
        self.progress.emit("⏰ 映射时间戳...")
        new_subtitles = self.map_timestamps(new_segments, subtitles)
        
        if not new_subtitles:
            self.error.emit("时间戳映射失败")
            return
        
        # 5. 保存结果
        self.progress.emit("💾 保存结果...")
        self.save_srt(new_subtitles)
        
        self.progress.emit(f"✅ 完成！生成 {len(new_subtitles)} 条字幕")
        self.progress.emit(f"📁 保存到: {self.output_file}")
        
        self.finished_signal.emit(self.output_file)
    
    def process_new_transcription(self):
        """处理模式3：从视频生成新字幕 + LLM优化"""
        # 检查缓存（只使用视频文件，因为词级时间戳只依赖视频内容）
        self.progress.emit('🔍 检查缓存...')
        self.progress.emit(f'   视频文件: {self.video_file}')
        cache_status = '✅ 已启用' if self.enable_cache else '❌ 已禁用'
        self.progress.emit(f'   缓存开关: {cache_status}')
        
        cached_data = None
        if self.enable_cache:
            cache_key = self.get_cache_key(self.video_file)  # 只用视频文件生成缓存key
            self.progress.emit(f'   缓存键: {cache_key[:16]}... (SHA256)')
            cached_data = self.load_cache(cache_key)
        else:
            self.progress.emit('   ⚠️  缓存已禁用，将重新识别')
        
        if cached_data:
            self.progress.emit('   ✅ 找到缓存！')
            all_words = cached_data['all_words']
            detected_language = cached_data['language']
            self.progress.emit(f'   📊 从缓存加载: {len(all_words)} 个词')
            self.progress.emit(f'   🌐 检测语言: {detected_language}')
        else:
            self.progress.emit('   ❌ 未找到缓存，开始 Whisper 处理...')
            all_words, detected_language = self.transcribe_with_whisper()
            if not all_words:
                return
            # 保存缓存（仅在启用缓存时）
            if self.enable_cache:
                cache_key = self.get_cache_key(self.video_file)
                self.save_cache(cache_key, all_words, detected_language)
            else:
                self.progress.emit('💡 提示: 缓存已禁用，未保存词级时间戳')
        
        # 使用 LLM 进行智能断句
        self.progress.emit('🤖 使用 LLM 进行智能断句优化...')
        subtitles = self.llm_smart_split(all_words, detected_language)
        
        if not subtitles:
            self.error.emit('LLM 断句失败')
            return
        
        self.progress.emit(f'✅ 生成 {len(subtitles)} 条字幕')
        
        # 保存
        self.save_srt(subtitles)
        
        self.progress.emit('💾 保存完成')
        self.finished_signal.emit(self.output_file)
    
    def process_with_video_and_srt(self):
        """处理模式2：使用视频+现有字幕重新分割"""
        self.progress.emit(f'📖 读取现有字幕: {Path(self.srt_file).name}')
        
        # 读取现有字幕
        original_subtitles = self.parse_srt(self.srt_file)
        if not original_subtitles:
            self.error.emit('无法解析字幕文件')
            return
        
        self.progress.emit(f'✅ 读取到 {len(original_subtitles)} 条原始字幕')
        
        # 提取完整文本
        original_text = ' '.join([sub['text'] for sub in original_subtitles])
        self.progress.emit(f'📝 原始文本长度: {len(original_text)} 字符')
        
        # 检查缓存（只使用视频文件，因为词级时间戳只依赖视频内容）
        self.progress.emit('🔍 检查缓存...')
        self.progress.emit(f'   视频文件: {self.video_file}')
        cache_status = '✅ 已启用' if self.enable_cache else '❌ 已禁用'
        self.progress.emit(f'   缓存开关: {cache_status}')
        
        cached_data = None
        if self.enable_cache:
            cache_key = self.get_cache_key(self.video_file)  # 不传srt_file，只用视频
            self.progress.emit(f'   缓存键: {cache_key[:16]}... (SHA256)')
            cached_data = self.load_cache(cache_key)
        else:
            self.progress.emit('   ⚠️  缓存已禁用，将重新识别')
        
        if cached_data:
            self.progress.emit('   ✅ 找到缓存！')
            all_words = cached_data['all_words']
            detected_language = cached_data['language']
            self.progress.emit(f'   📊 从缓存加载: {len(all_words)} 个词')
            self.progress.emit(f'   🌐 检测语言: {detected_language}')
        else:
            self.progress.emit('   ❌ 未找到缓存，开始 Whisper 处理...')
            all_words, detected_language = self.transcribe_with_whisper()
            if not all_words:
                return
            # 保存缓存（仅在启用缓存时）
            if self.enable_cache:
                cache_key = self.get_cache_key(self.video_file)
                self.save_cache(cache_key, all_words, detected_language)
            else:
                self.progress.emit('💡 提示: 缓存已禁用，未保存词级时间戳')
        
        # 使用 LLM 进行智能断句（使用原始文本）
        self.progress.emit('🤖 使用 LLM 进行智能断句优化...')
        subtitles = self.llm_smart_split(all_words, detected_language, original_text=original_text)
        
        if not subtitles:
            self.error.emit('LLM 断句失败')
            return
        
        self.progress.emit(f'📊 原始字幕: {len(original_subtitles)} 条 → 新字幕: {len(subtitles)} 条')
        
        # 保存
        self.save_srt(subtitles)
        
        self.progress.emit('💾 保存完成')
        self.finished_signal.emit(self.output_file)
    
    # ========== 缓存相关方法 ==========
    
    def get_file_hash(self, filepath):
        """计算文件的哈希值"""
        hash_obj = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            self.progress.emit(f'⚠️ 计算哈希值失败: {str(e)}')
            return None
    
    def get_cache_key(self, video_file, srt_file=None):
        """生成缓存键"""
        video_hash = self.get_file_hash(video_file)
        if not video_hash:
            return None
        
        if srt_file:
            srt_hash = self.get_file_hash(srt_file)
            if not srt_hash:
                return None
            return f"{video_hash}_{srt_hash}"
        
        return video_hash
    
    def save_cache(self, cache_key, all_words, language):
        """保存缓存"""
        if not cache_key:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            cache_data = {
                'all_words': all_words,
                'language': language,
                'timestamp': time.time()
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            self.progress.emit(f'💾 缓存已保存: {cache_file.name}')
        except Exception as e:
            self.progress.emit(f'⚠️ 保存缓存失败: {str(e)}')
    
    def load_cache(self, cache_key):
        """加载缓存"""
        if not cache_key:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            return cache_data
        except Exception as e:
            self.progress.emit(f'⚠️ 读取缓存失败: {str(e)}')
            return None
    
    # ========== Whisper 转录方法 ==========
    
    def transcribe_with_whisper(self):
        """使用 Whisper 进行语音识别"""
        self.progress.emit('🔧 加载 Faster-Whisper 模型...')
        
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            self.error.emit('未安装 faster-whisper\n请运行: pip install faster-whisper')
            return None, None
        
        self.progress.emit(f'📥 模型: {self.model_size}')
        
        # 设备信息
        device_name = {
            'cpu': 'CPU',
            'cuda': 'CUDA (NVIDIA GPU)',
            'mps': 'MPS (Apple Silicon GPU)'
        }.get(self.device, self.device.upper())
        self.progress.emit(f'⚙️  设备: {device_name}')
        
        # 根据设备选择计算类型
        if self.device == 'cuda':
            compute_type = "float16"
        elif self.device == 'mps':
            compute_type = "float16"
        else:
            compute_type = "int8"
        
        # 加载模型
        try:
            model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=compute_type,
                download_root=str(self.models_dir)
            )
        except ValueError as e:
            if 'unsupported device' in str(e).lower() and self.device == 'mps':
                self.progress.emit('⚠️  faster-whisper 暂不支持 MPS')
                self.progress.emit('📥 回退到 CPU 模式...')
                self.device = 'cpu'
                compute_type = 'int8'
                model = WhisperModel(
                    self.model_size,
                    device='cpu',
                    compute_type='int8',
                    download_root=str(self.models_dir)
                )
            else:
                raise
        
        self.progress.emit(f'🎤 开始识别语音...')
        self.progress.emit('⏳ 此过程可能需要几分钟，请耐心等待...')
        
        # 转录音频
        start_time = time.time()
        segments, info = model.transcribe(
            self.video_file,
            language=self.language if self.language != 'auto' else None,
            word_timestamps=True,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.5,
                min_speech_duration_ms=250,
                max_speech_duration_s=float('inf'),
                min_silence_duration_ms=2000,
                speech_pad_ms=400
            )
        )
        transcribe_time = time.time() - start_time
        
        self.progress.emit(f'✅ 识别完成！检测语言: {info.language} (耗时: {transcribe_time:.1f}秒)')
        self.progress.emit('📊 收集词级时间戳...')
        
        # 收集所有词
        all_words = []
        segment_count = 0
        for segment in segments:
            segment_count += 1
            if segment_count % 10 == 0:
                self.progress.emit(f'   处理片段: {segment_count}...')
            
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    all_words.append({
                        'word': word.word,
                        'start': word.start,
                        'end': word.end
                    })
        
        if not all_words:
            self.error.emit('未检测到任何语音内容')
            return None, None
        
        self.progress.emit(f'✅ 收集完成！共 {len(all_words)} 个词')
        
        return all_words, info.language
    
    # ========== LLM 分割方法 ==========
    
    def llm_split_simple(self, text):
        """简单的 LLM 分割（用于仅SRT模式）"""
        prompt = f"""You are an expert subtitle editor. Split the following text into natural, readable subtitle segments.

TEXT TO SPLIT:
{text}

REQUIREMENTS:
1. Each segment should be 3-6 seconds when spoken (approximately 10-15 words)
2. Split at natural phrase boundaries
3. Maintain semantic completeness
4. Consider reading speed and viewer comprehension

OUTPUT FORMAT:
Return ONLY a JSON array. Each element should be a string (the subtitle text).

Example:
["First subtitle segment here", "Second subtitle segment here", "Third subtitle segment"]

DO NOT include explanations, only return the JSON array."""
        
        try:
            self.progress.emit("   📡 正在调用 LLM API...")
            
            if self.llm_provider == 'siliconflow':
                response = self._call_siliconflow_stream(prompt)
            elif self.llm_provider == 'openai':
                response = self._call_openai_stream(prompt)
            elif self.llm_provider == 'claude':
                response = self._call_claude_stream(prompt)
            elif self.llm_provider == 'deepseek':
                response = self._call_deepseek_stream(prompt)
            else:
                response = self._call_siliconflow_stream(prompt)
            
            self.progress.emit("\n   ✅ LLM 响应完成")
            
            # 解析响应
            segments = self._parse_simple_response(response)
            return segments
            
        except Exception as e:
            self.progress.emit(f"\n   ❌ LLM 调用失败: {str(e)}") 
            raise
    
    def llm_smart_split(self, words, detected_language, original_text=None):
        """使用 LLM 进行智能断句（基于词级时间戳）"""
        if not words:
            return []
        
        # 如果有原始文本，使用原始文本；否则使用识别的文本
        reference_text = original_text if original_text else ''.join([w['word'] for w in words])
        
        # 构建 prompt
        prompt = self._build_llm_prompt(reference_text, len(words), detected_language)
        
        self.progress.emit(f'   LLM提供商: {self.llm_provider}')
        self.progress.emit(f'   LLM模型: {self.llm_model}')
        self.progress.emit(f'   处理文本: {len(words)} 词')
        self.progress.emit('   ⏳ 正在调用 LLM API，请稍候...')
        
        # 调用 LLM（支持流式传输）
        start_time = time.time()
        try:
            self.progress.emit('   📡 LLM 响应流:')
            response = self._call_llm_stream(prompt)
            llm_time = time.time() - start_time
            self.progress.emit(f'\n   ✅ LLM响应完成 (耗时: {llm_time:.1f}秒)')
        except Exception as e:
            self.progress.emit(f'   ⚠️  LLM调用失败: {str(e)}')
            self.progress.emit('   回退到规则引擎断句')
            return self.fallback_split(words)
        
        # 解析 LLM 返回的断句结果
        self.progress.emit('   📋 解析 LLM 返回结果...')
        subtitles = self._parse_llm_response(response, words)
        
        if not subtitles:
            self.progress.emit('   ⚠️  LLM返回格式错误，回退到规则引擎')
            return self.fallback_split(words)
        
        self.progress.emit(f'   ✅ 解析完成，生成 {len(subtitles)} 条字幕')
        
        # 验证和调整时间戳
        self.progress.emit('   🔧 验证和调整时间戳...')
        subtitles = self._validate_and_adjust_timestamps(subtitles)
        
        self.progress.emit('   ✅ 时间戳调整完成')
        
        return subtitles
    
    def _build_llm_prompt(self, text, word_count, language):
        """构建 LLM prompt"""
        lang_name = {
            'en': 'English',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'ru': 'Russian'
        }.get(language, 'English')
        
        prompt = f"""You are an expert subtitle editor. Your task is to split the following {lang_name} text into natural, readable subtitle segments.

TEXT TO SPLIT:
{text}

REQUIREMENTS:
1. Each subtitle should be 3-6 seconds when spoken (approximately {int(self.max_words * 0.7)}-{self.max_words} words)
2. Split at natural phrase boundaries (not in the middle of phrases)
3. Maintain semantic completeness (don't split incomplete thoughts)
4. Consider reading speed and viewer comprehension
5. Prioritize natural pauses in speech
6. Keep related concepts together (e.g., "a beautiful day" should not be split)

The text has {word_count} words total. Please split it into approximately {max(2, word_count // self.max_words)} segments.

OUTPUT FORMAT:
Return ONLY a JSON array of subtitle segments. Each segment should have:
- "text": the subtitle text
- "word_count": approximate number of words

Example output:
[
  {{"text": "Bringing people together these days is a feat.", "word_count": 8}},
  {{"text": "Thousands of people coming joyfully together", "word_count": 6}},
  {{"text": "to create a mile-long beautiful spectacle", "word_count": 7}}
]

DO NOT include explanations, only return the JSON array."""

        return prompt
    
    def _call_llm_stream(self, prompt):
        """调用 LLM API（流式传输）"""
        if self.llm_provider == 'siliconflow':
            return self._call_siliconflow_stream(prompt)
        elif self.llm_provider == 'openai':
            return self._call_openai_stream(prompt)
        elif self.llm_provider == 'claude':
            return self._call_claude_stream(prompt)
        elif self.llm_provider == 'deepseek':
            return self._call_deepseek_stream(prompt)
        else:
            return self._call_siliconflow_stream(prompt)
    
    def _call_siliconflow_stream(self, prompt):
        """调用 SiliconFlow API（流式）"""
        import requests
        
        url = 'https://api.siliconflow.cn/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.llm_api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.llm_model if self.llm_model else 'Qwen/Qwen2.5-7B-Instruct',
            'messages': [
                {'role': 'system', 'content': 'You are an expert subtitle editor.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'stream': True
        }
        
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=120)
        response.raise_for_status()
        
        full_content = []
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(data_str)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content.append(content)
                            self.stream.emit(content)
                except json.JSONDecodeError:
                    continue
        
        return ''.join(full_content)
    
    def _call_openai_stream(self, prompt):
        """调用 OpenAI API（流式）"""
        import requests
        
        url = self.llm_base_url if self.llm_base_url else 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.llm_api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.llm_model,
            'messages': [
                {'role': 'system', 'content': 'You are an expert subtitle editor.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'stream': True
        }
        
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=120)
        response.raise_for_status()
        
        full_content = []
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(data_str)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content.append(content)
                            self.stream.emit(content)
                except json.JSONDecodeError:
                    continue
        
        return ''.join(full_content)
    
    def _call_claude_stream(self, prompt):
        """调用 Claude API（流式）"""
        import requests
        
        url = 'https://api.anthropic.com/v1/messages'
        headers = {
            'x-api-key': self.llm_api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.llm_model,
            'max_tokens': 4096,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.3,
            'stream': True
        }
        
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=120)
        response.raise_for_status()
        
        full_content = []
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                
                try:
                    chunk = json.loads(data_str)
                    if chunk.get('type') == 'content_block_delta':
                        delta = chunk.get('delta', {})
                        content = delta.get('text', '')
                        if content:
                            full_content.append(content)
                            self.stream.emit(content)
                except json.JSONDecodeError:
                    continue
        
        return ''.join(full_content)
    
    def _call_deepseek_stream(self, prompt):
        """调用 DeepSeek API（流式）"""
        import requests
        
        url = 'https://api.deepseek.com/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.llm_api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.llm_model,
            'messages': [
                {'role': 'system', 'content': 'You are an expert subtitle editor.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'stream': True
        }
        
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=120)
        response.raise_for_status()
        
        full_content = []
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(data_str)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content.append(content)
                            self.stream.emit(content)
                except json.JSONDecodeError:
                    continue
        
        return ''.join(full_content)
    
    def _parse_simple_response(self, response):
        """解析简单的 LLM 返回（字符串数组）"""
        # 提取 JSON 数组
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if not json_match:
            return []
        
        try:
            segments = json.loads(json_match.group(0))
            if isinstance(segments, list):
                return [s.strip() for s in segments if isinstance(s, str) and s.strip()]
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _parse_llm_response(self, response, words):
        """解析 LLM 返回的结果（对象数组）"""
        # 尝试提取 JSON
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if not json_match:
            return []
        
        try:
            segments = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return []
        
        if not isinstance(segments, list):
            return []
        
        # 将 LLM 返回的文本段匹配到词级时间戳
        subtitles = []
        word_idx = 0
        skipped_count = 0
        
        for i, segment in enumerate(segments):
            if not isinstance(segment, dict) or 'text' not in segment:
                continue
            
            segment_text = segment['text'].strip()
            if not segment_text:
                continue
            
            # 使用增强的匹配策略
            # 如果接近尾部，放宽匹配条件
            remaining_segments = len(segments) - i
            remaining_words = len(words) - word_idx
            is_near_end = remaining_words < remaining_segments * 5
            
            match_result = self._match_text_to_words(segment_text, words, word_idx, relax=is_near_end)
            
            if match_result:
                subtitle = {
                    'start': match_result['start'],
                    'end': match_result['end'],
                    'text': segment_text
                }
                subtitles.append(subtitle)
                word_idx = match_result['next_idx']
                
                # 重置跳过计数
                skipped_count = 0
            else:
                skipped_count += 1
                self.progress.emit(f'   ⚠️  Segment {i+1} 无法匹配（已跳过 {skipped_count} 个）')
                self.progress.emit(f'      当前 word_idx: {word_idx}/{len(words)}')
                self.progress.emit(f'      文本: "{segment_text[:50]}..."')
                
                # 显示当前位置的词，帮助诊断
                if word_idx < len(words):
                    nearby_words = []
                    for j in range(word_idx, min(word_idx + 5, len(words))):
                        nearby_words.append(words[j]['word'])
                    self.progress.emit(f'      附近的词: {" ".join(nearby_words)}')
                
                # 如果连续跳过太多，强制推进 word_idx
                if skipped_count >= 3 and word_idx < len(words) - 10:
                    # 基于进度比例推进
                    progress_ratio = (i + 1) / len(segments)
                    target_idx = int(len(words) * progress_ratio)
                    jump = max(10, target_idx - word_idx)
                    word_idx = min(word_idx + jump, len(words) - 10)
                    self.progress.emit(f'      → 基于进度推进 word_idx 到 {word_idx} (跳跃{jump}个词)')
                    skipped_count = 0
        
        self.progress.emit(f'   📊 成功匹配: {len(subtitles)}/{len(segments)} 个 segments')
        return subtitles
    
    def _match_text_to_words(self, text, words, start_idx, relax=False):
        """匹配文本到词级时间戳（增强版）
        
        Args:
            text: 要匹配的文本
            words: 词级时间戳列表
            start_idx: 开始索引
            relax: 是否放宽匹配条件（用于尾部segments）
        """
        # 清理和分词
        text_clean = text.lower()
        for punct in [',', '.', '!', '?', ';', ':', '"', "'", '(', ')', '[', ']']:
            text_clean = text_clean.replace(punct, ' ')
        text_words = [w for w in text_clean.split() if w]
        
        if not text_words:
            return None
        
        # 使用动态规划进行序列对齐
        matched_indices = []
        text_idx = 0
        word_idx = start_idx
        max_lookahead = 20  # ✅ 增加前瞻范围
        consecutive_misses = 0  # 连续未匹配计数
        
        while text_idx < len(text_words) and word_idx < len(words):
            text_word = text_words[text_idx]
            best_match = None
            best_score = 0
            
            # 在当前位置附近查找最佳匹配
            for offset in range(min(max_lookahead, len(words) - word_idx)):
                if word_idx + offset >= len(words):
                    break
                
                word_data = words[word_idx + offset]
                word_text = word_data['word'].lower().strip()
                
                # 清理单词
                for punct in [',', '.', '!', '?', ';', ':', '"', "'", '(', ')', '[', ']']:
                    word_text = word_text.replace(punct, '')
                word_text = word_text.strip()
                
                if not word_text:
                    continue
                
                # 计算匹配分数
                score = self._calculate_match_score(text_word, word_text)
                score = score - (offset * 0.05)  # ✅ 降低位置惩罚（从0.1到0.05）
                
                if score > best_score:
                    best_score = score
                    best_match = word_idx + offset
            
            # ✅ 降低匹配阈值（从 0.5 到 0.3），更容易接受匹配
            # 如果是放宽模式，进一步降低阈值
            threshold = 0.2 if relax else 0.3
            if best_score > threshold:
                matched_indices.append(best_match)
                word_idx = best_match + 1
                text_idx += 1
                consecutive_misses = 0
            else:
                # 未找到匹配，可能是 Whisper 缺失的词
                text_idx += 1
                consecutive_misses += 1
                
                # ✅ 智能推进：连续多次未匹配时，适度推进 word_idx
                if consecutive_misses >= 2:
                    word_idx = min(word_idx + 1, len(words) - 1)
                    consecutive_misses = 0
        
        # ✅ 放宽要求：只要匹配了至少1个词就返回结果
        if len(matched_indices) < 1:
            return None
        
        # 获取匹配到的单词的时间戳
        matched_words = [words[i] for i in matched_indices]
        start_time = matched_words[0]['start']
        end_time = matched_words[-1]['end']
        
        # 🔧 时间戳插值估算（处理 Whisper 漏识别的词）
        match_ratio = len(matched_indices) / len(text_words)
        if match_ratio < 0.5:
            # 匹配率低于50%，可能有很多缺失词
            # 使用更保守的时间范围估算
            if len(matched_indices) >= 2:
                # 基于匹配词的密度估算总时长
                avg_word_duration = (end_time - start_time) / len(matched_indices)
                estimated_duration = avg_word_duration * len(text_words)
                
                # 调整结束时间
                end_time = start_time + estimated_duration
            else:
                # 只有一个匹配词，使用默认估算
                avg_duration_per_word = 0.3  # 假设每词0.3秒
                end_time = start_time + (len(text_words) * avg_duration_per_word)
        
        return {
            'start': start_time,
            'end': end_time,
            'next_idx': word_idx,
            'match_ratio': match_ratio  # 用于调试
        }
    
    def _calculate_match_score(self, text_word, whisper_word):
        """计算两个词的匹配分数（改进版：更智能的相似度判断）"""
        if not text_word or not whisper_word:
            return 0.0
        
        # 完全匹配
        if text_word == whisper_word:
            return 1.0
        
        # 一个包含另一个
        if text_word in whisper_word or whisper_word in text_word:
            shorter = min(len(text_word), len(whisper_word))
            longer = max(len(text_word), len(whisper_word))
            return shorter / longer * 0.9
        
        # 使用编辑距离
        distance = self._levenshtein_distance(text_word, whisper_word)
        max_len = max(len(text_word), len(whisper_word))
        
        if max_len == 0:
            return 0.0
        
        # 计算基于编辑距离的相似度
        edit_similarity = 1.0 - (distance / max_len)
        
        # 使用 SequenceMatcher 计算序列相似度
        seq_similarity = difflib.SequenceMatcher(None, text_word, whisper_word).ratio()
        
        # 取两者的最大值（更宽松的匹配策略）
        final_similarity = max(edit_similarity, seq_similarity)
        
        # 🔧 关键改进：根据词长调整容忍度
        if max_len <= 3:
            # 短词：要求至少 50% 相似度
            threshold = 0.5
        elif max_len <= 6:
            # 中等长度词：要求至少 40% 相似度
            threshold = 0.4
        else:
            # 长词：要求至少 30% 相似度，并给予编辑距离优惠
            threshold = 0.3
            # 对于长词，如果编辑距离 <= 3，给予额外奖励
            if distance <= 3:
                final_similarity = max(final_similarity, 0.7)
        
        return final_similarity if final_similarity >= threshold else 0.0
    
    def _levenshtein_distance(self, s1, s2):
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _validate_and_adjust_timestamps(self, subtitles):
        """验证和调整时间戳"""
        if not subtitles:
            return []
        
        validated = []
        
        for i, sub in enumerate(subtitles):
            # 确保时间戳合法
            if sub['start'] >= sub['end']:
                sub['end'] = sub['start'] + 1.0
            
            # 确保不与前一条重叠
            if i > 0 and sub['start'] < validated[-1]['end']:
                sub['start'] = validated[-1]['end'] + 0.01
                if sub['start'] >= sub['end']:
                    sub['end'] = sub['start'] + 1.0
            
            # 检查持续时间是否合理
            duration = sub['end'] - sub['start']
            if duration > self.max_duration * 2:
                sub['end'] = sub['start'] + self.max_duration * 1.5
            elif duration < 0.5:
                sub['end'] = sub['start'] + 0.5
            
            validated.append(sub)
        
        return validated
    
    def fallback_split(self, words):
        """规则引擎回退（当LLM失败时）"""
        self.progress.emit('   🔄 使用规则引擎断句...')
        
        if not words or len(words) == 0:
            self.progress.emit('   ⚠️  词列表为空，无法断句')
            return []
        
        try:
            subtitles = []
            current_words = []
            current_start = words[0]['start']
            
            sentence_ends = {'.', '!', '?', '。', '！', '？'}
            
            for i, word in enumerate(words):
                current_words.append(word)
                duration = word['end'] - current_start
                word_text = word['word'].strip()
                
                should_split = False
                
                # 句子结束
                if word_text and word_text[-1] in sentence_ends:
                    should_split = True
                # 超限制
                elif duration >= self.max_duration or len(current_words) >= self.max_words:
                    should_split = True
                
                if should_split and current_words:
                    subtitle = {
                        'start': current_start,
                        'end': current_words[-1]['end'],
                        'text': ''.join([w['word'] for w in current_words]).strip(),
                    }
                    subtitles.append(subtitle)
                    current_words = []
                    if i + 1 < len(words):
                        current_start = words[i + 1]['start']
            
            # 处理剩余的词
            if current_words:
                subtitle = {
                    'start': current_start,
                    'end': current_words[-1]['end'],
                    'text': ''.join([w['word'] for w in current_words]).strip(),
                }
                subtitles.append(subtitle)
            
            self.progress.emit(f'   ✅ 规则引擎生成 {len(subtitles)} 条字幕')
            return subtitles
            
        except Exception as e:
            self.progress.emit(f'   ❌ 规则引擎失败: {str(e)}')
            import traceback
            self.progress.emit(f'   详细错误: {traceback.format_exc()}')
            return []
    
    # ========== SRT 文件处理方法 ==========
    
    def parse_srt(self, srt_file):
        """解析 SRT 文件"""
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            try:
                with open(srt_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
            except:
                return []
        
        pattern = r'(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n((?:.*\n)*?)(?:\n|$)'
        matches = re.findall(pattern, content)
        
        subtitles = []
        for match in matches:
            start_time = self.parse_timestamp(match[1])
            end_time = self.parse_timestamp(match[2])
            text = match[3].strip()
            
            if text:
                subtitles.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
        
        return subtitles
    
    def parse_timestamp(self, timestamp_str):
        """将 SRT 时间戳转换为秒"""
        match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp_str)
        if match:
            h, m, s, ms = map(int, match.groups())
            return h * 3600 + m * 60 + s + ms / 1000.0
        return 0.0
    
    def map_timestamps(self, new_segments, original_subtitles):
        """将新分段映射到原始字幕的时间戳（简单映射）"""
        new_subtitles = []
        
        # 构建原始文本
        original_text = ' '.join([sub['text'] for sub in original_subtitles])
        
        # 为每个新分段找到在原始文本中的位置
        current_pos = 0
        
        for segment_text in new_segments:
            segment_lower = segment_text.lower().strip()
            original_lower = original_text[current_pos:].lower()
            
            # 查找最接近的匹配
            pos = original_lower.find(segment_lower[:min(20, len(segment_lower))])
            if pos == -1:
                continue
            
            actual_pos = current_pos + pos
            
            # 找到对应的时间戳范围
            char_count = 0
            start_time = None
            end_time = None
            
            for sub in original_subtitles:
                sub_text = sub['text']
                if start_time is None and char_count + len(sub_text) >= actual_pos:
                    start_time = sub['start']
                
                char_count += len(sub_text) + 1
                
                if char_count >= actual_pos + len(segment_text):
                    end_time = sub['end']
                    break
            
            if start_time and end_time:
                new_subtitles.append({
                    'start': start_time,
                    'end': end_time,
                    'text': segment_text
                })
                current_pos = actual_pos + len(segment_text)
        
        return new_subtitles
    
    def save_srt(self, subtitles):
        """保存为 SRT 格式"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                f.write(f"{i}\n")
                f.write(f"{self.format_timestamp(sub['start'])} --> {self.format_timestamp(sub['end'])}\n")
                f.write(f"{sub['text']}\n")
                f.write("\n")
    
    def format_timestamp(self, seconds):
        """转换为 SRT 时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

