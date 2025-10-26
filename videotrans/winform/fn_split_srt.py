# 字幕断句工具 - 智能分割长字幕
def openwin():
    import json
    import re
    from pathlib import Path

    from PySide6.QtCore import QThread, Signal, QUrl
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtWidgets import QFileDialog

    from videotrans.configure import config
    from videotrans.util import tools
    RESULT_DIR = config.HOME_DIR + "/SplitSrt"
    Path(RESULT_DIR).mkdir(exist_ok=True)

    def time_to_ms(time_str):
        """将时间字符串转换为毫秒"""
        h, m, s = time_str.split(':')
        s, ms = s.split(',')
        return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

    def ms_to_time(ms):
        """将毫秒转换为时间字符串"""
        h = ms // 3600000
        m = (ms % 3600000) // 60000
        s = (ms % 60000) // 1000
        ms_part = ms % 1000
        return f"{h:02d}:{m:02d}:{s:02d},{ms_part:03d}"

    def split_by_sentences(text):
        """将文本按句子分割"""
        sentences = []
        
        # 分割模式：句号、问号、感叹号后面跟空格或结尾
        pattern = r'([^.!?。！？]+[.!?。！？]+\s*)'
        matches = re.findall(pattern, text)
        
        if matches:
            sentences = [m.strip() for m in matches if m.strip()]
            # 检查是否有剩余文本（没有结束标点的部分）
            remaining = re.sub(pattern, '', text).strip()
            if remaining:
                sentences.append(remaining)
        else:
            # 如果没有明确的句子分隔符，尝试按逗号或其他标点分割
            if len(text) > 100:
                # 按逗号、分号等分割
                parts = re.split(r'[,，;；]\s*', text)
                sentences = [p.strip() for p in parts if p.strip()]
            else:
                sentences = [text]
        
        return sentences

    def smart_split_subtitles(subtitles, max_duration_ms=3000):
        """智能分割字幕"""
        new_subtitles = []
        new_index = 1
        
        for sub in subtitles:
            duration = sub['end_ms'] - sub['start_ms']
            text = sub['text']
            
            # 如果持续时间较短，直接保留
            if duration <= max_duration_ms:
                new_subtitles.append({
                    'index': str(new_index),
                    'start': sub['start'],
                    'end': sub['end'],
                    'text': text,
                    'start_ms': sub['start_ms'],
                    'end_ms': sub['end_ms']
                })
                new_index += 1
                continue
            
            # 如果持续时间较长，需要分割
            sentences = split_by_sentences(text)
            
            if len(sentences) <= 1:
                # 无法分割，保留原样
                new_subtitles.append({
                    'index': str(new_index),
                    'start': sub['start'],
                    'end': sub['end'],
                    'text': text,
                    'start_ms': sub['start_ms'],
                    'end_ms': sub['end_ms']
                })
                new_index += 1
                continue
            
            # 按句子数量平均分配时间
            time_per_sentence = duration / len(sentences)
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                # 计算这个句子的开始和结束时间
                sentence_start_ms = sub['start_ms'] + int(i * time_per_sentence)
                sentence_end_ms = sub['start_ms'] + int((i + 1) * time_per_sentence)
                
                # 确保最后一个句子的结束时间与原字幕一致
                if i == len(sentences) - 1:
                    sentence_end_ms = sub['end_ms']
                
                new_subtitles.append({
                    'index': str(new_index),
                    'start': ms_to_time(sentence_start_ms),
                    'end': ms_to_time(sentence_end_ms),
                    'text': sentence.strip(),
                    'start_ms': sentence_start_ms,
                    'end_ms': sentence_end_ms
                })
                new_index += 1
        
        return new_subtitles

    class SplitThread(QThread):
        uito = Signal(str)

        def __init__(self, *, parent=None, srt_file=None, max_duration=3):
            super().__init__(parent=parent)
            self.srt_file = srt_file
            self.max_duration = max_duration
            self.result_file = RESULT_DIR + "/" + Path(srt_file).stem + '_split.srt'

        def post(self, type='logs', text=""):
            self.uito.emit(json.dumps({"type": type, "text": text}))

        def run(self):
            try:
                self.post(type='logs', text='正在读取字幕文件...' if config.defaulelang == 'zh' else 'Reading subtitle file...')
                
                # 解析字幕
                subtitles = tools.get_subtitle_from_srt(self.srt_file)
                original_count = len(subtitles)
                
                self.post(type='logs', text=f'原始字幕条目: {original_count}')
                self.post(type='logs', text='正在智能分割...' if config.defaulelang == 'zh' else 'Smart splitting...')
                
                # 转换为分割函数需要的格式
                srt_list = []
                for sub in subtitles:
                    srt_list.append({
                        'index': str(sub['line']),
                        'start': sub['startraw'],
                        'end': sub['endraw'],
                        'text': sub['text'],
                        'start_ms': sub['start_time'],
                        'end_ms': sub['end_time']
                    })
                
                # 智能分割
                new_subtitles = smart_split_subtitles(srt_list, max_duration_ms=int(self.max_duration * 1000))
                new_count = len(new_subtitles)
                
                self.post(type='logs', text=f'分割后字幕条目: {new_count}')
                self.post(type='logs', text='正在保存...' if config.defaulelang == 'zh' else 'Saving...')
                
                # 保存
                with open(self.result_file, 'w', encoding='utf-8') as f:
                    for sub in new_subtitles:
                        f.write(f"{sub['index']}\n")
                        f.write(f"{sub['start']} --> {sub['end']}\n")
                        f.write(f"{sub['text']}\n")
                        f.write("\n")
                
                self.post(type='ok', text=self.result_file)
            except Exception as e:
                import traceback
                self.post(type='error', text=str(e) + "\n" + traceback.format_exc())

    def feed(d):
        if winobj.has_done:
            return
        d = json.loads(d)
        if d['type'] == "error":
            winobj.has_done = True
            winobj.loglabel.setPlainText(d['text'])
            tools.show_error(d['text'])
            winobj.startbtn.setText('开始分割' if config.defaulelang == 'zh' else 'Start Split')
            winobj.startbtn.setDisabled(False)
        elif d['type'] == 'logs':
            current_text = winobj.loglabel.toPlainText()
            winobj.loglabel.setPlainText(current_text + '\n' + d['text'])
        else:
            winobj.has_done = True
            winobj.startbtn.setText('开始分割' if config.defaulelang == 'zh' else 'Start Split')
            winobj.startbtn.setDisabled(False)
            winobj.resultlabel.setText(d['text'])
            winobj.resultbtn.setDisabled(False)
            winobj.resultinput.setPlainText(Path(winobj.resultlabel.text()).read_text(encoding='utf-8'))
            winobj.loglabel.setPlainText(winobj.loglabel.toPlainText() + '\n\n✅ 分割完成！')

    def get_file():
        fname, _ = QFileDialog.getOpenFileName(winobj, "选择字幕文件", config.params['last_opendir'],
                                               "SRT files(*.srt)")
        if fname:
            winobj.srtinput.setText(fname.replace('file:///', '').replace('\\', '/'))

    def start():
        winobj.has_done = False
        srt = winobj.srtinput.text()
        if not srt:
            tools.show_error(
                '必须选择字幕文件' if config.defaulelang == 'zh' else 'Subtitle file must be selected',
                False)
            return
        
        # 获取最大持续时间
        try:
            max_duration = float(winobj.duration_input.text())
            if max_duration <= 0:
                raise ValueError
        except:
            tools.show_error(
                '最大持续时间必须是正数' if config.defaulelang == 'zh' else 'Max duration must be a positive number',
                False)
            return

        winobj.startbtn.setText('分割中...' if config.defaulelang == 'zh' else 'Splitting...')
        winobj.startbtn.setDisabled(True)
        winobj.resultbtn.setDisabled(True)
        winobj.resultinput.setPlainText("")
        winobj.loglabel.setPlainText("开始处理..." if config.defaulelang == 'zh' else 'Starting...')

        task = SplitThread(parent=winobj, srt_file=srt, max_duration=max_duration)
        task.uito.connect(feed)
        task.start()

    def opendir():
        QDesktopServices.openUrl(QUrl.fromLocalFile(RESULT_DIR))

    from videotrans.component import SplitSrtForm
    try:
        winobj = config.child_forms.get('splitw')
        if winobj is not None:
            winobj.show()
            winobj.raise_()
            winobj.activateWindow()
            return
        winobj = SplitSrtForm()
        config.child_forms['splitw'] = winobj
        winobj.srtbtn.clicked.connect(get_file)
        winobj.resultbtn.clicked.connect(opendir)
        winobj.startbtn.clicked.connect(start)
        winobj.show()
    except Exception as e:
        import traceback
        print(traceback.format_exc())

