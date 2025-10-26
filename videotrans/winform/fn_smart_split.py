# AI智能字幕生成和断句工具 - 基于词级时间戳
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

    class SmartSplitThread(QThread):
        uito = Signal(str)

        def __init__(self, *, parent=None, video_file=None, language='en', model_size='large-v3-turbo', 
                     max_duration=5.0, max_words=15, device='cpu', existing_srt=None):
            super().__init__(parent=parent)
            self.video_file = video_file
            self.language = language
            self.model_size = model_size
            self.max_duration = max_duration
            self.max_words = max_words
            self.device = device  # 'cpu', 'cuda', or 'mps'
            self.existing_srt = existing_srt  # 现有字幕文件路径
            suffix = '_resplit.srt' if existing_srt else '_smart.srt'
            self.result_file = RESULT_DIR + "/" + Path(video_file).stem + suffix

        def post(self, type='logs', text=""):
            self.uito.emit(json.dumps({"type": type, "text": text}))

        def run(self):
            try:
                # 如果提供了现有字幕文件，使用不同的处理流程
                if self.existing_srt:
                    self.post(type='logs', text='🔄 模式: 重新分割现有字幕')
                    self.process_with_existing_srt()
                else:
                    self.post(type='logs', text='🆕 模式: 从视频生成新字幕')
                    self.process_new_transcription()
                
            except Exception as e:
                import traceback
                self.post(type='error', text=str(e) + "\n" + traceback.format_exc())
        
        def process_new_transcription(self):
            """从视频生成新字幕的原始流程"""
            self.post(type='logs', text='🔧 加载 Faster-Whisper 模型...')
            
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                self.post(type='error', text='未安装 faster-whisper\n请运行: pip install faster-whisper')
                return
            
            self.post(type='logs', text=f'📥 模型: {self.model_size}')
            
            # 显示设备信息
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
                compute_type = "float16"  # MPS 支持 float16
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
                    # faster-whisper 还不支持 MPS，回退到 CPU
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
            self.post(type='logs', text='📊 开始收集词级时间戳...')
            
            # 收集所有词 - 添加进度反馈
            collect_start = time.time()
            all_words = []
            segment_count = 0
            for segment in segments:
                segment_count += 1
                if segment_count % 10 == 0:  # 每10个片段报告一次
                    self.post(type='logs', text=f'   处理片段: {segment_count}...')
                
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        all_words.append({
                            'word': word.word,  # 保留原始空格
                            'start': word.start,
                            'end': word.end
                        })
            
            if not all_words:
                self.post(type='error', text='未检测到任何语音内容')
                return
            
            collect_time = time.time() - collect_start
            self.post(type='logs', text=f'✅ 收集完成！共 {len(all_words)} 个词，{segment_count} 个片段 (耗时: {collect_time:.1f}秒)')
            self.post(type='logs', text='🔄 开始智能断句处理...')
            
            # 智能分割
            split_start = time.time()
            subtitles = self.smart_split_by_words(all_words)
            split_time = time.time() - split_start
            
            self.post(type='logs', text=f'✅ 断句完成！(耗时: {split_time:.1f}秒)')
            
            self.post(type='logs', text=f'✅ 生成 {len(subtitles)} 条字幕')
            
            # 保存
            self.save_srt(subtitles)
            
            self.post(type='logs', text='💾 保存完成')
            self.post(type='ok', text=self.result_file)
        
        def process_with_existing_srt(self):
            """使用现有字幕文件进行重新分割"""
            import time
            import re
            from difflib import SequenceMatcher
            
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
            self.post(type='logs', text='⏳ 此过程可能需要几分钟，请耐心等待...')
            
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
            
            # 对齐原始字幕文本和 whisper 识别的词
            self.post(type='logs', text='🔗 开始文本对齐...')
            aligned_words = self.align_text_with_words(original_text, all_words)
            
            if not aligned_words:
                self.post(type='logs', text='⚠️  文本对齐失败，使用 Whisper 识别的文本')
                aligned_words = all_words
            else:
                self.post(type='logs', text=f'✅ 对齐成功！共 {len(aligned_words)} 个词')
            
            # 使用对齐后的词进行智能分割
            self.post(type='logs', text='✂️  开始智能重新分割...')
            split_start = time.time()
            subtitles = self.smart_split_by_words(aligned_words)
            split_time = time.time() - split_start
            
            self.post(type='logs', text=f'✅ 分割完成！(耗时: {split_time:.1f}秒)')
            self.post(type='logs', text=f'📊 原始字幕: {len(original_subtitles)} 条 → 新字幕: {len(subtitles)} 条')
            
            # 保存
            self.save_srt(subtitles)
            
            self.post(type='logs', text='💾 保存完成')
            self.post(type='ok', text=self.result_file)
        
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
            
            # SRT 格式: 序号 \n 时间 \n 文本 \n 空行
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
            # 格式: 00:00:20,317
            match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp_str)
            if match:
                h, m, s, ms = map(int, match.groups())
                return h * 3600 + m * 60 + s + ms / 1000.0
            return 0.0
        
        def align_text_with_words(self, original_text, whisper_words):
            """将原始字幕文本与 Whisper 的词级时间戳对齐"""
            import re
            from difflib import SequenceMatcher
            
            # 清理文本用于对齐
            def clean_for_alignment(text):
                # 移除多余的空格和标点，统一为小写用于匹配
                text = re.sub(r'\s+', ' ', text)
                text = text.lower().strip()
                return text
            
            # 从 whisper_words 构建识别的文本
            whisper_text = ''.join([w['word'] for w in whisper_words])
            
            # 清理两个文本
            original_clean = clean_for_alignment(original_text)
            whisper_clean = clean_for_alignment(whisper_text)
            
            # 计算文本相似度
            similarity = SequenceMatcher(None, original_clean, whisper_clean).ratio()
            self.post(type='logs', text=f'   文本相似度: {similarity:.2%}')
            
            # 如果相似度太低，返回空表示对齐失败
            if similarity < 0.5:
                self.post(type='logs', text=f'   ⚠️  相似度过低 ({similarity:.2%})，可能不匹配')
                return []
            
            # 尝试简单的词对齐：将原始文本分词，然后映射到 whisper 的词
            # 分割原始文本为词
            original_words = re.findall(r'\S+', original_text)
            
            # 如果原始词数和 whisper 词数相差太大，尝试更智能的对齐
            if abs(len(original_words) - len(whisper_words)) > len(whisper_words) * 0.3:
                self.post(type='logs', text=f'   原始词数: {len(original_words)}, Whisper词数: {len(whisper_words)}')
                # 词数差异较大，使用 whisper 的识别结果
                return []
            
            # 简单映射：尝试将原始词对应到 whisper 词
            aligned = []
            whisper_idx = 0
            
            for orig_word in original_words:
                if whisper_idx >= len(whisper_words):
                    break
                
                # 找到最匹配的 whisper 词
                orig_clean = clean_for_alignment(orig_word)
                best_match_idx = whisper_idx
                best_similarity = 0
                
                # 在当前位置附近搜索（窗口大小为5）
                search_end = min(whisper_idx + 5, len(whisper_words))
                for i in range(whisper_idx, search_end):
                    whisper_clean = clean_for_alignment(whisper_words[i]['word'])
                    sim = SequenceMatcher(None, orig_clean, whisper_clean).ratio()
                    if sim > best_similarity:
                        best_similarity = sim
                        best_match_idx = i
                
                # 如果找到合理的匹配（相似度>0.6），使用原始词，否则使用whisper的词
                if best_similarity > 0.6:
                    aligned.append({
                        'word': orig_word,  # 使用原始文本
                        'start': whisper_words[best_match_idx]['start'],
                        'end': whisper_words[best_match_idx]['end']
                    })
                    whisper_idx = best_match_idx + 1
                else:
                    # 匹配度不高，使用 whisper 的结果
                    aligned.append(whisper_words[whisper_idx])
                    whisper_idx += 1
            
            # 如果对齐结果太少，返回空
            if len(aligned) < len(original_words) * 0.7:
                return []
            
            return aligned

        def smart_split_by_words(self, words):
            """基于词级时间戳和语法规则的智能分割"""
            if not words:
                return []
            
            subtitles = []
            current_words = []
            current_start = words[0]['start']
            total_words = len(words)
            
            # 句子结束标点
            sentence_ends = {'.', '!', '?', '。', '！', '？'}
            # 从句分隔符
            clause_separators = {',', ';', ':', '，', '；', '：'}
            
            # 不应该在这些词后断开（英文）
            bad_break_words_en = {
                # 冠词
                'a', 'an', 'the',
                # 介词
                'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'from', 'about',
                'into', 'through', 'during', 'before', 'after', 'above', 'below',
                'between', 'under', 'over', 'upon', 'within', 'without',
                # 连词
                'and', 'or', 'but', 'so', 'yet', 'nor',
                # 助动词
                'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did',
                'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
                # 限定词
                'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
                'some', 'any', 'all', 'both', 'each', 'every', 'either', 'neither',
                # 否定词
                'not', 'no', "n't",
                # 疑问词
                'who', 'what', 'where', 'when', 'why', 'how', 'which', 'whose',
            }
            
            # 中文不应断开的词
            bad_break_words_zh = {
                '的', '了', '和', '与', '或', '但', '而', '却', '则', '就',
                '在', '于', '从', '向', '对', '把', '被', '给', '让', '使',
                '是', '有', '没', '不', '没有',
                '这', '那', '该', '此', '哪', '什么', '怎么', '为什么',
                '一', '一个', '一些', '所有', '每', '各',
            }
            
            # 合并所有不良断点词
            bad_break_words = bad_break_words_en | bad_break_words_zh
            
            # 进度报告间隔
            report_interval = max(100, total_words // 10)
            
            for i, word in enumerate(words):
                # 定期报告进度
                if i > 0 and i % report_interval == 0:
                    progress = int((i / total_words) * 100)
                    self.post(type='logs', text=f'   断句进度: {progress}% ({i}/{total_words} 词)')
                
                current_words.append(word)
                duration = word['end'] - current_start
                word_text = word['word'].strip()
                
                # 检查是否是不良断点
                def is_bad_break_point():
                    """检查当前位置是否适合断句"""
                    if not word_text:
                        return True
                    
                    # 检查当前词（小写，去除标点）
                    clean_word = word_text.lower().rstrip('.,;:!?').rstrip('，。；：！？')
                    if clean_word in bad_break_words:
                        return True
                    
                    # 检查下一个词是否存在且是连接性词汇
                    if i + 1 < len(words):
                        next_word = words[i + 1]['word'].strip().lower()
                        next_clean = next_word.lstrip().rstrip('.,;:!?').rstrip('，。；：！？')
                        # 如果下一个词是连词或介词，也不宜在此断开
                        if next_clean in {'and', 'or', 'but', 'so', '和', '或', '但'}:
                            return True
                    
                    return False
                
                should_split = False
                
                # 1. 最高优先级：句子结束（必须断开）
                if word_text and word_text[-1] in sentence_ends:
                    should_split = True
                
                # 2. 次优先级：达到限制条件
                elif duration >= self.max_duration or len(current_words) >= self.max_words:
                    # 如果在从句分隔符处，直接断开
                    if word_text and word_text[-1] in clause_separators:
                        should_split = True
                    # 否则需要向前查找最近的合适断点
                    elif len(current_words) >= 3:
                        # 向前查找最多5个词，寻找合适的断点
                        best_split_pos = None
                        for lookback in range(min(5, len(current_words) - 1), 0, -1):
                            check_idx = i - lookback
                            if check_idx < 0:
                                continue
                            
                            check_word = words[check_idx]['word'].strip()
                            check_clean = check_word.lower().rstrip('.,;:!?').rstrip('，。；：！？')
                            
                            # 找到从句分隔符
                            if check_word and check_word[-1] in clause_separators:
                                best_split_pos = lookback
                                break
                            # 找到非不良断点的位置
                            elif check_clean not in bad_break_words:
                                if best_split_pos is None:
                                    best_split_pos = lookback
                        
                        # 如果找到了合适的断点，回退到那个位置
                        if best_split_pos is not None and best_split_pos > 0:
                            # 回退 current_words
                            words_to_keep = current_words[:-best_split_pos]
                            words_to_next = current_words[-best_split_pos:]
                            
                            if words_to_keep:
                                subtitle = {
                                    'start': current_start,
                                    'end': words_to_keep[-1]['end'],
                                    'text': ''.join([w['word'] for w in words_to_keep]).strip(),
                                }
                                subtitles.append(subtitle)
                            
                            # 开始新的字幕
                            current_words = words_to_next
                            if words_to_next:
                                current_start = words_to_next[0]['start']
                            should_split = False  # 已经处理了
                        # 如果确实太长了，即使是不良断点也要断开
                        elif len(current_words) > self.max_words + 5 or duration > self.max_duration * 1.5:
                            should_split = True
                
                # 3. 第三优先级：从句边界且接近限制（提前规划）
                elif len(current_words) >= max(5, int(self.max_words * 0.7)):
                    if word_text and word_text[-1] in clause_separators:
                        if i + 1 < len(words):
                            next_duration = words[i + 1]['end'] - current_start
                            # 如果继续下去会超出限制，提前断开
                            if next_duration > self.max_duration * 0.85:
                                should_split = True
                
                # 执行分割
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
            
            return subtitles
        
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
            tools.show_error(d['text'])
            winobj.startbtn.setText('开始生成' if config.defaulelang == 'zh' else 'Start Generate')
            winobj.startbtn.setDisabled(False)
        elif d['type'] == 'logs':
            current_text = winobj.loglabel.toPlainText()
            winobj.loglabel.setPlainText(current_text + '\n' + d['text'])
        else:
            winobj.has_done = True
            winobj.startbtn.setText('开始生成' if config.defaulelang == 'zh' else 'Start Generate')
            winobj.startbtn.setDisabled(False)
            winobj.resultlabel.setText(d['text'])
            winobj.resultbtn.setDisabled(False)
            winobj.resultinput.setPlainText(Path(winobj.resultlabel.text()).read_text(encoding='utf-8'))
            winobj.loglabel.setPlainText(winobj.loglabel.toPlainText() + '\n\n✅ 生成完成！')

    def toggle_srt_input():
        """切换字幕文件输入框的显示"""
        is_checked = winobj.use_existing_srt_checkbox.isChecked()
        winobj.srtinput.setVisible(is_checked)
        winobj.srtbtn.setVisible(is_checked)
        if not is_checked:
            winobj.srtinput.setText("")
    
    def get_file():
        # 支持视频和音频文件
        formats = ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'mp3', 'wav', 'flac', 'm4a']
        format_str = ' '.join([f'*.{f}' for f in formats])
        fname, _ = QFileDialog.getOpenFileName(
            winobj, 
            "选择视频或音频文件",
            config.params['last_opendir'],
            f"Video/Audio files({format_str})"
        )
        if fname:
            winobj.videoinput.setText(fname.replace('file:///', '').replace('\\', '/'))
    
    def get_srt_file():
        """选择字幕文件"""
        fname, _ = QFileDialog.getOpenFileName(
            winobj,
            "选择字幕文件" if config.defaulelang == 'zh' else 'Select Subtitle File',
            config.params['last_opendir'],
            "Subtitle files(*.srt)"
        )
        if fname:
            winobj.srtinput.setText(fname.replace('file:///', '').replace('\\', '/'))

    def start():
        winobj.has_done = False
        video_file = winobj.videoinput.text()
        if not video_file:
            tools.show_error(
                '必须选择视频或音频文件' if config.defaulelang == 'zh' else 'Video/audio file must be selected',
                False)
            return
        
        # 检查是否使用现有字幕
        existing_srt = None
        if winobj.use_existing_srt_checkbox.isChecked():
            existing_srt = winobj.srtinput.text()
            if not existing_srt:
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

        winobj.startbtn.setText('生成中...' if config.defaulelang == 'zh' else 'Generating...')
        winobj.startbtn.setDisabled(True)
        winobj.resultbtn.setDisabled(True)
        winobj.resultinput.setPlainText("")
        winobj.loglabel.setPlainText("🚀 开始处理..." if config.defaulelang == 'zh' else '🚀 Starting...')

        task = SmartSplitThread(
            parent=winobj,
            video_file=video_file,
            language=language,
            model_size=model_size,
            max_duration=max_duration,
            max_words=max_words,
            device=device,
            existing_srt=existing_srt
        )
        task.uito.connect(feed)
        task.start()

    def opendir():
        QDesktopServices.openUrl(QUrl.fromLocalFile(RESULT_DIR))

    from videotrans.component import SmartSplitForm
    try:
        winobj = config.child_forms.get('smartsplitw')
        if winobj is not None:
            winobj.show()
            winobj.raise_()
            winobj.activateWindow()
            return
        winobj = SmartSplitForm()
        config.child_forms['smartsplitw'] = winobj
        winobj.videobtn.clicked.connect(get_file)
        winobj.srtbtn.clicked.connect(get_srt_file)
        winobj.use_existing_srt_checkbox.stateChanged.connect(toggle_srt_input)
        winobj.resultbtn.clicked.connect(opendir)
        winobj.startbtn.clicked.connect(start)
        winobj.show()
    except Exception as e:
        import traceback
        print(traceback.format_exc())

