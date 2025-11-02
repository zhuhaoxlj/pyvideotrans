"""
Whisper Processor - Handles audio processing and transcription
使用 OpenAI Whisper 实现，支持词级时间戳和缓存
"""

from PySide6.QtCore import QObject, Signal
from pathlib import Path
import tempfile
import time
import os
import hashlib
import pickle
from datetime import timedelta
import subprocess
from pydub import AudioSegment
from utils.srt_utils import merge_srt_files
from utils.fcpxml_generator import generate_fcpxml
from utils.paths import setup_whisper_cache, get_models_dir
from utils.model_loader import format_bytes

# ⭐ 在模块加载时就导入 whisper，避免在 QThread 中导入导致崩溃
print("🔧 预加载 whisper（避免线程崩溃）...")
try:
    import whisper
    print("✅ whisper 预加载成功")
except Exception as e:
    print(f"❌ whisper 预加载失败: {e}")
    whisper = None


class WhisperProcessor(QObject):
    progress = Signal(float)
    status = Signal(str)
    output = Signal(str)
    batch_info = Signal(int, int, int, str)  # current, total, percentage, remaining
    finished = Signal(str, str)  # srt_path, fcpxml_path
    error = Signal(str)
    
    def __init__(self, data):
        super().__init__()
        print("🔧 WhisperProcessor.__init__() 开始")
        print(f"   data: {data}")
        
        self.data = data
        self.model = None
        self._download_start_time = None
        self._last_download_update = 0
        
        # 缓存开关（默认启用）
        self.enable_cache = data.get('enable_cache', True)
        cache_status = '✅ 已启用' if self.enable_cache else '❌ 已禁用'
        print(f"   缓存开关: {cache_status}")
        
        print("   创建缓存目录...")
        # 缓存目录（与智能分割共享）
        self.cache_dir = Path.home() / 'Videos' / 'pyvideotrans' / 'get_srt_zimu' / 'whisper_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ 缓存目录: {self.cache_dir}")
        print("🔧 WhisperProcessor.__init__() 完成\n")
        
    def _setup_download_progress_hook(self):
        """Setup hooks to monitor download progress"""
        import urllib.request
        
        # Store original urlretrieve
        original_urlretrieve = urllib.request.urlretrieve
        
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            
            # Initialize start time
            if self._download_start_time is None:
                self._download_start_time = time.time()
                self.output.emit("⬇️  Starting download...\n")
            
            if total_size > 0:
                percentage = min((downloaded / total_size) * 100, 100)
                
                # Update every 5% or every 10 seconds
                current_time = time.time()
                if percentage - self._last_download_update >= 5 or \
                   current_time - self._download_start_time > 10:
                    
                    elapsed = current_time - self._download_start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0
                    
                    self.output.emit(
                        f"📥 Downloaded: {format_bytes(downloaded)} / {format_bytes(total_size)} "
                        f"({percentage:.1f}%) - Speed: {format_bytes(int(speed))}/s\n"
                    )
                    self._last_download_update = percentage
        
        def custom_urlretrieve(url, filename, reporthook=None, data=None):
            """Custom urlretrieve with progress reporting"""
            return original_urlretrieve(url, filename, progress_hook, data)
        
        # Monkey patch urllib
        urllib.request.urlretrieve = custom_urlretrieve
        
    def _get_best_device(self):
        """Detect and return the best available device for processing"""
        try:
            import torch
            if torch.cuda.is_available():
                print("   检测设备：CUDA GPU 可用")
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                # ⚠️ MPS 设备在词级时间戳模式下有兼容性问题（不支持 float64）
                # 因此使用 CPU 以确保词级时间戳功能正常工作
                print("   检测设备：Apple Silicon MPS 可用，但词级时间戳需要 CPU")
                print("   📝 提示：使用 CPU 模式以支持词级时间戳")
                return "cpu"
            else:
                print("   检测设备：使用 CPU")
                return "cpu"
        except ImportError:
            print("   检测设备：torch 未安装，使用 CPU")
            return "cpu"
        
    def process(self):
        """Main processing function"""
        print("\n" + "=" * 60)
        print("⚙️  process() 方法被调用")
        print("=" * 60)
        
        try:
            print("尝试发送第一个信号...")
            self.output.emit("\n🚀 开始处理流程...\n\n")
            print("✓ 第一个信号发送成功")
            
            # Setup custom cache directory for models
            print("准备发送 Step 1 信号...")
            self.output.emit("📂 Step 1: 设置目录...\n")
            print("✓ Step 1 信号发送成功")
            
            print("调用 setup_whisper_cache()...")
            models_dir = setup_whisper_cache()
            print(f"✓ setup_whisper_cache() 返回: {models_dir}")
            
            print("发送 models 目录信息...")
            self.output.emit(f"   ✓ Models 目录: {models_dir}\n")
            print("发送 cache 目录信息...")
            self.output.emit(f"   ✓ Cache 目录: {self.cache_dir}\n\n")
            print("✓ Step 1 完成")
            
            print("获取模型信息...")
            model_name = self.data['model']
            model_display = self.data.get('model_display', model_name)
            print(f"   model_name: {model_name}")
            print(f"   model_display: {model_display}")
            
            # Show model information
            print("发送模型信息到 UI...")
            self.output.emit("=" * 60 + "\n")
            self.output.emit(f"🎯 Model: {model_display} (OpenAI Whisper)\n")
            self.output.emit(f"📁 Models directory: {models_dir}\n")
            self.output.emit(f"💾 Cache directory: {self.cache_dir}\n")
            self.output.emit("=" * 60 + "\n\n")
            print("✓ 模型信息发送完成")
            
            # Detect best available device
            print("\nStep 2: 检测设备...")
            self.output.emit("🖥️  Step 2: 检测计算设备...\n")
            print("调用 _get_best_device()...")
            device = self._get_best_device()
            self.device = device  # 保存为实例变量
            print(f"✓ 检测到设备: {device}")
            self.output.emit(f"   ✓ 检测到设备: {device}\n\n")
            print("✓ Step 2 完成")
            
            print("\nStep 3: 加载模型...")
            self.status.emit(f"Loading OpenAI Whisper {model_display} model...")
            self.output.emit(f"⚙️  Step 3: 加载 OpenAI Whisper 模型...\n")
            self.output.emit(f"   模型: {model_display}\n")
            self.output.emit(f"   设备: {device}\n")
            self.output.emit("   正在加载...\n\n")
            
            # Load OpenAI Whisper model
            try:
                print("检查 whisper...")
                self.output.emit("   📥 使用预加载的 whisper...\n")
                
                if whisper is None:
                    raise ImportError("whisper 未能预加载")
                
                print("✓ whisper 可用")
                self.output.emit("   ✓ whisper 已就绪\n")
                
                print(f"加载模型: {model_name}")
                print(f"   device: {device}")
                print(f"   download_root: {models_dir}")
                
                self.output.emit(f"   📥 加载模型 {model_name}...\n")
                self.output.emit(f"   （首次加载需要下载，请耐心等待）\n")
                
                print("创建 Whisper 模型实例...")
                # OpenAI Whisper loads model to the specified device
                self.model = whisper.load_model(model_name, device=device, download_root=str(models_dir))
                print("✓ Whisper 模型创建成功")
                
                self.output.emit(f"\n✅ 模型加载成功！\n")
                self.output.emit(f"   Device: {device}\n\n")
                
                # Show device info
                if device == "cuda":
                    self.output.emit("✓ Using NVIDIA GPU acceleration (CUDA)\n")
                elif device == "mps":
                    self.output.emit("✓ Using Apple Silicon GPU acceleration (MPS)\n")
                else:
                    self.output.emit("ℹ Using CPU\n")
                    # 检查是否是因为 MPS 限制而使用 CPU
                    try:
                        import torch
                        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                            self.output.emit("📝 注意：Apple Silicon 检测到，但词级时间戳需要 CPU\n")
                            self.output.emit("   原因：MPS 不支持 float64（DTW 算法需要）\n")
                            self.output.emit("   性能：Apple Silicon CPU 依然很快！⚡\n")
                    except:
                        pass
                    
            except Exception as e:
                import traceback
                error_msg = f"❌ 模型加载失败!\n\n错误信息: {str(e)}\n\n详细堆栈:\n{traceback.format_exc()}"
                self.output.emit(error_msg)
                self.error.emit(error_msg)
                return
            
            # 检查缓存
            try:
                self.output.emit("\n🔍 Step 4: 检查缓存...\n")
                self.output.emit(f"   视频文件: {self.data['file_path']}\n")
                cache_status = '✅ 已启用' if self.enable_cache else '❌ 已禁用'
                self.output.emit(f"   缓存开关: {cache_status}\n")
                
                all_words = None
                detected_language = None
                cached_data = None
                
                # 只有启用缓存时才检查和加载
                if self.enable_cache:
                    cache_key = self._get_cache_key(self.data['file_path'])
                    self.output.emit(f"   缓存键: {cache_key[:16]}... (SHA256)\n")
                    cached_data = self._load_cache(cache_key)
                else:
                    self.output.emit("   ⚠️  缓存已禁用，将重新识别\n")
                
                if cached_data:
                    self.output.emit("   ✅ 找到缓存！\n")
                    all_words = cached_data['all_words']
                    detected_language = cached_data['language']
                    self.output.emit(f"   📊 从缓存加载: {len(all_words)} 个词\n")
                    self.output.emit(f"   🌐 检测语言: {detected_language}\n\n")
                else:
                    self.output.emit("   ❌ 未找到缓存\n\n")
                    self.output.emit("🎵 Step 5: 开始语音识别...\n\n")
                    
                    # Convert audio to WAV
                    self.status.emit("Converting audio to WAV format...")
                    self.output.emit("   Step 5.1: 转换音频格式...\n")
                    self.output.emit(f"   源文件: {self.data['file_path']}\n")
                    
                    try:
                        wav_path = self._convert_to_wav(self.data['file_path'])
                        self.output.emit(f"   ✅ 转换完成: {wav_path}\n\n")
                    except Exception as e:
                        import traceback
                        error_msg = f"❌ 音频转换失败: {str(e)}\n\n{traceback.format_exc()}"
                        self.output.emit(error_msg)
                        self.error.emit(error_msg)
                        return
                    
                    # 使用 OpenAI Whisper 进行转录（获取词级时间戳）
                    self.status.emit("Generating AI subtitles with word timestamps...")
                    self.output.emit("   Step 5.2: 开始语音识别（词级时间戳）\n")
                    self.output.emit("   ⏳ 此过程可能需要几分钟，请耐心等待...\n\n")
                    
                    try:
                        start_time = time.time()
                        self.output.emit("   🎤 调用 _transcribe_with_word_timestamps()...\n")
                        all_words, detected_language = self._transcribe_with_word_timestamps(wav_path)
                        transcribe_time = time.time() - start_time
                        
                        if not all_words:
                            self.error.emit("未检测到任何语音内容")
                            return
                        
                        self.output.emit(f"\n✅ 识别完成！\n")
                        self.output.emit(f"   耗时: {transcribe_time:.1f}秒\n")
                        self.output.emit(f"   检测语言: {detected_language}\n")
                        self.output.emit(f"   词数: {len(all_words)}\n\n")
                        
                        # 保存缓存（仅在启用缓存时）
                        if self.enable_cache:
                            self._save_cache(cache_key, all_words, detected_language)
                        else:
                            self.output.emit(f"💡 提示: 缓存已禁用，未保存词级时间戳\n")
                        
                    except Exception as e:
                        import traceback
                        self.error.emit(f"语音识别失败: {str(e)}\n\n详细错误:\n{traceback.format_exc()}")
                        return
                        
            except Exception as e:
                import traceback
                self.error.emit(f"处理失败: {str(e)}\n\n详细错误:\n{traceback.format_exc()}")
                return
            
            # 从词级时间戳生成 SRT 文件
            self.status.emit("Generating subtitle files...")
            self.output.emit("📝 从词级时间戳生成字幕文件...\n")
            srt_files = self._generate_srt_from_words(all_words)
            
            # Merge SRT files
            self.status.emit("Merging subtitle files...")
            self.output.emit("\nMerging subtitle files...\n")
            merged_srt_path = merge_srt_files(srt_files, self.data['project_name'])
            
            # Generate FCPXML
            self.status.emit("Generating FCPXML file...")
            self.output.emit("Generating FCPXML file...\n")
            fcpxml_path = generate_fcpxml(
                merged_srt_path,
                self.data['fps'],
                self.data['project_name'],
                self.data['language']
            )
            
            self.output.emit("\n✓ All processing completed!\n")
            self.finished.emit(merged_srt_path, fcpxml_path)
            
        except Exception as e:
            import traceback
            error_msg = f"❌ process() 方法异常: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            try:
                self.error.emit(error_msg)
            except:
                print("⚠️  无法发送错误信号")
            
    def _convert_to_wav(self, audio_path):
        """Convert audio/video to 16kHz WAV format"""
        self.output.emit(f"      尝试使用 pydub 转换...\n")
        try:
            # pydub can handle most formats including video files (extracts audio)
            audio = AudioSegment.from_file(audio_path)
            self.output.emit(f"      ✓ 文件读取成功\n")
            
            audio = audio.set_frame_rate(16000).set_channels(1)
            self.output.emit(f"      ✓ 转换为 16kHz 单声道\n")
            
            wav_path = Path(tempfile.gettempdir()) / f"{self.data['project_name']}.wav"
            self.output.emit(f"      ✓ 导出到: {wav_path}\n")
            
            audio.export(str(wav_path), format="wav")
            return str(wav_path)
        except Exception as e:
            self.output.emit(f"      ⚠️  pydub 失败: {str(e)}\n")
            self.output.emit(f"      尝试使用 ffmpeg...\n")
            
            # If pydub fails, try using ffmpeg directly (for video files)
            wav_path = Path(tempfile.gettempdir()) / f"{self.data['project_name']}.wav"
            try:
                subprocess.run([
                    'ffmpeg', '-i', audio_path,
                    '-vn',  # No video
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    str(wav_path),
                    '-y'  # Overwrite
                ], check=True, capture_output=True)
                self.output.emit(f"      ✓ ffmpeg 转换成功\n")
                return str(wav_path)
            except Exception as ffmpeg_error:
                raise Exception(f"Failed to convert audio: {str(e)}\nFFmpeg error: {str(ffmpeg_error)}")
        
    def _split_audio(self, wav_path):
        """Split audio into 10-minute segments if needed"""
        audio = AudioSegment.from_wav(wav_path)
        duration_ms = len(audio)
        segment_duration_ms = 10 * 60 * 1000  # 10 minutes
        
        if duration_ms <= segment_duration_ms:
            return [wav_path]
        
        segments = []
        num_segments = (duration_ms + segment_duration_ms - 1) // segment_duration_ms
        
        for i in range(num_segments):
            start = i * segment_duration_ms
            end = min((i + 1) * segment_duration_ms, duration_ms)
            segment = audio[start:end]
            
            segment_path = Path(tempfile.gettempdir()) / f"{self.data['project_name']}_segment_{i}.wav"
            segment.export(str(segment_path), format="wav")
            segments.append(str(segment_path))
            
        return segments
        
    def _transcribe_with_word_timestamps(self, audio_path):
        """使用 OpenAI Whisper 进行转录，获取词级时间戳"""
        try:
            language_code = self.data['language_code']
            
            # Set initial prompt for Chinese
            initial_prompt = None
            if language_code == "zh":
                if self.data['language'] == "Chinese Simplified":
                    initial_prompt = "以下是普通话的句子"
                else:
                    initial_prompt = "以下是普通話的句子"
            
            self.output.emit(f"   语言代码: {language_code}\n")
            if initial_prompt:
                self.output.emit(f"   初始提示: {initial_prompt}\n")
            self.output.emit("\n   开始转录...\n")
            
            # 根据设备选择精度
            device = getattr(self, 'device', 'cpu')
            use_fp16 = (device == 'cuda')  # 仅在 CUDA 上使用 FP16
            self.output.emit(f"   精度设置: {'FP16' if use_fp16 else 'FP32'}\n")
            
            # 使用 OpenAI Whisper 转录
            result = self.model.transcribe(
                audio_path,
                language=language_code if language_code else None,
                initial_prompt=initial_prompt,
                word_timestamps=True,  # ⭐ 启用词级时间戳
                fp16=use_fp16,  # CPU 使用 FP32，CUDA 使用 FP16
                verbose=False
            )
            
        except Exception as e:
            self.output.emit(f"\n❌ 转录初始化失败: {str(e)}\n")
            raise
        
        # 收集所有词和文本
        try:
            all_words = []
            full_text = []
            segment_count = 0
            
            self.output.emit("   开始收集词级时间戳...\n")
            
            # OpenAI Whisper returns segments in result['segments']
            segments = result.get('segments', [])
            detected_language = result.get('language', language_code)
            
            for segment in segments:
                segment_count += 1
                if segment_count % 10 == 0:
                    self.output.emit(f"   处理片段: {segment_count}...\n")
                
                # 收集文本
                if 'text' in segment:
                    full_text.append(segment['text'].strip())
                
                # 收集词级时间戳
                if 'words' in segment:
                    for word in segment['words']:
                        all_words.append({
                            'word': word.get('word', ''),
                            'start': word.get('start', 0),
                            'end': word.get('end', 0)
                        })
            
            self.output.emit(f"   收集完成：{segment_count} 个片段\n")
            
            # 输出识别的文本
            if full_text:
                self.output.emit("\n📄 识别文本预览:\n")
                preview = ' '.join(full_text[:10])  # 显示前10段
                if len(full_text) > 10:
                    preview += "..."
                self.output.emit(f"   {preview}\n")
            
            return all_words, detected_language
            
        except Exception as e:
            self.output.emit(f"\n❌ 收集数据失败: {str(e)}\n")
            raise
        
    def _generate_srt_from_words(self, all_words):
        """从词级时间戳生成 SRT 文件"""
        # 使用简单规则将词组合成句子
        subtitles = []
        current_words = []
        current_start = None
        
        max_words = 15  # 每条字幕最多 15 个词
        max_duration = 5.0  # 每条字幕最多 5 秒
        sentence_ends = {'.', '!', '?', '。', '！', '？'}
        
        for i, word in enumerate(all_words):
            if current_start is None:
                current_start = word['start']
            
            current_words.append(word)
            duration = word['end'] - current_start
            word_text = word['word'].strip()
            
            should_split = False
            
            # 句子结束
            if word_text and word_text[-1] in sentence_ends:
                should_split = True
            # 超过限制
            elif duration >= max_duration or len(current_words) >= max_words:
                should_split = True
            
            if should_split and current_words:
                subtitle = {
                    'start': current_start,
                    'end': current_words[-1]['end'],
                    'text': ''.join([w['word'] for w in current_words]).strip()
                }
                subtitles.append(subtitle)
                current_words = []
                current_start = None
        
        # 处理剩余的词
        if current_words:
            subtitle = {
                'start': current_start,
                'end': current_words[-1]['end'],
                'text': ''.join([w['word'] for w in current_words]).strip()
            }
            subtitles.append(subtitle)
        
        # 生成临时 SRT 文件
        srt_path = Path(tempfile.gettempdir()) / f"{self.data['project_name']}_word_based.srt"
        self._write_srt_from_subtitles(subtitles, str(srt_path))
        
        self.output.emit(f"✅ 生成 {len(subtitles)} 条字幕\n")
        
        return [str(srt_path)]
    
    def _write_srt_from_subtitles(self, subtitles, output_path):
        """将字幕列表写入 SRT 文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                f.write(f"{i}\n")
                f.write(f"{self._format_timestamp(sub['start'])} --> {self._format_timestamp(sub['end'])}\n")
                f.write(f"{sub['text']}\n\n")
    
    def _get_cache_key(self, file_path):
        """生成缓存键（与智能分割共享）"""
        try:
            hash_obj = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            self.output.emit(f'⚠️ 计算哈希值失败: {str(e)}\n')
            return None
    
    def _save_cache(self, cache_key, all_words, language):
        """保存缓存（与智能分割共享）"""
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
            self.output.emit(f'💾 缓存已保存: {cache_file.name}\n')
            self.output.emit(f'📝 提示: 智能分割功能可以直接使用此缓存！\n')
        except Exception as e:
            self.output.emit(f'⚠️ 保存缓存失败: {str(e)}\n')
    
    def _load_cache(self, cache_key):
        """加载缓存（与智能分割共享）"""
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
            self.output.emit(f'⚠️ 读取缓存失败: {str(e)}\n')
            return None
                
    def _format_timestamp(self, seconds):
        """Format timestamp for SRT format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

