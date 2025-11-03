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
                 llm_api_key='', llm_model='deepseek-ai/DeepSeek-V3.1-Terminus', llm_base_url='',
                 language='en', model_size='large-v3-turbo', max_duration=5.0,
                 max_words=12, device='cpu', output_dir=None, models_dir=None, enable_cache=True,
                 enable_chunking=True, chunk_size=500, enable_strict_validation=True):
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
            enable_chunking: 是否启用分段处理（推荐性能一般的模型启用）
            chunk_size: 每段的词数（默认500词）
            enable_strict_validation: 是否启用严格文本验证（检测LLM是否修改了单词）
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
        self.enable_chunking = enable_chunking
        self.chunk_size = chunk_size
        self.enable_strict_validation = enable_strict_validation
        
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
        """简单的 LLM 分割（用于仅SRT模式）- 支持分段处理和严格验证"""
        
        # 检查是否需要分段处理
        word_count = len(text.split())
        
        if self.enable_chunking and word_count > self.chunk_size:
            self.progress.emit(f"📊 文本较长 ({word_count} 词)，启用分段处理模式")
            self.progress.emit(f"   分段大小: {self.chunk_size} 词/段")
            return self._llm_split_chunked(text)
        else:
            self.progress.emit(f"📊 文本长度适中 ({word_count} 词)，使用单次处理")
            return self._llm_split_single(text)
    
    def _llm_split_single(self, text):
        """单次处理整个文本"""
        prompt = f"""You are a professional subtitle editor following industry standards (BBC, Netflix, TED).

TEXT TO SPLIT:
{text}

PRINCIPLES (in order of importance):

1. **SEMANTIC COMPLETENESS**: Each subtitle should express a complete thought
   - Don't break in the middle of phrases or clauses
   - Keep grammatical structures intact
   - A subtitle should be understandable on its own

2. **NATURAL BREAKING POINTS**: Split at logical pauses
   - Priority 1: Sentence endings (periods, question marks)
   - Priority 2: Major punctuation (commas, semicolons, dashes)
   - Priority 3: Conjunctions (and, but, because, when, if)

3. **READING COMFORT**:
   - For English: typically 6-12 words (flexible!)
   - Shorter (3-5 words) OK if complete
   - Longer (up to 15 words) OK if indivisible
   - Reading time: 1-2 seconds per subtitle

4. **NATURAL VARIETY**: Don't make every subtitle the same length

⚠️ CRITICAL: DO NOT modify, correct, or rewrite any words. Keep the text EXACTLY as written.

EXAMPLES:

❌ BAD (breaks meaning):
1. "One of my earliest memories is"
2. "of trying to wake up"
3. "one of my relatives"

✅ GOOD (preserves meaning):
1. "One of my earliest memories"
2. "is of trying to wake up one of my relatives"

OR:
1. "One of my earliest memories is of trying to wake up one of my relatives"

OUTPUT FORMAT:
Return ONLY a JSON array. Each element should be a string (the subtitle text).

Example:
["First complete thought here", "Second complete thought", "Third one"]

DO NOT include explanations, only return the JSON array.

REMEMBER: 
1. Copy text EXACTLY - do not fix grammar or spelling
2. Semantic completeness is MORE important than exact word counts."""
        
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
            
            # 严格验证
            if self.enable_strict_validation and segments:
                segments = self._validate_text_integrity(text, segments)
            
            return segments
            
        except Exception as e:
            self.progress.emit(f"\n   ❌ LLM 调用失败: {str(e)}") 
            raise
    
    def _llm_split_chunked(self, text):
        """分段处理长文本"""
        # 按句子分割
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            self.progress.emit("   ⚠️  无法分割句子，回退到单次处理")
            return self._llm_split_single(text)
        
        self.progress.emit(f"   ✂️  分割为 {len(sentences)} 个句子")
        
        # 将句子组合成chunks
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            if current_word_count + sentence_words > self.chunk_size and current_chunk:
                # 当前chunk已满，保存并开始新chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_words
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_words
        
        # 添加最后一个chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        self.progress.emit(f"   📦 组合为 {len(chunks)} 个处理块")
        
        # 处理每个chunk
        all_segments = []
        for i, chunk in enumerate(chunks, 1):
            self.progress.emit(f"\n   🔄 处理第 {i}/{len(chunks)} 块 ({len(chunk.split())} 词)...")
            
            try:
                chunk_segments = self._llm_split_single(chunk)
                if chunk_segments:
                    all_segments.extend(chunk_segments)
                    self.progress.emit(f"   ✅ 第 {i} 块完成，生成 {len(chunk_segments)} 个片段")
                else:
                    self.progress.emit(f"   ⚠️  第 {i} 块处理失败，跳过")
            except Exception as e:
                self.progress.emit(f"   ❌ 第 {i} 块错误: {str(e)}")
                continue
        
        self.progress.emit(f"\n   ✅ 分段处理完成！共 {len(all_segments)} 个片段")
        return all_segments
    
    def _split_into_sentences(self, text):
        """将文本分割成句子"""
        import re
        
        # 使用正则表达式按标点分割
        # 保留标点符号
        pattern = r'([.!?]+[\s]|[。！？]+)'
        parts = re.split(pattern, text)
        
        sentences = []
        current = ''
        
        for part in parts:
            current += part
            if re.match(pattern, part):
                # 遇到句子结束符
                sentences.append(current.strip())
                current = ''
        
        # 添加剩余部分
        if current.strip():
            sentences.append(current.strip())
        
        return [s for s in sentences if s]
    
    def _validate_text_integrity(self, original_text, segments):
        """验证LLM是否修改了原文"""
        self.progress.emit("   🔍 验证文本完整性...")
        
        # 重建文本
        reconstructed = ' '.join(segments)
        
        # 标准化比较（忽略多余空格和标点）
        def normalize(text):
            text = text.lower()
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            return text
        
        original_norm = normalize(original_text)
        reconstructed_norm = normalize(reconstructed)
        
        # 计算相似度
        similarity = difflib.SequenceMatcher(None, original_norm, reconstructed_norm).ratio()
        
        self.progress.emit(f"   📊 文本相似度: {similarity*100:.1f}%")
        
        if similarity < 0.95:
            self.progress.emit("   ⚠️  警告: LLM 修改了部分单词！")
            self.progress.emit(f"   原文长度: {len(original_text)} 字符")
            self.progress.emit(f"   返回长度: {len(reconstructed)} 字符")
            
            # 显示差异
            diff = difflib.unified_diff(
                original_norm.split()[:20], 
                reconstructed_norm.split()[:20],
                lineterm='',
                n=0
            )
            diff_lines = list(diff)[2:]  # 跳过头部
            if diff_lines:
                self.progress.emit("   差异示例（前20词）:")
                for line in diff_lines[:5]:
                    self.progress.emit(f"      {line}")
            
            # 询问是否继续
            self.progress.emit("   💡 提示: 建议使用更好的模型或调整参数")
        else:
            self.progress.emit("   ✅ 文本完整性验证通过")
        
        return segments
    
    def llm_smart_split(self, words, detected_language, original_text=None):
        """使用 LLM 进行智能断句（基于词级时间戳）- 支持分段处理"""
        if not words:
            return []
        
        # 如果有原始文本，使用原始文本；否则使用识别的文本
        reference_text = original_text if original_text else ''.join([w['word'] for w in words])
        
        self.progress.emit(f'   LLM提供商: {self.llm_provider}')
        self.progress.emit(f'   LLM模型: {self.llm_model}')
        self.progress.emit(f'   处理文本: {len(words)} 词')
        
        # 检查是否需要分段处理
        if self.enable_chunking and len(words) > self.chunk_size:
            self.progress.emit(f"📊 词数较多 ({len(words)} 词)，启用分段处理")
            self.progress.emit(f"   分段大小: {self.chunk_size} 词/段")
            return self._llm_smart_split_chunked(words, detected_language, reference_text)
        else:
            self.progress.emit(f"📊 词数适中 ({len(words)} 词)，使用单次处理")
            return self._llm_smart_split_single(words, detected_language, reference_text)
    
    def _llm_smart_split_single(self, words, detected_language, reference_text):
        """单次处理所有词"""
        # 构建 prompt
        prompt = self._build_llm_prompt(reference_text, len(words), detected_language)
        
        self.progress.emit('   ⏳ 正在调用 LLM API，请稍候...')
        
        # 调用 LLM（支持流式传输）
        start_time = time.time()
        try:
            self.progress.emit('   📡 LLM 响应流:')
            response = self._call_llm_stream(prompt, reference_text)
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
        
        # 严格验证（检查是否修改了单词）
        if self.enable_strict_validation:
            subtitles = self._validate_subtitle_text_integrity(reference_text, subtitles)
        
        # 验证和调整时间戳
        self.progress.emit('   🔧 验证和调整时间戳...')
        subtitles = self._validate_and_adjust_timestamps(subtitles)
        
        self.progress.emit('   ✅ 时间戳调整完成')
        
        return subtitles
    
    def _llm_smart_split_chunked(self, words, detected_language, reference_text):
        """分段处理词级时间戳"""
        # 将words分成多个chunks
        chunks = []
        current_chunk = []
        
        for i, word in enumerate(words):
            current_chunk.append(word)
            
            if len(current_chunk) >= self.chunk_size:
                chunks.append(current_chunk)
                current_chunk = []
        
        # 添加剩余的词
        if current_chunk:
            chunks.append(current_chunk)
        
        self.progress.emit(f"   📦 分为 {len(chunks)} 个处理块")
        
        # 处理每个chunk
        all_subtitles = []
        
        for i, chunk_words in enumerate(chunks, 1):
            self.progress.emit(f"\n   🔄 处理第 {i}/{len(chunks)} 块 ({len(chunk_words)} 词)...")
            
            # 构建这个chunk的文本
            chunk_text = ''.join([w['word'] for w in chunk_words])
            
            try:
                chunk_subtitles = self._llm_smart_split_single(chunk_words, detected_language, chunk_text)
                if chunk_subtitles:
                    all_subtitles.extend(chunk_subtitles)
                    self.progress.emit(f"   ✅ 第 {i} 块完成，生成 {len(chunk_subtitles)} 条字幕")
                else:
                    self.progress.emit(f"   ⚠️  第 {i} 块处理失败，使用规则引擎")
                    fallback_subs = self.fallback_split(chunk_words)
                    if fallback_subs:
                        all_subtitles.extend(fallback_subs)
            except Exception as e:
                self.progress.emit(f"   ❌ 第 {i} 块错误: {str(e)}")
                # 使用规则引擎作为后备
                fallback_subs = self.fallback_split(chunk_words)
                if fallback_subs:
                    all_subtitles.extend(fallback_subs)
        
        self.progress.emit(f"\n   ✅ 分段处理完成！共 {len(all_subtitles)} 条字幕")
        
        # 最终验证和调整
        self.progress.emit('   🔧 最终时间戳调整...')
        all_subtitles = self._validate_and_adjust_timestamps(all_subtitles)
        
        return all_subtitles
    
    def _validate_subtitle_text_integrity(self, original_text, subtitles):
        """验证字幕文本是否被LLM修改"""
        self.progress.emit("   🔍 验证字幕文本完整性...")
        
        # 重建文本
        reconstructed = ' '.join([sub['text'] for sub in subtitles])
        
        # 标准化比较
        def normalize(text):
            text = text.lower()
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            return text
        
        original_norm = normalize(original_text)
        reconstructed_norm = normalize(reconstructed)
        
        # 计算相似度
        similarity = difflib.SequenceMatcher(None, original_norm, reconstructed_norm).ratio()
        
        self.progress.emit(f"   📊 文本相似度: {similarity*100:.1f}%")
        
        if similarity < 0.90:
            self.progress.emit("   ⚠️  警告: LLM 修改了部分单词！")
            self.progress.emit(f"   原文长度: {len(original_text)} 字符")
            self.progress.emit(f"   返回长度: {len(reconstructed)} 字符")
            
            # 显示差异示例
            diff = difflib.unified_diff(
                original_norm.split()[:30], 
                reconstructed_norm.split()[:30],
                lineterm='',
                n=0
            )
            diff_lines = list(diff)[2:]
            if diff_lines:
                self.progress.emit("   差异示例（前30词）:")
                for line in diff_lines[:8]:
                    self.progress.emit(f"      {line}")
            
            self.progress.emit("   💡 提示: 考虑换用更好的模型或启用分段处理")
        else:
            self.progress.emit("   ✅ 文本完整性验证通过")
        
        return subtitles
    
    def _build_llm_prompt(self, text, word_count, language):
        """构建 LLM prompt - 成熟版，平衡语义完整性和可读性"""
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

        prompt = f"""You are a subtitle splitter. Your ONLY task is to split long text into shorter subtitle segments.

⚠️ CRITICAL RULES (MUST FOLLOW):
1. DO NOT modify, correct, or rewrite any words in the original text
2. DO NOT fix grammar, spelling, or punctuation errors
3. DO NOT rearrange or paraphrase the content
4. ONLY split the text - keep every word exactly as it appears

TEXT TO SPLIT:
{text}

SPLITTING GUIDELINES:

Target Length: ~10 words per subtitle (flexible: 7-13 words is fine)

Split Priority:
1. At sentence endings (. ? ! )
2. At major punctuation (, ; : — )
3. At conjunctions (and, but, so, because, when, if)
4. Keep complete phrases together (don't split subject-verb-object)

EXAMPLES:

❌ BAD - Breaks meaning:
"One of my earliest memories is"
"of trying to wake up"

✅ GOOD - Complete thoughts:
"One of my earliest memories"
"is of trying to wake up one of my relatives"

❌ BAD - Too mechanical:
"And I've been thinking about"
"it a lot lately, partly"
"because it's now exactly 100"

✅ GOOD - Natural splits:
"And I've been thinking about it a lot lately,"
"partly because it's now exactly 100 years"
"since drugs were first banned"

OUTPUT FORMAT (JSON only, no explanations):
[
  {{"text": "exact text from original", "word_count": 5}},
  {{"text": "next segment", "word_count": 10}}
]

REMINDER: Copy the text EXACTLY as written. Do not change anything - just split it into readable segments."""

        return prompt
    
    def _call_llm_stream(self, prompt, words_text):
        """调用 LLM API（流式传输）- 严格按照主项目实现"""
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
    
    def _stream_siliconflow(self, prompt):
        """调用 SiliconFlow API (流式传输) - 严格按照主项目实现"""
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
    
    def _stream_openai(self, prompt):
        """调用 OpenAI API (流式传输) - 严格按照主项目实现"""
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
    
    def _stream_anthropic(self, prompt):
        """调用 Anthropic Claude API (流式传输) - 严格按照主项目实现"""
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
    
    def _stream_deepseek(self, prompt):
        """调用 DeepSeek API (流式传输) - 严格按照主项目实现"""
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
    
    def _stream_local_llm(self, prompt):
        """调用本地 LLM (Ollama 等，流式传输) - 严格按照主项目实现"""
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
                if 'response' in chunk:
                    content = chunk['response']
                    if content:
                        full_content.append(content)
                        self.stream.emit(content)
                
                if chunk.get('done', False):
                    break
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
        """
        增强的文本到单词时间戳匹配算法 - 修复版

        支持：
        1. 缺失词的处理（Whisper 未识别的词）
        2. 时间戳插值估算
        3. 更智能的序列对齐
        4. ⭐ 时间戳连续性检查（修复时间跳跃问题）

        Args:
            text: 要匹配的文本
            words: 词级时间戳列表
            start_idx: 开始索引
            relax: 是否放宽匹配条件（用于尾部segments）
        """
        import re

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
        max_lookahead = 10  # 减小前瞻范围，避免跨句匹配

        while text_idx < len(text_words) and word_idx < len(words):
            text_word = text_words[text_idx]
            best_match = None
            best_score = 0
            best_offset = 0

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

                # 考虑位置因素（越近越好）
                score = score - (offset * 0.15)  # 增加位置惩罚

                # ⭐ 新增：时间戳连续性检查
                if matched_indices and offset > 0:
                    prev_match_idx = matched_indices[-1]
                    prev_end_time = words[prev_match_idx]['end']
                    current_start_time = word_data['start']
                    time_gap = current_start_time - prev_end_time

                    # 如果时间间隔过大（>1.5秒），降低分数
                    if time_gap > 1.5:
                        score -= 0.4

                if score > best_score:
                    best_score = score
                    best_match = word_idx + offset
                    best_offset = offset

            # 如果找到匹配（阈值：0.6，提高阈值）
            if best_score > 0.6:
                matched_indices.append(best_match)
                word_idx = best_match + 1
                text_idx += 1
            else:
                # 未找到匹配，可能是 Whisper 缺失的词
                # 跳过这个文本词，但不移动 word_idx
                text_idx += 1

        if not matched_indices:
            return None

        # 获取匹配到的单词的时间戳
        matched_words = [words[i] for i in matched_indices]

        # ⭐ 核心改进：计算起止时间（带时间跳跃检测）
        start_time = matched_words[0]['start']
        end_time = self._calculate_robust_end_time(matched_words, text_words)

        # 如果匹配率太低，尝试插值估算
        match_ratio = len(matched_indices) / len(text_words)
        if match_ratio < 0.6:
            if len(matched_indices) >= 2:
                # 基于匹配词的密度估算总时长
                avg_word_duration = (matched_words[-1]['end'] - matched_words[0]['start']) / len(matched_indices)
                estimated_duration = avg_word_duration * len(text_words)

                # 使用估算值和检测值中的较小者
                end_time = min(end_time, start_time + estimated_duration)
            else:
                # 只有一个匹配词，使用默认估算
                avg_duration_per_word = 0.3  # 假设每词0.3秒
                end_time = start_time + (len(text_words) * avg_duration_per_word)

        # ⭐ 边界检查：确保结束时间不会过度延伸
        max_reasonable_duration = len(text_words) * 0.8  # 假设最快 1.25 词/秒
        if (end_time - start_time) > max_reasonable_duration:
            end_time = start_time + max_reasonable_duration

        return {
            'start': start_time,
            'end': end_time,
            'next_idx': word_idx,
            'match_ratio': match_ratio  # 用于调试
        }

    def _calculate_robust_end_time(self, matched_words, text_words):
        """
        计算稳健的结束时间（修复时间跳跃问题）

        策略：
        1. 检查匹配词之间的时间间隔
        2. 如果发现大跳跃（>1.5秒），截断在跳跃之前
        3. 否则使用最后一个匹配词的结束时间
        """
        if len(matched_words) == 1:
            return matched_words[0]['end']

        # 检查时间连续性
        for i in range(len(matched_words) - 1):
            current_end = matched_words[i]['end']
            next_start = matched_words[i + 1]['start']
            time_gap = next_start - current_end

            # 如果发现大跳跃（>1.5秒），截断
            if time_gap > 1.5:
                # 截断在跳跃之前，并添加小缓冲
                return current_end + 0.2

        # 没有大跳跃，但仍需验证总时长是否合理
        last_end = matched_words[-1]['end']
        first_start = matched_words[0]['start']
        total_duration = last_end - first_start

        # 如果总时长过长（> 文本词数 * 1.0 秒），可能有问题
        max_expected_duration = len(text_words) * 1.0
        if total_duration > max_expected_duration and len(matched_words) > 1:
            # 使用倒数第二个词的结束时间
            return matched_words[-2]['end'] + 0.3

        return last_end
    
    def _calculate_match_score(self, text_word, whisper_word):
        """
        计算两个词的匹配分数（严格按照主项目实现）
        
        返回值：0.0 - 1.0
        """
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
        
        similarity = 1.0 - (distance / max_len)
        
        # 只有相似度足够高才认为是匹配
        return similarity if similarity > 0.6 else 0.0
    
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
        """验证和调整时间戳 - 增强版"""
        if not subtitles:
            return []

        validated = []

        for i, sub in enumerate(subtitles):
            # 确保时间戳合法
            if sub['start'] >= sub['end']:
                sub['end'] = sub['start'] + 1.0

            # 确保不与前一条重叠
            if i > 0 and sub['start'] < validated[-1]['end']:
                # 添加小间隔（100ms）
                sub['start'] = validated[-1]['end'] + 0.1
                if sub['start'] >= sub['end']:
                    sub['end'] = sub['start'] + 1.0

            # ⭐ 新增：基于词数的智能持续时间检查
            duration = sub['end'] - sub['start']
            word_count = len(sub['text'].split())

            # 正常说话速度：2-4 词/秒（英文）
            min_expected_duration = word_count * 0.25  # 最快 4 词/秒
            max_expected_duration = word_count * 1.0   # 最慢 1 词/秒

            if duration > max_expected_duration and word_count > 0:
                self.progress.emit(
                    f'   ⚠️  字幕 {i+1} 时长过长 ({duration:.2f}s，{word_count}词)，'
                    f'调整为 {max_expected_duration:.2f}s'
                )
                sub['end'] = sub['start'] + max_expected_duration
            elif duration < min_expected_duration and word_count > 0:
                # 只有在持续时间真的太短时才调整
                if duration < 0.5:
                    self.progress.emit(
                        f'   ⚠️  字幕 {i+1} 时长过短 ({duration:.2f}s，{word_count}词)，'
                        f'调整为 {max(min_expected_duration, 0.5):.2f}s'
                    )
                    sub['end'] = sub['start'] + max(min_expected_duration, 0.5)

            validated.append(sub)

        return validated
    
    def fallback_split(self, words):
        """回退到规则引擎断句（当LLM失败时）- 严格按照主项目实现"""
        self.progress.emit('   🔄 使用规则引擎断句...')
        
        # 检查输入
        if not words or len(words) == 0:
            self.progress.emit('   ⚠️  词列表为空，无法断句')
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

