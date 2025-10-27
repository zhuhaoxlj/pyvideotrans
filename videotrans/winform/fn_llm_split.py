# LLM智能字幕断句优化 - 基于语义理解
def openwin():
    import json
    from pathlib import Path

    from PySide6.QtCore import QThread, Signal, QUrl
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtWidgets import QFileDialog

    from videotrans.configure import config
    from videotrans.util import tools
    
    RESULT_DIR = config.HOME_DIR + "/SmartSplit"
    Path(RESULT_DIR).mkdir(exist_ok=True)
    
    # 缓存目录
    CACHE_DIR = Path(config.HOME_DIR) / "whisper_cache"
    CACHE_DIR.mkdir(exist_ok=True)

    class LLMSplitThread(QThread):
        uito = Signal(str)

        def __init__(self, *, parent=None, video_file=None, language='en', model_size='large-v3-turbo', 
                     max_duration=5.0, max_words=15, device='cpu', existing_srt=None,
                     llm_provider='openai', llm_api_key='', llm_model='gpt-4o-mini', llm_base_url=''):
            super().__init__(parent=parent)
            self.video_file = video_file
            self.language = language
            self.model_size = model_size
            self.max_duration = max_duration
            self.max_words = max_words
            self.device = device
            self.existing_srt = existing_srt
            
            # LLM 配置
            self.llm_provider = llm_provider
            self.llm_api_key = llm_api_key
            self.llm_model = llm_model
            self.llm_base_url = llm_base_url
            
            suffix = '_llm_resplit.srt' if existing_srt else '_llm_smart.srt'
            self.result_file = RESULT_DIR + "/" + Path(video_file).stem + suffix

        def post(self, type='logs', text=""):
            self.uito.emit(json.dumps({"type": type, "text": text}))
        
        def get_file_hash(self, filepath):
            """计算文件的哈希值"""
            import hashlib
            
            hash_obj = hashlib.sha256()
            try:
                with open(filepath, 'rb') as f:
                    # 分块读取，避免大文件占用过多内存
                    for chunk in iter(lambda: f.read(8192), b''):
                        hash_obj.update(chunk)
                return hash_obj.hexdigest()
            except Exception as e:
                self.post(type='logs', text=f'⚠️ 计算哈希值失败: {str(e)}')
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
            import pickle
            
            if not cache_key:
                return
            
            cache_file = CACHE_DIR / f"{cache_key}.pkl"
            try:
                cache_data = {
                    'all_words': all_words,
                    'language': language,
                    'timestamp': __import__('time').time()
                }
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
                self.post(type='logs', text=f'💾 缓存已保存: {cache_file.name}')
            except Exception as e:
                self.post(type='logs', text=f'⚠️ 保存缓存失败: {str(e)}')
        
        def load_cache(self, cache_key):
            """加载缓存"""
            import pickle
            
            if not cache_key:
                return None
            
            cache_file = CACHE_DIR / f"{cache_key}.pkl"
            if not cache_file.exists():
                return None
            
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                return cache_data
            except Exception as e:
                self.post(type='logs', text=f'⚠️ 读取缓存失败: {str(e)}')
                return None

        def run(self):
            try:
                if self.existing_srt:
                    self.post(type='logs', text='🤖 模式: LLM智能重新分割现有字幕')
                    self.process_with_existing_srt()
                else:
                    self.post(type='logs', text='🤖 模式: LLM智能生成新字幕')
                    self.process_new_transcription()
                
            except Exception as e:
                import traceback
                self.post(type='error', text=str(e) + "\n" + traceback.format_exc())
        
        def process_new_transcription(self):
            """从视频生成新字幕 + LLM优化"""
            # 检查缓存
            self.post(type='logs', text='🔍 检查缓存...')
            cache_key = self.get_cache_key(self.video_file)
            cached_data = self.load_cache(cache_key)
            
            if cached_data:
                self.post(type='logs', text='✅ 找到缓存！直接使用缓存数据')
                all_words = cached_data['all_words']
                detected_language = cached_data['language']
                self.post(type='logs', text=f'📊 从缓存加载: {len(all_words)} 个词')
                self.post(type='logs', text=f'🌐 检测语言: {detected_language}')
            else:
                self.post(type='logs', text='❌ 未找到缓存，开始 Whisper 处理...')
                self.post(type='logs', text='🔧 加载 Faster-Whisper 模型...')
                
                try:
                    from faster_whisper import WhisperModel
                except ImportError:
                    self.post(type='error', text='未安装 faster-whisper\n请运行: pip install faster-whisper')
                    return
                
                self.post(type='logs', text=f'📥 模型: {self.model_size}')
                
                # 设备信息
                device_name = {
                    'cpu': 'CPU',
                    'cuda': 'CUDA (NVIDIA GPU)',
                    'mps': 'MPS (Apple Silicon GPU)'
                }.get(self.device, self.device.upper())
                self.post(type='logs', text=f'⚙️  设备: {device_name}')
                
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
                        download_root=config.ROOT_DIR + "/models"
                    )
                except ValueError as e:
                    if 'unsupported device' in str(e).lower() and self.device == 'mps':
                        self.post(type='logs', text='⚠️  faster-whisper 暂不支持 MPS')
                        self.post(type='logs', text='📥 回退到 CPU 模式...')
                        self.device = 'cpu'
                        compute_type = 'int8'
                        model = WhisperModel(
                            self.model_size,
                            device='cpu',
                            compute_type='int8',
                            download_root=config.ROOT_DIR + "/models"
                        )
                    else:
                        raise
                
                self.post(type='logs', text=f'🎤 开始识别语音...')
                self.post(type='logs', text='⏳ 此过程可能需要几分钟，请耐心等待...')
                
                # 转录音频
                import time
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
                
                self.post(type='logs', text=f'✅ 识别完成！检测语言: {info.language} (耗时: {transcribe_time:.1f}秒)')
                self.post(type='logs', text='📊 收集词级时间戳...')
                
                # 收集所有词
                all_words = []
                segment_count = 0
                for segment in segments:
                    segment_count += 1
                    if segment_count % 10 == 0:
                        self.post(type='logs', text=f'   处理片段: {segment_count}...')
                    
                    if hasattr(segment, 'words') and segment.words:
                        for word in segment.words:
                            all_words.append({
                                'word': word.word,
                                'start': word.start,
                                'end': word.end
                            })
                
                if not all_words:
                    self.post(type='error', text='未检测到任何语音内容')
                    return
                
                self.post(type='logs', text=f'✅ 收集完成！共 {len(all_words)} 个词')
                
                # 保存缓存
                detected_language = info.language
                self.save_cache(cache_key, all_words, detected_language)
            
            # 使用 LLM 进行智能断句
            self.post(type='logs', text='🤖 使用 LLM 进行智能断句优化...')
            subtitles = self.llm_smart_split(all_words, detected_language)
            
            if not subtitles:
                self.post(type='error', text='LLM 断句失败')
                return
            
            self.post(type='logs', text=f'✅ 生成 {len(subtitles)} 条字幕')
            
            # 保存
            self.save_srt(subtitles)
            
            self.post(type='logs', text='💾 保存完成')
            self.post(type='ok', text=self.result_file)
        
        def process_with_existing_srt(self):
            """使用现有字幕 + LLM重新分割"""
            import time
            import re
            
            self.post(type='logs', text=f'📖 读取现有字幕: {Path(self.existing_srt).name}')
            
            # 读取现有字幕
            original_subtitles = self.parse_srt(self.existing_srt)
            if not original_subtitles:
                self.post(type='error', text='无法解析字幕文件')
                return
            
            self.post(type='logs', text=f'✅ 读取到 {len(original_subtitles)} 条原始字幕')
            
            # 提取完整文本
            original_text = ' '.join([sub['text'] for sub in original_subtitles])
            self.post(type='logs', text=f'📝 原始文本长度: {len(original_text)} 字符')
            
            # 检查缓存（包括视频和字幕文件）
            self.post(type='logs', text='🔍 检查缓存...')
            cache_key = self.get_cache_key(self.video_file, self.existing_srt)
            cached_data = self.load_cache(cache_key)
            
            if cached_data:
                self.post(type='logs', text='✅ 找到缓存！直接使用缓存数据')
                all_words = cached_data['all_words']
                detected_language = cached_data['language']
                self.post(type='logs', text=f'📊 从缓存加载: {len(all_words)} 个词')
                self.post(type='logs', text=f'🌐 检测语言: {detected_language}')
            else:
                self.post(type='logs', text='❌ 未找到缓存，开始 Whisper 处理...')
                
                # 使用 Whisper 获取词级时间戳
                self.post(type='logs', text='🔧 加载 Faster-Whisper 模型...')
                
                try:
                    from faster_whisper import WhisperModel
                except ImportError:
                    self.post(type='error', text='未安装 faster-whisper\n请运行: pip install faster-whisper')
                    return
                
                self.post(type='logs', text=f'📥 模型: {self.model_size}')
                
                # 设备信息
                device_name = {
                    'cpu': 'CPU',
                    'cuda': 'CUDA (NVIDIA GPU)',
                    'mps': 'MPS (Apple Silicon GPU)'
                }.get(self.device, self.device.upper())
                self.post(type='logs', text=f'⚙️  设备: {device_name}')
                
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
                        download_root=config.ROOT_DIR + "/models"
                    )
                except ValueError as e:
                    if 'unsupported device' in str(e).lower() and self.device == 'mps':
                        self.post(type='logs', text='⚠️  faster-whisper 暂不支持 MPS')
                        self.post(type='logs', text='📥 回退到 CPU 模式...')
                        self.device = 'cpu'
                        compute_type = 'int8'
                        model = WhisperModel(
                            self.model_size,
                            device='cpu',
                            compute_type='int8',
                            download_root=config.ROOT_DIR + "/models"
                        )
                    else:
                        raise
                
                self.post(type='logs', text=f'🎤 开始识别语音（获取词级时间戳）...')
                
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
                
                self.post(type='logs', text=f'✅ 识别完成！检测语言: {info.language} (耗时: {transcribe_time:.1f}秒)')
                self.post(type='logs', text='📊 收集词级时间戳...')
                
                # 收集所有词
                all_words = []
                segment_count = 0
                word_count = 0
                for segment in segments:
                    segment_count += 1
                    if segment_count % 10 == 0:
                        self.post(type='logs', text=f'   处理片段: {segment_count}... (已收集 {word_count} 个词)')
                    
                    if hasattr(segment, 'words') and segment.words:
                        for word in segment.words:
                            all_words.append({
                                'word': word.word,
                                'start': word.start,
                                'end': word.end
                            })
                            word_count += 1
                
                if not all_words:
                    self.post(type='error', text='未检测到任何语音内容')
                    return
                
                self.post(type='logs', text=f'✅ 收集完成！共处理 {segment_count} 个片段，{len(all_words)} 个词')
                
                # 保存缓存
                detected_language = info.language
                self.save_cache(cache_key, all_words, detected_language)
            
            # 使用 LLM 进行智能断句（使用原始文本）
            self.post(type='logs', text='🤖 使用 LLM 进行智能断句优化...')
            subtitles = self.llm_smart_split(all_words, detected_language, original_text=original_text)
            
            if not subtitles:
                self.post(type='error', text='LLM 断句失败')
                return
            
            self.post(type='logs', text=f'📊 原始字幕: {len(original_subtitles)} 条 → 新字幕: {len(subtitles)} 条')
            
            # 保存
            self.save_srt(subtitles)
            
            self.post(type='logs', text='💾 保存完成')
            self.post(type='ok', text=self.result_file)
        
        def llm_smart_split(self, words, detected_language, original_text=None):
            """使用 LLM 进行智能断句"""
            import time
            
            if not words:
                return []
            
            # 构建词列表的文本表示
            words_with_index = []
            for i, w in enumerate(words):
                words_with_index.append(f"[{i}]{w['word']}")
            
            words_text = ''.join(words_with_index)
            
            # 如果有原始文本，使用原始文本；否则使用识别的文本
            reference_text = original_text if original_text else ''.join([w['word'] for w in words])
            
            # 构建 prompt
            prompt = self._build_llm_prompt(reference_text, len(words), detected_language)
            
            self.post(type='logs', text=f'   LLM提供商: {self.llm_provider}')
            self.post(type='logs', text=f'   LLM模型: {self.llm_model}')
            self.post(type='logs', text=f'   处理文本: {len(words)} 词')
            self.post(type='logs', text='   ⏳ 正在调用 LLM API，请稍候...')
            
            # 调用 LLM（支持流式传输）
            start_time = time.time()
            try:
                self.post(type='logs', text='   📡 LLM 响应流:')
                response = self._call_llm_stream(prompt, words_text)
                llm_time = time.time() - start_time
                self.post(type='logs', text=f'\n   ✅ LLM响应完成 (耗时: {llm_time:.1f}秒)')
            except Exception as e:
                self.post(type='logs', text=f'   ⚠️  LLM调用失败: {str(e)}')
                self.post(type='logs', text='   回退到规则引擎断句')
                return self.fallback_split(words)
            
            # 解析 LLM 返回的断句结果
            self.post(type='logs', text='   📋 解析 LLM 返回结果...')
            subtitles = self._parse_llm_response(response, words)
            
            if not subtitles:
                self.post(type='logs', text='   ⚠️  LLM返回格式错误，回退到规则引擎')
                return self.fallback_split(words)
            
            self.post(type='logs', text=f'   ✅ 解析完成，生成 {len(subtitles)} 条字幕')
            
            # 验证和调整时间戳
            self.post(type='logs', text='   🔧 验证和调整时间戳...')
            subtitles = self._validate_and_adjust_timestamps(subtitles)
            
            self.post(type='logs', text='   ✅ 时间戳调整完成')
            
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
        
        def _call_llm_stream(self, prompt, words_text):
            """调用 LLM API（流式传输）"""
            import requests
            import json
            
            if self.llm_provider == 'openai':
                return self._stream_openai(prompt)
            elif self.llm_provider == 'anthropic':
                return self._stream_anthropic(prompt)
            elif self.llm_provider == 'deepseek':
                return self._stream_deepseek(prompt)
            elif self.llm_provider == 'siliconflow':
                return self._stream_siliconflow(prompt)
            elif self.llm_provider == 'local':
                return self._stream_local_llm(prompt)
            else:
                raise ValueError(f'不支持的 LLM 提供商: {self.llm_provider}')
        
        def _call_llm(self, prompt, words_text):
            """调用 LLM API（非流式，备用）"""
            import requests
            
            if self.llm_provider == 'openai':
                return self._call_openai(prompt)
            elif self.llm_provider == 'anthropic':
                return self._call_anthropic(prompt)
            elif self.llm_provider == 'deepseek':
                return self._call_deepseek(prompt)
            elif self.llm_provider == 'siliconflow':
                return self._call_siliconflow(prompt)
            elif self.llm_provider == 'local':
                return self._call_local_llm(prompt)
            else:
                raise ValueError(f'不支持的 LLM 提供商: {self.llm_provider}')
        
        def _call_openai(self, prompt):
            """调用 OpenAI API"""
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
                'response_format': {'type': 'json_object'} if 'gpt-4' in self.llm_model else None
            }
            
            # 移除 None 值
            data = {k: v for k, v in data.items() if v is not None}
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        
        def _call_anthropic(self, prompt):
            """调用 Anthropic Claude API"""
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
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['content'][0]['text']
        
        def _call_deepseek(self, prompt):
            """调用 DeepSeek API"""
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
                'temperature': 0.3
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        
        def _call_siliconflow(self, prompt):
            """调用 SiliconFlow API"""
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
                'temperature': 0.3
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        
        def _call_local_llm(self, prompt):
            """调用本地 LLM (Ollama 等)"""
            import requests
            
            url = self.llm_base_url if self.llm_base_url else 'http://localhost:11434/api/generate'
            
            data = {
                'model': self.llm_model,
                'prompt': prompt,
                'stream': False
            }
            
            response = requests.post(url, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
        
        # ==================== 流式传输方法 ====================
        
        def _stream_siliconflow(self, prompt):
            """调用 SiliconFlow API (流式传输)"""
            import requests
            import json
            
            url = 'https://api.siliconflow.cn/v1/chat/completions'
            
            headers = {
                'Authorization': f'Bearer {self.llm_api_key}',
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            }
            
            data = {
                'model': self.llm_model if self.llm_model else 'Qwen/Qwen2.5-7B-Instruct',
                'messages': [
                    {'role': 'system', 'content': 'You are an expert subtitle editor.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'stream': True  # 启用流式传输
            }
            
            response = requests.post(url, headers=headers, json=data, stream=True, timeout=120)
            response.raise_for_status()
            
            full_content = []
            buffer = ""
            
            try:
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 "data: " 前缀
                        
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_content.append(content)
                                    buffer += content
                                    
                                    # 实时显示流式内容
                                    self.post(type='stream', text=content)
                        except json.JSONDecodeError:
                            continue
            
            except Exception as e:
                self.post(type='logs', text=f'\n   ⚠️  流式传输异常: {str(e)}')
            
            return ''.join(full_content)
        
        def _stream_openai(self, prompt):
            """调用 OpenAI API (流式传输)"""
            import requests
            import json
            
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
                                self.post(type='stream', text=content)
                    except json.JSONDecodeError:
                        continue
            
            return ''.join(full_content)
        
        def _stream_deepseek(self, prompt):
            """调用 DeepSeek API (流式传输)"""
            import requests
            import json
            
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
                                self.post(type='stream', text=content)
                    except json.JSONDecodeError:
                        continue
            
            return ''.join(full_content)
        
        def _stream_anthropic(self, prompt):
            """调用 Anthropic Claude API (流式传输)"""
            import requests
            import json
            
            url = 'https://api.anthropic.com/v1/messages'
            
            headers = {
                'x-api-key': self.llm_api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.llm_model,
                'max_tokens': 4096,
                'messages': [
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
                    
                    try:
                        chunk = json.loads(data_str)
                        if chunk.get('type') == 'content_block_delta':
                            delta = chunk.get('delta', {})
                            content = delta.get('text', '')
                            if content:
                                full_content.append(content)
                                self.post(type='stream', text=content)
                    except json.JSONDecodeError:
                        continue
            
            return ''.join(full_content)
        
        def _stream_local_llm(self, prompt):
            """调用本地 LLM (Ollama 等，流式传输)"""
            import requests
            import json
            
            url = self.llm_base_url if self.llm_base_url else 'http://localhost:11434/api/generate'
            
            data = {
                'model': self.llm_model,
                'prompt': prompt,
                'stream': True
            }
            
            response = requests.post(url, json=data, stream=True, timeout=120)
            response.raise_for_status()
            
            full_content = []
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                try:
                    chunk = json.loads(line)
                    content = chunk.get('response', '')
                    if content:
                        full_content.append(content)
                        self.post(type='stream', text=content)
                    
                    if chunk.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue
            
            return ''.join(full_content)
        
        # ==================== 解析和验证方法 ====================
        
        def _parse_llm_response(self, response, words):
            """解析 LLM 返回的结果"""
            import json
            import re
            
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
            
            for segment in segments:
                if not isinstance(segment, dict) or 'text' not in segment:
                    continue
                
                segment_text = segment['text'].strip()
                if not segment_text:
                    continue
                
                # 在词列表中查找这段文本
                segment_words = []
                search_text = segment_text.lower().replace(',', '').replace('.', '').replace('!', '').replace('?', '')
                search_words = search_text.split()
                
                # 简单的词匹配策略
                matched_words = []
                temp_idx = word_idx
                
                for search_word in search_words:
                    # 在当前位置附近查找匹配的词
                    for offset in range(min(10, len(words) - temp_idx)):
                        if temp_idx + offset >= len(words):
                            break
                        
                        word_text = words[temp_idx + offset]['word'].lower().strip()
                        word_clean = word_text.replace(',', '').replace('.', '').replace('!', '').replace('?', '').strip()
                        
                        if search_word in word_clean or word_clean in search_word:
                            matched_words.append(words[temp_idx + offset])
                            temp_idx = temp_idx + offset + 1
                            break
                
                if matched_words:
                    subtitle = {
                        'start': matched_words[0]['start'],
                        'end': matched_words[-1]['end'],
                        'text': segment_text
                    }
                    subtitles.append(subtitle)
                    word_idx = temp_idx
            
            return subtitles
        
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
                    # 如果太长，截断
                    sub['end'] = sub['start'] + self.max_duration * 1.5
                elif duration < 0.5:
                    # 如果太短，延长
                    sub['end'] = sub['start'] + 0.5
                
                validated.append(sub)
            
            return validated
        
        def fallback_split(self, words):
            """回退到规则引擎断句（当LLM失败时）"""
            self.post(type='logs', text='   🔄 使用规则引擎断句...')
            
            # 检查输入
            if not words or len(words) == 0:
                self.post(type='logs', text='   ⚠️  词列表为空，无法断句')
                return []
            
            try:
                # 使用简化的规则引擎
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
                
                self.post(type='logs', text=f'   ✅ 规则引擎生成 {len(subtitles)} 条字幕')
                return subtitles
                
            except Exception as e:
                self.post(type='logs', text=f'   ❌ 规则引擎失败: {str(e)}')
                import traceback
                self.post(type='logs', text=f'   详细错误: {traceback.format_exc()}')
                return []
        
        def parse_srt(self, srt_file):
            """解析 SRT 文件"""
            import re
            
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
            import re
            match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp_str)
            if match:
                h, m, s, ms = map(int, match.groups())
                return h * 3600 + m * 60 + s + ms / 1000.0
            return 0.0
        
        def save_srt(self, subtitles):
            """保存为SRT格式"""
            with open(self.result_file, 'w', encoding='utf-8') as f:
                for i, sub in enumerate(subtitles, 1):
                    f.write(f"{i}\n")
                    f.write(f"{self.format_timestamp(sub['start'])} --> {self.format_timestamp(sub['end'])}\n")
                    f.write(f"{sub['text']}\n")
                    f.write("\n")
        
        def format_timestamp(self, seconds):
            """转换为SRT时间格式"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            milliseconds = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def feed(d):
        if winobj.has_done:
            return
        d = json.loads(d)
        if d['type'] == "error":
            winobj.has_done = True
            winobj.loglabel.setPlainText(d['text'])
            # 自动滚动到底部
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )
            tools.show_error(d['text'])
            winobj.startbtn.setText('开始生成' if config.defaulelang == 'zh' else 'Start Generate')
            winobj.startbtn.setDisabled(False)
        elif d['type'] == 'logs':
            current_text = winobj.loglabel.toPlainText()
            winobj.loglabel.setPlainText(current_text + '\n' + d['text'])
            # 自动滚动到底部
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )
        elif d['type'] == 'stream':
            # 流式内容：追加到当前行末尾，不换行
            current_text = winobj.loglabel.toPlainText()
            winobj.loglabel.setPlainText(current_text + d['text'])
            # 自动滚动到底部
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )
        else:
            winobj.has_done = True
            winobj.startbtn.setText('开始生成' if config.defaulelang == 'zh' else 'Start Generate')
            winobj.startbtn.setDisabled(False)
            winobj.resultlabel.setText(d['text'])
            winobj.resultbtn.setDisabled(False)
            winobj.resultinput.setPlainText(Path(winobj.resultlabel.text()).read_text(encoding='utf-8'))
            winobj.loglabel.setPlainText(winobj.loglabel.toPlainText() + '\n\n✅ 生成完成！')
            # 自动滚动到底部
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )

    def toggle_srt_input():
        """切换字幕文件输入框的显示"""
        is_checked = winobj.use_existing_srt_checkbox.isChecked()
        winobj.srtbtn.setVisible(is_checked)
        winobj.srtinput.setVisible(is_checked)
        if not is_checked:
            winobj.srtinput.setText("未选择字幕文件" if config.defaulelang == 'zh' else 'No subtitle file selected')
    
    def toggle_llm_settings():
        """切换 LLM 设置的显示"""
        is_checked = winobj.use_llm_checkbox.isChecked()
        # 显示/隐藏 LLM 配置
        winobj.llm_provider_combo.setVisible(is_checked)
        winobj.llm_provider_label.setVisible(is_checked)
        winobj.llm_api_key_input.setVisible(is_checked)
        winobj.llm_api_key_label.setVisible(is_checked)
        winobj.llm_model_combo.setVisible(is_checked)
        winobj.llm_model_label.setVisible(is_checked)
        winobj.llm_base_url_input.setVisible(is_checked)
        winobj.llm_base_url_label.setVisible(is_checked)
        winobj.llm_test_btn.setVisible(is_checked)
        
        # 勾选 LLM 时，隐藏最大持续时间和最大词数（LLM 会自动优化）
        # 不勾选时显示这些参数（规则引擎需要）
        winobj.duration_input.setVisible(not is_checked)
        winobj.duration_label.setVisible(not is_checked)
        winobj.words_input.setVisible(not is_checked)
        winobj.words_label.setVisible(not is_checked)
    
    def save_api_key_to_env():
        """保存 API Key 到 .env 文件"""
        import os
        api_key = winobj.llm_api_key_input.text().strip()
        if not api_key:
            return
        
        env_file = os.path.join(config.ROOT_DIR, '.env')
        
        # 读取现有的 .env 文件内容
        lines = []
        key_exists = False
        
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 查找并更新 SILICONFLOW_API_KEY
                for i, line in enumerate(lines):
                    if line.strip().startswith('SILICONFLOW_API_KEY='):
                        lines[i] = f'SILICONFLOW_API_KEY={api_key}\n'
                        key_exists = True
                        break
            except Exception as e:
                print(f"读取 .env 文件失败: {e}")
        
        # 如果 key 不存在，添加到文件末尾
        if not key_exists:
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            lines.append(f'SILICONFLOW_API_KEY={api_key}\n')
        
        # 写回文件
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"API Key 已保存到 {env_file}")
        except Exception as e:
            print(f"保存 API Key 失败: {e}")
    
    class TestLLMThread(QThread):
        """异步测试LLM连接的线程"""
        finished = Signal(str, bool)  # 信号：(消息, 是否成功)
        progress = Signal(str)  # 进度信号
        
        def __init__(self, provider, api_key, model, base_url):
            super().__init__()
            self.provider = provider
            self.api_key = api_key
            self.model = model
            self.base_url = base_url
        
        def run(self):
            try:
                import requests
                
                # 发送进度更新
                self.progress.emit('⏳ 正在构建测试请求...' if config.defaulelang == 'zh' else '⏳ Building test request...')
                
                # 构建测试请求
                test_prompt = "请回复'OK'，这是一个连接测试。" if config.defaulelang == 'zh' else "Reply 'OK', this is a connection test."
                
                if self.provider == 'openai':
                    url = self.base_url if self.base_url else 'https://api.openai.com/v1/chat/completions'
                    headers = {
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    }
                    data = {
                        'model': self.model,
                        'messages': [{'role': 'user', 'content': test_prompt}],
                        'max_tokens': 10
                    }
                
                elif self.provider == 'anthropic':
                    url = 'https://api.anthropic.com/v1/messages'
                    headers = {
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                        'Content-Type': 'application/json'
                    }
                    data = {
                        'model': self.model,
                        'max_tokens': 10,
                        'messages': [{'role': 'user', 'content': test_prompt}]
                    }
                
                elif self.provider == 'deepseek':
                    url = 'https://api.deepseek.com/v1/chat/completions'
                    headers = {
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    }
                    data = {
                        'model': self.model,
                        'messages': [{'role': 'user', 'content': test_prompt}],
                        'max_tokens': 10
                    }
                
                elif self.provider == 'siliconflow':
                    url = self.base_url if self.base_url else 'https://api.siliconflow.cn/v1/chat/completions'
                    headers = {
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    }
                    data = {
                        'model': self.model,
                        'messages': [{'role': 'user', 'content': test_prompt}],
                        'max_tokens': 10
                    }
                
                elif self.provider == 'local':
                    url = self.base_url if self.base_url else 'http://localhost:11434/api/generate'
                    data = {
                        'model': self.model,
                        'prompt': test_prompt,
                        'stream': False
                    }
                    headers = {}
                
                else:
                    self.finished.emit(
                        f'不支持的提供商: {self.provider}' if config.defaulelang == 'zh' else f'Unsupported provider: {self.provider}',
                        False
                    )
                    return
                
                # 发送进度更新
                self.progress.emit('📡 正在连接服务器...' if config.defaulelang == 'zh' else '📡 Connecting to server...')
                
                # 发送测试请求
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                # 发送进度更新
                self.progress.emit('📥 正在解析响应...' if config.defaulelang == 'zh' else '📥 Parsing response...')
                
                # 检查响应
                if response.status_code == 200:
                    result = response.json()
                    # 验证响应格式
                    if self.provider in ['openai', 'deepseek', 'siliconflow']:
                        if 'choices' in result and len(result['choices']) > 0:
                            success_msg = f'✅ 连接成功！提供商: {self.provider} | 模型: {self.model} | 响应正常' if config.defaulelang == 'zh' else f'✅ Connection Successful! Provider: {self.provider} | Model: {self.model} | Response OK'
                            self.finished.emit(success_msg, True)
                        else:
                            self.finished.emit('响应格式不正确' if config.defaulelang == 'zh' else 'Invalid response format', False)
                    
                    elif self.provider == 'anthropic':
                        if 'content' in result:
                            success_msg = f'✅ 连接成功！提供商: {self.provider} | 模型: {self.model} | 响应正常' if config.defaulelang == 'zh' else f'✅ Connection Successful! Provider: {self.provider} | Model: {self.model} | Response OK'
                            self.finished.emit(success_msg, True)
                        else:
                            self.finished.emit('响应格式不正确' if config.defaulelang == 'zh' else 'Invalid response format', False)
                    
                    elif self.provider == 'local':
                        if 'response' in result:
                            success_msg = f'✅ 连接成功！提供商: {self.provider} | 模型: {self.model} | 响应正常' if config.defaulelang == 'zh' else f'✅ Connection Successful! Provider: {self.provider} | Model: {self.model} | Response OK'
                            self.finished.emit(success_msg, True)
                        else:
                            self.finished.emit('响应格式不正确' if config.defaulelang == 'zh' else 'Invalid response format', False)
                else:
                    error_msg = f'❌ 连接失败！HTTP {response.status_code}: {response.text[:200]}' if config.defaulelang == 'zh' else f'❌ Connection Failed! HTTP {response.status_code}: {response.text[:200]}'
                    self.finished.emit(error_msg, False)
            
            except requests.exceptions.Timeout:
                self.finished.emit(
                    '❌ 连接超时！请检查网络连接' if config.defaulelang == 'zh' else '❌ Connection Timeout! Please check network connection',
                    False
                )
            
            except requests.exceptions.ConnectionError:
                self.finished.emit(
                    '❌ 无法连接到服务器！请检查网络或 Base URL' if config.defaulelang == 'zh' else '❌ Cannot connect to server! Please check network or Base URL',
                    False
                )
            
            except Exception as e:
                error_msg = f'❌ 测试失败！{str(e)}' if config.defaulelang == 'zh' else f'❌ Test Failed! {str(e)}'
                self.finished.emit(error_msg, False)
    
    def test_llm_connection():
        """测试 LLM 连接是否正常（异步）"""
        # 获取配置
        provider = winobj.llm_provider_combo.currentText().lower()
        api_key = winobj.llm_api_key_input.text()
        model = winobj.llm_model_combo.currentText()
        base_url = winobj.llm_base_url_input.text()
        
        # 清空日志或获取当前日志内容
        current_log = winobj.loglabel.toPlainText()
        if current_log in ["处理日志将显示在这里...", "Processing log will be displayed here..."]:
            winobj.loglabel.clear()
        
        # 验证必填项
        if not api_key and provider != 'local':
            msg = '❌ 请输入 API Key' if config.defaulelang == 'zh' else '❌ Please enter API Key'
            winobj.loglabel.appendPlainText(f'\n{msg}')
            # 自动滚动
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )
            return
        
        if not model:
            msg = '❌ 请选择模型' if config.defaulelang == 'zh' else '❌ Please select model'
            winobj.loglabel.appendPlainText(f'\n{msg}')
            # 自动滚动
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )
            return
        
        # 禁用按钮，显示测试中
        winobj.llm_test_btn.setDisabled(True)
        winobj.llm_test_btn.setText('⏳\n测试中' if config.defaulelang == 'zh' else '⏳\nTesting')
        
        # 在日志中显示开始测试
        if config.defaulelang == 'zh':
            test_start_msg = f'\n{"="*50}\n🔍 开始测试 LLM 连接...\n{"="*50}\n📌 提供商: {provider}\n📌 模型: {model}\n📌 正在发送测试请求...'
        else:
            test_start_msg = f'\n{"="*50}\n🔍 Testing LLM connection...\n{"="*50}\n📌 Provider: {provider}\n📌 Model: {model}\n📌 Sending test request...'
        
        winobj.loglabel.appendPlainText(test_start_msg)
        # 自动滚动到底部
        winobj.loglabel.verticalScrollBar().setValue(
            winobj.loglabel.verticalScrollBar().maximum()
        )
        
        # 强制刷新UI
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # 创建并启动测试线程
        test_thread = TestLLMThread(provider, api_key, model, base_url)
        
        def on_test_progress(message):
            """进度更新的回调"""
            # 在日志中显示进度
            winobj.loglabel.appendPlainText(f'{message}')
            # 自动滚动到底部
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )
        
        def on_test_finished(message, success):
            """测试完成的回调"""
            # 在日志中显示结果
            winobj.loglabel.appendPlainText(f'\n{message}')
            winobj.loglabel.appendPlainText(f'{"="*50}\n')
            
            # 自动滚动到底部
            winobj.loglabel.verticalScrollBar().setValue(
                winobj.loglabel.verticalScrollBar().maximum()
            )
            
            # 恢复按钮状态
            winobj.llm_test_btn.setDisabled(False)
            winobj.llm_test_btn.setText('🔍\n测试连接' if config.defaulelang == 'zh' else '🔍\nTest\nConnection')
        
        test_thread.progress.connect(on_test_progress)
        test_thread.finished.connect(on_test_finished)
        test_thread.start()
        
        # 保存线程引用，避免被垃圾回收
        winobj._test_thread = test_thread
    
    def get_file():
        # 检查是否是拖放文件
        if hasattr(winobj.videobtn, 'selected_file') and winobj.videobtn.selected_file:
            fname = winobj.videobtn.selected_file
            winobj.videobtn.selected_file = ""  # 清空，避免重复使用
        else:
            # 点击按钮选择文件
            formats = ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'mp3', 'wav', 'flac', 'm4a']
            format_str = ' '.join([f'*.{f}' for f in formats])
            fname, _ = QFileDialog.getOpenFileName(
                winobj, 
                "选择视频或音频文件" if config.defaulelang == 'zh' else 'Select Video/Audio File',
                config.params['last_opendir'],
                f"Video/Audio files({format_str})"
            )
        
        if fname:
            from pathlib import Path
            fname = fname.replace('file:///', '').replace('\\', '/')
            # 显示文件名
            file_name = Path(fname).name
            winobj.videoinput.setText(f"✅ {file_name}\n📂 {fname}")
    
    def get_srt_file():
        """选择字幕文件"""
        # 检查是否是拖放文件
        if hasattr(winobj.srtbtn, 'selected_file') and winobj.srtbtn.selected_file:
            fname = winobj.srtbtn.selected_file
            winobj.srtbtn.selected_file = ""  # 清空，避免重复使用
        else:
            # 点击按钮选择文件
            fname, _ = QFileDialog.getOpenFileName(
                winobj,
                "选择字幕文件" if config.defaulelang == 'zh' else 'Select Subtitle File',
                config.params['last_opendir'],
                "Subtitle files(*.srt)"
            )
        
        if fname:
            from pathlib import Path
            fname = fname.replace('file:///', '').replace('\\', '/')
            # 显示文件名
            file_name = Path(fname).name
            winobj.srtinput.setText(f"✅ {file_name}\n📂 {fname}")

    def start():
        winobj.has_done = False
        # 从显示文本中提取文件路径（格式：✅ 文件名\n📂 路径）
        video_text = winobj.videoinput.text()
        if '📂' in video_text:
            video_file = video_text.split('📂')[-1].strip()
        else:
            video_file = video_text
        
        if not video_file or video_file == "未选择文件" or video_file == "No file selected":
            tools.show_error(
                '必须选择视频或音频文件' if config.defaulelang == 'zh' else 'Video/audio file must be selected',
                False)
            return
        
        # 检查是否使用 LLM
        use_llm = winobj.use_llm_checkbox.isChecked()
        
        # 检查是否使用现有字幕
        existing_srt = None
        if winobj.use_existing_srt_checkbox.isChecked():
            # 从显示文本中提取文件路径
            srt_text = winobj.srtinput.text()
            if '📂' in srt_text:
                existing_srt = srt_text.split('📂')[-1].strip()
            else:
                existing_srt = srt_text
            
            if not existing_srt or existing_srt == "未选择字幕文件" or existing_srt == "No subtitle file selected":
                tools.show_error(
                    '请选择字幕文件' if config.defaulelang == 'zh' else 'Please select subtitle file',
                    False)
                return
            if not Path(existing_srt).exists():
                tools.show_error(
                    '字幕文件不存在' if config.defaulelang == 'zh' else 'Subtitle file does not exist',
                    False)
                return
        
        # 获取参数
        language = winobj.language_combo.currentText().split('=')[0]
        model_size = winobj.model_combo.currentText()
        
        try:
            max_duration = float(winobj.duration_input.text())
            max_words = int(winobj.words_input.text())
            if max_duration <= 0 or max_words <= 0:
                raise ValueError
        except:
            tools.show_error(
                '参数必须是正数' if config.defaulelang == 'zh' else 'Parameters must be positive numbers',
                False)
            return
        
        # 获取设备选择
        device = winobj.device_combo.currentText().lower()
        
        # 获取 LLM 配置
        llm_provider = winobj.llm_provider_combo.currentText().lower() if use_llm else ''
        llm_api_key = winobj.llm_api_key_input.text() if use_llm else ''
        llm_model = winobj.llm_model_combo.currentText() if use_llm else ''
        llm_base_url = winobj.llm_base_url_input.text() if use_llm else ''
        
        if use_llm and not llm_api_key and llm_provider != 'local':
            tools.show_error(
                '请输入 LLM API Key' if config.defaulelang == 'zh' else 'Please enter LLM API Key',
                False)
            return

        winobj.startbtn.setText('生成中...' if config.defaulelang == 'zh' else 'Generating...')
        winobj.startbtn.setDisabled(True)
        winobj.resultbtn.setDisabled(True)
        winobj.resultinput.setPlainText("")
        winobj.loglabel.setPlainText("🚀 开始处理..." if config.defaulelang == 'zh' else '🚀 Starting...')

        # LLM 模式必须启用
        if not use_llm:
            tools.show_error(
                '此工具必须启用 LLM 智能断句' if config.defaulelang == 'zh' else 'This tool requires LLM smart split',
                False)
            winobj.startbtn.setText('开始生成' if config.defaulelang == 'zh' else 'Start Generate')
            winobj.startbtn.setDisabled(False)
            return
        
        task = LLMSplitThread(
            parent=winobj,
            video_file=video_file,
            language=language,
            model_size=model_size,
            max_duration=max_duration,
            max_words=max_words,
            device=device,
            existing_srt=existing_srt,
            llm_provider=llm_provider,
            llm_api_key=llm_api_key,
            llm_model=llm_model,
            llm_base_url=llm_base_url
        )
        
        task.uito.connect(feed)
        task.start()

    def opendir():
        QDesktopServices.openUrl(QUrl.fromLocalFile(RESULT_DIR))

    from videotrans.component import LLMSplitForm
    try:
        winobj = config.child_forms.get('llmsplitw')
        if winobj is not None:
            winobj.show()
            winobj.raise_()
            winobj.activateWindow()
            return
        winobj = LLMSplitForm()
        config.child_forms['llmsplitw'] = winobj
        
        winobj.videobtn.clicked.connect(get_file)
        winobj.srtbtn.clicked.connect(get_srt_file)
        winobj.use_existing_srt_checkbox.stateChanged.connect(toggle_srt_input)
        winobj.use_llm_checkbox.stateChanged.connect(toggle_llm_settings)
        winobj.llm_test_btn.clicked.connect(test_llm_connection)
        winobj.resultbtn.clicked.connect(opendir)
        winobj.startbtn.clicked.connect(start)
        
        # 监听 API Key 输入变化，自动保存到 .env 文件
        winobj.llm_api_key_input.textChanged.connect(save_api_key_to_env)
        
        # 初始化时根据默认状态显示/隐藏控件
        toggle_llm_settings()
        toggle_srt_input()
        
        # 从环境变量或配置文件读取 API Key
        import os
        api_key = ""
        # 首先尝试从环境变量读取
        api_key = os.environ.get('SILICONFLOW_API_KEY', '')
        # 如果环境变量没有，尝试从 .env 文件读取
        if not api_key:
            env_file = os.path.join(config.ROOT_DIR, '.env')
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    key = key.strip()
                                    value = value.strip().strip('"').strip("'")
                                    if key == 'SILICONFLOW_API_KEY':
                                        api_key = value
                                        break
                except Exception as e:
                    print(f"读取 .env 文件失败: {e}")
        
        # 设置 API Key 到输入框
        if api_key:
            winobj.llm_api_key_input.setText(api_key)
        
        # 设置默认模型为 DeepSeek-R1（在 UI 初始化后，提供商已经设置为 SiliconFlow）
        winobj.llm_model_combo.setCurrentText("deepseek-ai/DeepSeek-R1")
        
        # 让窗口在屏幕上居中显示
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = winobj.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            winobj.move(window_geometry.topLeft())
        
        winobj.show()
    except Exception as e:
        import traceback
        print(traceback.format_exc())

