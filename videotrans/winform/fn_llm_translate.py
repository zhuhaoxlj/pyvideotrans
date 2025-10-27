# LLM字幕翻译功能
def openwin():
    import json
    from pathlib import Path

    from PySide6.QtCore import QThread, Signal, QUrl
    from PySide6.QtGui import QDesktopServices, QTextCursor
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    from videotrans.configure import config
    from videotrans.util import tools
    
    RESULT_DIR = config.HOME_DIR + "/LLMTranslate"
    Path(RESULT_DIR).mkdir(exist_ok=True)

    class LLMTranslateThread(QThread):
        uito = Signal(str)

        def __init__(self, *, parent=None, srt_file=None, source_lang='auto', target_lang='en',
                     llm_provider='openai', llm_api_key='', llm_model='gpt-4o-mini', 
                     llm_base_url='', batch_size=10, proxy='', bilingual=False):
            super().__init__(parent=parent)
            self.srt_file = srt_file
            self.source_lang = source_lang
            self.target_lang = target_lang
            
            # LLM 配置
            self.llm_provider = llm_provider
            self.llm_api_key = llm_api_key
            self.llm_model = llm_model
            self.llm_base_url = llm_base_url
            self.batch_size = batch_size
            self.proxy = proxy
            self.bilingual = bilingual  # 是否生成双语字幕
            
            bilingual_suffix = "_bilingual" if bilingual else ""
            self.result_file = RESULT_DIR + "/" + Path(srt_file).stem + f"_translated_{target_lang}{bilingual_suffix}.srt"
            self.stop_flag = False

        def post(self, type='logs', text=""):
            self.uito.emit(json.dumps({"type": type, "text": text}))
        
        def stop(self):
            self.stop_flag = True
        
        def run(self):
            try:
                self.post(type='logs', text='⏳ 开始翻译...')
                
                # 读取字幕文件
                self.post(type='logs', text=f'📖 读取字幕文件: {Path(self.srt_file).name}')
                subtitles = self.parse_srt(self.srt_file)
                
                if not subtitles:
                    self.post(type='error', text='❌ 字幕文件为空或格式不正确')
                    return
                
                self.post(type='set_source', text=Path(self.srt_file).read_text(encoding='utf-8'))
                self.post(type='clear_target')
                
                self.post(type='logs', text=f'📝 共 {len(subtitles)} 条字幕待翻译')
                
                # 初始化 LLM 翻译器
                translator = self.init_translator()
                if not translator:
                    self.post(type='error', text='❌ 初始化翻译器失败')
                    return
                
                # 分批翻译
                translated_subtitles = []
                total_batches = (len(subtitles) + self.batch_size - 1) // self.batch_size
                
                for i in range(0, len(subtitles), self.batch_size):
                    if self.stop_flag:
                        self.post(type='logs', text='⏹ 翻译已停止')
                        return
                    
                    batch = subtitles[i:i + self.batch_size]
                    batch_num = i // self.batch_size + 1
                    
                    self.post(type='logs', text=f'🔄 正在翻译第 {batch_num}/{total_batches} 批...')
                    
                    # 提取文本进行翻译
                    texts_to_translate = [sub['text'] for sub in batch]
                    
                    try:
                        translated_texts = self.translate_batch(translator, texts_to_translate)
                        
                        # 更新字幕
                        for j, translated_text in enumerate(translated_texts):
                            if j < len(batch):
                                translated_sub = batch[j].copy()
                                original_text = translated_sub['text']
                                
                                # 根据是否双语字幕来决定文本格式
                                if self.bilingual:
                                    # 双语字幕：原文 + 换行 + 译文
                                    translated_sub['text'] = f"{original_text}\n{translated_text}"
                                else:
                                    # 单语字幕：只保留译文
                                    translated_sub['text'] = translated_text
                                
                                translated_subtitles.append(translated_sub)
                                
                                # 实时显示翻译结果
                                self.post(type='subtitle', text=f"{translated_sub['index']}\n{translated_sub['time']}\n{translated_sub['text']}\n\n")
                        
                        progress = int((batch_num / total_batches) * 100)
                        self.post(type='logs', text=f'✅ 第 {batch_num}/{total_batches} 批完成 ({progress}%)')
                        
                    except Exception as e:
                        error_msg = f'❌ 第 {batch_num} 批翻译失败: {str(e)}'
                        self.post(type='logs', text=error_msg)
                        config.logger.error(error_msg)
                        # 失败时保留原文
                        for sub in batch:
                            translated_subtitles.append(sub)
                
                if self.stop_flag:
                    self.post(type='logs', text='⏹ 翻译已停止')
                    return
                
                # 保存结果
                self.post(type='logs', text=f'💾 保存翻译结果: {Path(self.result_file).name}')
                self.save_srt(translated_subtitles, self.result_file)
                
                self.post(type='succeed', text=f'✅ 翻译完成！结果已保存到: {self.result_file}')
                
            except Exception as e:
                error_msg = f'❌ 翻译过程出错: {str(e)}'
                self.post(type='error', text=error_msg)
                config.logger.error(error_msg, exc_info=True)
        
        def parse_srt(self, srt_file):
            """解析 SRT 文件"""
            try:
                content = Path(srt_file).read_text(encoding='utf-8')
                subtitles = []
                
                # 按空行分割
                blocks = content.strip().split('\n\n')
                
                for block in blocks:
                    lines = block.strip().split('\n')
                    if len(lines) >= 3:
                        try:
                            index = lines[0].strip()
                            time = lines[1].strip()
                            text = '\n'.join(lines[2:]).strip()
                            
                            subtitles.append({
                                'index': index,
                                'time': time,
                                'text': text
                            })
                        except Exception as e:
                            config.logger.warning(f'解析字幕块失败: {block}, 错误: {e}')
                            continue
                
                return subtitles
            except Exception as e:
                config.logger.error(f'解析 SRT 文件失败: {e}', exc_info=True)
                return []
        
        def save_srt(self, subtitles, output_file):
            """保存为 SRT 文件"""
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    for sub in subtitles:
                        f.write(f"{sub['index']}\n")
                        f.write(f"{sub['time']}\n")
                        f.write(f"{sub['text']}\n\n")
            except Exception as e:
                config.logger.error(f'保存 SRT 文件失败: {e}', exc_info=True)
                raise
        
        def init_translator(self):
            """初始化翻译器"""
            try:
                if self.llm_provider == 'openai':
                    return self.init_openai_translator()
                elif self.llm_provider in ['claude', 'anthropic']:
                    return self.init_claude_translator()
                elif self.llm_provider == 'gemini':
                    return self.init_gemini_translator()
                elif self.llm_provider == 'deepseek':
                    return self.init_deepseek_translator()
                elif self.llm_provider == 'siliconflow':
                    return self.init_siliconflow_translator()
                else:
                    self.post(type='error', text=f'❌ 不支持的LLM提供商: {self.llm_provider}')
                    return None
            except Exception as e:
                config.logger.error(f'初始化翻译器失败: {e}', exc_info=True)
                return None
        
        def init_openai_translator(self):
            """初始化 OpenAI 翻译器"""
            import httpx
            from openai import OpenAI
            
            api_url = self.llm_base_url if self.llm_base_url else "https://api.openai.com/v1"
            
            # 自动修正 API 地址：移除末尾的 /chat/completions（如果有）
            # 因为 OpenAI SDK 会自动添加这个路径
            if api_url.endswith('/chat/completions'):
                api_url = api_url[:-len('/chat/completions')]
                config.logger.info(f'自动修正 API 地址: {api_url}')
            
            proxy = self.proxy if self.proxy else None
            
            http_client = httpx.Client(proxy=proxy, timeout=300) if proxy else httpx.Client(timeout=300)
            
            client = OpenAI(
                api_key=self.llm_api_key,
                base_url=api_url,
                http_client=http_client
            )
            
            return {
                'type': 'openai',
                'client': client,
                'model': self.llm_model
            }
        
        def init_claude_translator(self):
            """初始化 Claude 翻译器"""
            import anthropic
            
            client = anthropic.Anthropic(
                api_key=self.llm_api_key,
            )
            
            return {
                'type': 'claude',
                'client': client,
                'model': self.llm_model
            }
        
        def init_gemini_translator(self):
            """初始化 Gemini 翻译器"""
            import google.generativeai as genai
            
            genai.configure(api_key=self.llm_api_key)
            model = genai.GenerativeModel(self.llm_model)
            
            return {
                'type': 'gemini',
                'model': model
            }
        
        def init_deepseek_translator(self):
            """初始化 DeepSeek 翻译器"""
            import httpx
            from openai import OpenAI
            
            api_url = self.llm_base_url if self.llm_base_url else "https://api.deepseek.com/v1"
            
            # 自动修正 API 地址：移除末尾的 /chat/completions（如果有）
            # 因为 OpenAI SDK 会自动添加这个路径
            if api_url.endswith('/chat/completions'):
                api_url = api_url[:-len('/chat/completions')]
                config.logger.info(f'自动修正 DeepSeek API 地址: {api_url}')
            
            proxy = self.proxy if self.proxy else None
            
            http_client = httpx.Client(proxy=proxy, timeout=300) if proxy else httpx.Client(timeout=300)
            
            client = OpenAI(
                api_key=self.llm_api_key,
                base_url=api_url,
                http_client=http_client
            )
            
            return {
                'type': 'deepseek',
                'client': client,
                'model': self.llm_model
            }
        
        def init_siliconflow_translator(self):
            """初始化 SiliconFlow 翻译器"""
            import httpx
            from openai import OpenAI
            
            api_url = self.llm_base_url if self.llm_base_url else "https://api.siliconflow.cn/v1"
            
            # 自动修正 API 地址：移除末尾的 /chat/completions（如果有）
            # 因为 OpenAI SDK 会自动添加这个路径
            if api_url.endswith('/chat/completions'):
                api_url = api_url[:-len('/chat/completions')]
                config.logger.info(f'自动修正 SiliconFlow API 地址: {api_url}')
            
            proxy = self.proxy if self.proxy else None
            
            http_client = httpx.Client(proxy=proxy, timeout=300) if proxy else httpx.Client(timeout=300)
            
            client = OpenAI(
                api_key=self.llm_api_key,
                base_url=api_url,
                http_client=http_client
            )
            
            return {
                'type': 'siliconflow',
                'client': client,
                'model': self.llm_model
            }
        
        def translate_batch(self, translator, texts):
            """批量翻译文本"""
            if translator['type'] in ['openai', 'deepseek', 'siliconflow']:
                return self.translate_with_openai(translator, texts)
            elif translator['type'] in ['claude', 'anthropic']:
                return self.translate_with_claude(translator, texts)
            elif translator['type'] == 'gemini':
                return self.translate_with_gemini(translator, texts)
            else:
                raise ValueError(f'不支持的翻译器类型: {translator["type"]}')
        
        def translate_with_openai(self, translator, texts):
            """使用 OpenAI API 翻译"""
            # 构建提示词
            source_lang_name = self.get_language_name(self.source_lang)
            target_lang_name = self.get_language_name(self.target_lang)
            
            prompt = f"""你是一个专业的字幕翻译助手。请将以下字幕从{source_lang_name}翻译成{target_lang_name}。

要求：
1. 保持原有的行数和格式
2. 翻译要准确、流畅、自然
3. 保留专有名词的原文
4. 每行翻译结果用换行符分隔
5. 不要添加任何序号、注释或额外的说明

待翻译的字幕（每行一条）：
"""
            
            for i, text in enumerate(texts, 1):
                prompt += f"{text}\n"
            
            prompt += "\n请直接输出翻译结果，每行对应一条翻译，不要包含任何其他内容："
            
            # 调用 API
            client = translator['client']
            model = translator['model']
            
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的字幕翻译助手，擅长准确、流畅地翻译字幕。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4096
                )
                
                result = response.choices[0].message.content.strip()
                
                # 解析结果
                translated_lines = result.split('\n')
                translated_lines = [line.strip() for line in translated_lines if line.strip()]
                
                # 确保结果行数匹配
                if len(translated_lines) < len(texts):
                    translated_lines += [''] * (len(texts) - len(translated_lines))
                elif len(translated_lines) > len(texts):
                    translated_lines = translated_lines[:len(texts)]
                
                return translated_lines
                
            except Exception as e:
                config.logger.error(f'OpenAI 翻译失败: {e}', exc_info=True)
                raise
        
        def translate_with_claude(self, translator, texts):
            """使用 Claude API 翻译"""
            source_lang_name = self.get_language_name(self.source_lang)
            target_lang_name = self.get_language_name(self.target_lang)
            
            prompt = f"""你是一个专业的字幕翻译助手。请将以下字幕从{source_lang_name}翻译成{target_lang_name}。

要求：
1. 保持原有的行数和格式
2. 翻译要准确、流畅、自然
3. 保留专有名词的原文
4. 每行翻译结果用换行符分隔
5. 不要添加任何序号、注释或额外的说明

待翻译的字幕（每行一条）：
"""
            
            for i, text in enumerate(texts, 1):
                prompt += f"{text}\n"
            
            prompt += "\n请直接输出翻译结果，每行对应一条翻译，不要包含任何其他内容："
            
            # 调用 API
            client = translator['client']
            model = translator['model']
            
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                
                result = response.content[0].text.strip()
                
                # 解析结果
                translated_lines = result.split('\n')
                translated_lines = [line.strip() for line in translated_lines if line.strip()]
                
                # 确保结果行数匹配
                if len(translated_lines) < len(texts):
                    translated_lines += [''] * (len(texts) - len(translated_lines))
                elif len(translated_lines) > len(texts):
                    translated_lines = translated_lines[:len(texts)]
                
                return translated_lines
                
            except Exception as e:
                config.logger.error(f'Claude 翻译失败: {e}', exc_info=True)
                raise
        
        def translate_with_gemini(self, translator, texts):
            """使用 Gemini API 翻译"""
            source_lang_name = self.get_language_name(self.source_lang)
            target_lang_name = self.get_language_name(self.target_lang)
            
            prompt = f"""你是一个专业的字幕翻译助手。请将以下字幕从{source_lang_name}翻译成{target_lang_name}。

要求：
1. 保持原有的行数和格式
2. 翻译要准确、流畅、自然
3. 保留专有名词的原文
4. 每行翻译结果用换行符分隔
5. 不要添加任何序号、注释或额外的说明

待翻译的字幕（每行一条）：
"""
            
            for i, text in enumerate(texts, 1):
                prompt += f"{text}\n"
            
            prompt += "\n请直接输出翻译结果，每行对应一条翻译，不要包含任何其他内容："
            
            # 调用 API
            model = translator['model']
            
            try:
                response = model.generate_content(prompt)
                result = response.text.strip()
                
                # 解析结果
                translated_lines = result.split('\n')
                translated_lines = [line.strip() for line in translated_lines if line.strip()]
                
                # 确保结果行数匹配
                if len(translated_lines) < len(texts):
                    translated_lines += [''] * (len(texts) - len(translated_lines))
                elif len(translated_lines) > len(texts):
                    translated_lines = translated_lines[:len(texts)]
                
                return translated_lines
                
            except Exception as e:
                config.logger.error(f'Gemini 翻译失败: {e}', exc_info=True)
                raise
        
        def get_language_name(self, lang_code):
            """获取语言名称"""
            lang_map = {
                'auto': '自动检测',
                'zh': '中文',
                'en': '英语',
                'ja': '日语',
                'ko': '韩语',
                'fr': '法语',
                'de': '德语',
                'es': '西班牙语',
                'it': '意大利语',
                'pt': '葡萄牙语',
                'ru': '俄语',
                'ar': '阿拉伯语',
                'th': '泰语',
                'vi': '越南语',
                'id': '印度尼西亚语',
                'tr': '土耳其语',
                'pl': '波兰语',
                'nl': '荷兰语',
            }
            return lang_map.get(lang_code, lang_code)

    def feed(d):
        if winobj.has_done:
            return
        d = json.loads(d)
        
        if d['type'] == 'error':
            winobj.has_done = True
            winobj.progress_label.setStyleSheet("QLabel { color: #f44336; font-weight: bold; padding: 5px; }")
            winobj.progress_label.setText(d['text'])
            winobj.start_btn.setDisabled(False)
            winobj.stop_btn.setDisabled(True)
            QMessageBox.critical(winobj, "错误" if config.defaulelang == 'zh' else "Error", d['text'])
        
        elif d['type'] == 'subtitle':
            # 实时显示翻译结果
            winobj.target_text.moveCursor(QTextCursor.End)
            winobj.target_text.insertPlainText(d['text'])
        
        elif d['type'] == 'set_source':
            winobj.source_text.setPlainText(d['text'])
        
        elif d['type'] == 'clear_target':
            winobj.target_text.clear()
        
        elif d['type'] == 'succeed':
            winobj.has_done = True
            winobj.progress_label.setStyleSheet("QLabel { color: #4caf50; font-weight: bold; padding: 5px; }")
            winobj.progress_label.setText(d['text'])
            winobj.start_btn.setDisabled(False)
            winobj.stop_btn.setDisabled(True)
            QMessageBox.information(winobj, "成功" if config.defaulelang == 'zh' else "Success", d['text'])
        
        elif d['type'] == 'logs':
            winobj.progress_label.setStyleSheet("QLabel { color: #2196f3; font-weight: bold; padding: 5px; }")
            winobj.progress_label.setText(d['text'])

    def select_file_fun():
        """选择字幕文件"""
        fname, _ = QFileDialog.getOpenFileName(
            winobj,
            "选择字幕文件" if config.defaulelang == 'zh' else "Select Subtitle File",
            config.params.get('last_opendir', ''),
            "Subtitle files (*.srt)"
        )
        
        if fname:
            winobj.selected_file = fname
            config.params['last_opendir'] = str(Path(fname).parent)
            winobj.selected_file_label.setText(f"已选择: {Path(fname).name}")
            winobj.selected_file_label.setStyleSheet("QLabel { color: #4caf50; padding: 5px; }")
            
            # 读取并显示原文
            try:
                content = Path(fname).read_text(encoding='utf-8')
                winobj.source_text.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(winobj, "警告" if config.defaulelang == 'zh' else "Warning", 
                                  f"读取文件失败: {str(e)}")

    def start_translate_fun():
        """开始翻译"""
        # 验证输入
        if not hasattr(winobj, 'selected_file') or not winobj.selected_file:
            QMessageBox.warning(winobj, "警告" if config.defaulelang == 'zh' else "Warning",
                              "请先选择字幕文件" if config.defaulelang == 'zh' else "Please select a subtitle file first")
            return
        
        api_key = winobj.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(winobj, "警告" if config.defaulelang == 'zh' else "Warning",
                              "请输入 API Key" if config.defaulelang == 'zh' else "Please enter API Key")
            return
        
        target_lang = winobj.target_lang_combo.currentData()
        if not target_lang or target_lang == 'auto':
            QMessageBox.warning(winobj, "警告" if config.defaulelang == 'zh' else "Warning",
                              "请选择目标语言" if config.defaulelang == 'zh' else "Please select target language")
            return
        
        # 清空结果
        winobj.target_text.clear()
        winobj.has_done = False
        
        # 获取双语字幕选项
        bilingual = winobj.bilingual_checkbox.isChecked()
        
        # 创建翻译线程
        winobj.translate_thread = LLMTranslateThread(
            parent=winobj,
            srt_file=winobj.selected_file,
            source_lang=winobj.source_lang_combo.currentData(),
            target_lang=target_lang,
            llm_provider=winobj.provider_combo.currentData(),
            llm_api_key=api_key,
            llm_model=winobj.model_combo.currentText(),
            llm_base_url=winobj.base_url_input.text().strip(),
            batch_size=winobj.batch_size_spin.value(),
            proxy=winobj.proxy_input.text().strip(),
            bilingual=bilingual
        )
        
        winobj.translate_thread.uito.connect(feed)
        winobj.translate_thread.start()
        
        winobj.start_btn.setDisabled(True)
        winobj.stop_btn.setDisabled(False)
        winobj.progress_label.setText("翻译中..." if config.defaulelang == 'zh' else "Translating...")

    def stop_translate_fun():
        """停止翻译"""
        if hasattr(winobj, 'translate_thread') and winobj.translate_thread.isRunning():
            winobj.translate_thread.stop()
            winobj.start_btn.setDisabled(False)
            winobj.stop_btn.setDisabled(True)

    def open_result_fun():
        """打开结果文件夹"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(RESULT_DIR))

    def save_api_key_to_env():
        """保存 API Key 到 .env 文件，并保存配置到 config.params"""
        import os
        provider = winobj.provider_combo.currentData()
        api_key = winobj.api_key_input.text().strip()
        if not api_key:
            return
        
        env_file = os.path.join(config.ROOT_DIR, '.env')
        
        # 根据提供商确定环境变量名称
        env_key_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'gemini': 'GEMINI_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'siliconflow': 'SILICONFLOW_API_KEY',
        }
        env_key_name = env_key_map.get(provider, 'LLM_API_KEY')
        
        # 读取现有的 .env 文件内容
        lines = []
        key_exists = False
        
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 查找并更新对应的 API Key
                for i, line in enumerate(lines):
                    if line.strip().startswith(f'{env_key_name}='):
                        lines[i] = f'{env_key_name}={api_key}\n'
                        key_exists = True
                        break
            except Exception as e:
                config.logger.warning(f"读取 .env 文件失败: {e}")
        
        # 如果 key 不存在，添加到文件末尾
        if not key_exists:
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            lines.append(f'{env_key_name}={api_key}\n')
        
        # 写回文件
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            config.logger.info(f"API Key 已保存到 {env_file}")
        except Exception as e:
            config.logger.error(f"保存 API Key 失败: {e}")
    
    def save_llm_config():
        """保存 LLM 配置到 config.params，与智能分割字幕共享"""
        provider = winobj.provider_combo.currentData()
        model = winobj.model_combo.currentText()
        base_url = winobj.base_url_input.text().strip()
        
        # 保存到 config.params，与智能分割字幕共享
        config.params['llm_provider'] = provider
        config.params['llm_model'] = model
        config.params['llm_base_url'] = base_url
        config.getset_params(config.params)
    
    def save_bilingual_config():
        """保存双语字幕配置"""
        config.params['llm_translate_bilingual'] = winobj.bilingual_checkbox.isChecked()
        config.getset_params(config.params)
    
    def load_api_key_from_env():
        """从 .env 文件加载 API Key"""
        import os
        provider = winobj.provider_combo.currentData()
        
        # 根据提供商确定环境变量名称
        env_key_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'gemini': 'GEMINI_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'siliconflow': 'SILICONFLOW_API_KEY',
        }
        env_key_name = env_key_map.get(provider, 'LLM_API_KEY')
        
        api_key = ""
        # 首先尝试从环境变量读取
        api_key = os.environ.get(env_key_name, '')
        
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
                                    if key == env_key_name:
                                        api_key = value
                                        break
                except Exception as e:
                    config.logger.warning(f"读取 .env 文件失败: {e}")
        
        # 设置到输入框
        if api_key:
            winobj.api_key_input.setText(api_key)
    
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
                        'Content-Type': 'application/json',
                        'anthropic-version': '2023-06-01'
                    }
                    data = {
                        'model': self.model,
                        'messages': [{'role': 'user', 'content': test_prompt}],
                        'max_tokens': 10
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
                
                else:
                    self.finished.emit(f'❌ 不支持的提供商: {self.provider}', False)
                    return
                
                # 发送进度更新
                self.progress.emit(f'🌐 正在连接到 {self.provider} API...' if config.defaulelang == 'zh' else f'🌐 Connecting to {self.provider} API...')
                
                # 发送请求
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
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
                    
                    elif self.provider in ['anthropic', 'claude']:
                        if 'content' in result:
                            success_msg = f'✅ 连接成功！提供商: {self.provider} | 模型: {self.model} | 响应正常' if config.defaulelang == 'zh' else f'✅ Connection Successful! Provider: {self.provider} | Model: {self.model} | Response OK'
                            self.finished.emit(success_msg, True)
                        else:
                            self.finished.emit('响应格式不正确' if config.defaulelang == 'zh' else 'Invalid response format', False)
                    
                    elif self.provider == 'gemini':
                        # Gemini 的响应格式不同，但200状态码表示成功
                        success_msg = f'✅ 连接成功！提供商: {self.provider} | 模型: {self.model} | 响应正常' if config.defaulelang == 'zh' else f'✅ Connection Successful! Provider: {self.provider} | Model: {self.model} | Response OK'
                        self.finished.emit(success_msg, True)
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
        provider = winobj.provider_combo.currentData()
        api_key = winobj.api_key_input.text()
        model = winobj.model_combo.currentText()
        base_url = winobj.base_url_input.text()
        
        # 验证必填项
        if not api_key:
            msg = '❌ 请输入 API Key' if config.defaulelang == 'zh' else '❌ Please enter API Key'
            winobj.progress_label.setText(msg)
            winobj.progress_label.setStyleSheet("QLabel { color: #f44336; font-weight: bold; padding: 5px; }")
            return
        
        if not model:
            msg = '❌ 请选择模型' if config.defaulelang == 'zh' else '❌ Please select model'
            winobj.progress_label.setText(msg)
            winobj.progress_label.setStyleSheet("QLabel { color: #f44336; font-weight: bold; padding: 5px; }")
            return
        
        # 禁用按钮
        winobj.test_btn.setDisabled(True)
        winobj.test_btn.setText('⏳ 测试中' if config.defaulelang == 'zh' else '⏳ Testing')
        
        # 创建并启动测试线程
        test_thread = TestLLMThread(provider, api_key, model, base_url)
        
        def on_test_progress(message):
            """进度更新的回调"""
            winobj.progress_label.setText(message)
            winobj.progress_label.setStyleSheet("QLabel { color: #2196f3; font-weight: bold; padding: 5px; }")
        
        def on_test_finished(message, success):
            """测试完成的回调"""
            winobj.progress_label.setText(message)
            if success:
                winobj.progress_label.setStyleSheet("QLabel { color: #4caf50; font-weight: bold; padding: 5px; }")
            else:
                winobj.progress_label.setStyleSheet("QLabel { color: #f44336; font-weight: bold; padding: 5px; }")
            
            # 恢复按钮状态
            winobj.test_btn.setDisabled(False)
            winobj.test_btn.setText('🔍 测试连接' if config.defaulelang == 'zh' else '🔍 Test Connection')
        
        test_thread.progress.connect(on_test_progress)
        test_thread.finished.connect(on_test_finished)
        test_thread.start()
        
        # 保存线程引用，避免被垃圾回收
        winobj._test_thread = test_thread
    
    def provider_changed(index):
        """LLM提供商改变时更新模型列表和配置"""
        provider = winobj.provider_combo.currentData()
        winobj.model_combo.clear()
        
        if provider == 'openai':
            models = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
            winobj.base_url_input.setPlaceholderText("https://api.openai.com/v1")
            winobj.base_url_input.setText("")
        elif provider == 'anthropic':
            models = ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
            winobj.base_url_input.setPlaceholderText("留空使用默认地址" if config.defaulelang == 'zh' else "Leave blank for default")
            winobj.base_url_input.setText("")
        elif provider == 'gemini':
            models = ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash']
            winobj.base_url_input.setPlaceholderText("留空使用默认地址" if config.defaulelang == 'zh' else "Leave blank for default")
            winobj.base_url_input.setText("")
        elif provider == 'deepseek':
            models = ['deepseek-chat', 'deepseek-coder']
            winobj.base_url_input.setPlaceholderText("https://api.deepseek.com/v1")
            winobj.base_url_input.setText("")
        elif provider == 'siliconflow':
            models = ['deepseek-ai/DeepSeek-V3.1-Terminus', 'Qwen/Qwen2.5-72B-Instruct', 'Qwen/Qwen2.5-7B-Instruct']
            winobj.base_url_input.setPlaceholderText("https://api.siliconflow.cn/v1")
            winobj.base_url_input.setText("https://api.siliconflow.cn/v1/chat/completions")
        else:
            models = []
        
        winobj.model_combo.addItems(models)
        if models:
            winobj.model_combo.setCurrentIndex(0)
        
        # 加载对应提供商的 API Key
        load_api_key_from_env()
        
        # 保存配置
        save_llm_config()

    from videotrans.component import LLMTranslateForm
    try:
        winobj = config.child_forms.get('llmtransform')

        if winobj is not None:
            winobj.show()
            winobj.raise_()
            winobj.activateWindow()
            return

        winobj = LLMTranslateForm()
        config.child_forms['llmtransform'] = winobj
        
        # 初始化 LLM 提供商
        providers = [
            ('OpenAI', 'openai'),
            ('Claude/Anthropic', 'anthropic'),
            ('Gemini', 'gemini'),
            ('DeepSeek', 'deepseek'),
            ('SiliconFlow', 'siliconflow'),
        ]
        
        for name, value in providers:
            winobj.provider_combo.addItem(name, value)
        
        # 从 config.params 加载保存的配置
        saved_provider = config.params.get('llm_provider', 'openai')
        for i in range(winobj.provider_combo.count()):
            if winobj.provider_combo.itemData(i) == saved_provider:
                winobj.provider_combo.setCurrentIndex(i)
                break
        
        # 初始化语言列表
        languages = [
            ('自动检测' if config.defaulelang == 'zh' else 'Auto', 'auto'),
            ('中文', 'zh'),
            ('英语', 'en'),
            ('日语', 'ja'),
            ('韩语', 'ko'),
            ('法语', 'fr'),
            ('德语', 'de'),
            ('西班牙语', 'es'),
            ('意大利语', 'it'),
            ('葡萄牙语', 'pt'),
            ('俄语', 'ru'),
            ('阿拉伯语', 'ar'),
            ('泰语', 'th'),
            ('越南语', 'vi'),
        ]
        
        for name, value in languages:
            winobj.source_lang_combo.addItem(name, value)
            if value != 'auto':  # 目标语言不能是自动检测
                winobj.target_lang_combo.addItem(name, value)
        
        # 设置默认值
        winobj.source_lang_combo.setCurrentIndex(0)  # 自动检测
        winobj.target_lang_combo.setCurrentIndex(0)  # 默认中文
        
        # 加载双语字幕选项
        bilingual_enabled = config.params.get('llm_translate_bilingual', False)
        winobj.bilingual_checkbox.setChecked(bilingual_enabled)
        
        # 设置代理
        if config.proxy:
            winobj.proxy_input.setText(config.proxy)
        
        # 连接信号
        winobj.select_file_btn.clicked.connect(select_file_fun)
        winobj.start_btn.clicked.connect(start_translate_fun)
        winobj.stop_btn.clicked.connect(stop_translate_fun)
        winobj.open_result_btn.clicked.connect(open_result_fun)
        winobj.provider_combo.currentIndexChanged.connect(provider_changed)
        winobj.test_btn.clicked.connect(test_llm_connection)
        
        # 监听 API Key 输入变化，自动保存到 .env 文件
        winobj.api_key_input.textChanged.connect(save_api_key_to_env)
        
        # 监听模型和 Base URL 变化，保存配置
        winobj.model_combo.currentTextChanged.connect(save_llm_config)
        winobj.base_url_input.textChanged.connect(save_llm_config)
        
        # 监听双语字幕选项变化，保存配置
        winobj.bilingual_checkbox.stateChanged.connect(save_bilingual_config)
        
        # 触发一次以初始化模型列表和加载保存的配置
        provider_changed(winobj.provider_combo.currentIndex())
        
        # 加载保存的模型和 Base URL
        saved_model = config.params.get('llm_model', '')
        if saved_model:
            # 如果模型不在列表中，添加进去
            if winobj.model_combo.findText(saved_model) == -1:
                winobj.model_combo.addItem(saved_model)
            winobj.model_combo.setCurrentText(saved_model)
        
        saved_base_url = config.params.get('llm_base_url', '')
        if saved_base_url:
            winobj.base_url_input.setText(saved_base_url)
        
        winobj.selected_file = None
        winobj.show()
        
    except Exception as e:
        print(f"Error opening LLM translate window: {e}")
        import traceback
        traceback.print_exc()

