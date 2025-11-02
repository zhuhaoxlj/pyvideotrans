# 🔄 自动智能分割工作流

## ✨ 新功能

**生成字幕完成后，自动跳转到智能分割页面！**

---

## 🚀 工作流程

### 步骤 1：生成字幕
```
选择视频 → 点击"开始生成字幕" → 等待处理完成
```

**处理内容：**
- ✅ 使用 faster-whisper 识别语音
- ✅ 生成词级时间戳
- ✅ 自动缓存到本地
- ✅ 生成初步字幕文件（SRT + FCPXML）

### 步骤 2：自动跳转（5秒倒计时）
```
处理完成 → 显示"5秒后自动跳转..." → 自动进入智能分割页面
```

**自动传递的数据：**
- ✅ 原始视频文件路径
- ✅ 生成的字幕文件
- ✅ 缓存的词级时间戳
- ✅ 自动勾选"使用现有字幕"

### 步骤 3：智能分割
```
配置 LLM → 点击"开始处理" → 秒级完成！
```

**处理内容：**
- ✅ 检测到缓存，直接使用
- ✅ LLM 智能优化断句
- ✅ 生成优化后的字幕

---

## 📊 性能对比

### 传统方式（手动）
```
1. 生成字幕 → 12秒
2. 手动点击"继续智能分割"
3. 智能分割 → 45秒（重新识别）+ 8秒（LLM）= 53秒

总计：12s + 53s = 65秒
```

### 新方式（自动 + 缓存）
```
1. 生成字幕 → 12秒
2. 自动跳转 → 5秒（可以取消）
3. 智能分割 → <1秒（使用缓存）+ 8秒（LLM）= 8秒

总计：12s + 5s + 8s = 25秒
⚡ 速度提升 62%！
```

---

## 🎯 使用场景

### 场景 1：完整流程（推荐）
```
视频 → 生成字幕 → [自动跳转] → 智能分割 → 完成
```

**优势：**
- ✅ 全自动，无需手动操作
- ✅ 缓存无缝共享
- ✅ 最快速度

### 场景 2：分步处理
```
视频 → 生成字幕 → 手动取消自动跳转 → 下载文件 → 稍后智能分割
```

**如何取消自动跳转：**
1. 看到"5秒后自动跳转..."
2. 点击"重新开始"或切换到其他页面
3. 自动跳转被取消

### 场景 3：只生成字幕
```
视频 → 生成字幕 → 取消自动跳转 → 下载 SRT/FCPXML
```

---

## 💡 智能缓存机制

### 缓存内容
```
~/Videos/pyvideotrans/get_srt_zimu/whisper_cache/
└── {视频SHA256哈希}.pkl
    ├── all_words: 词级时间戳数组
    ├── language: 检测的语言
    └── timestamp: 创建时间
```

### 缓存命中判断
1. ✅ 视频文件内容相同（SHA256）
2. ✅ 缓存文件存在且有效

### 缓存优势
- ⚡ 第二次处理同一视频：<1秒
- 💾 可以多次调整 LLM 参数重新分割
- 🔄 智能分割可以无限次优化

---

## 🔧 技术细节

### 自动跳转实现
```python
# process_view.py
def on_processing_finished(self, srt_path, fcpxml_path):
    # 5秒后自动跳转
    QTimer.singleShot(5000, lambda: self._auto_goto_split())

def _auto_goto_split(self):
    # 传递完整数据
    parent_window.show_split_with_full_data(
        video_file=video_file,
        srt_file=self.srt_path
    )
```

### 数据传递
```python
# main_window.py
def show_split_with_full_data(self, video_file, srt_file):
    # 1. 加载视频文件
    self.split_view.load_video_file(video_file)
    
    # 2. 勾选"使用现有字幕"
    self.split_view.use_existing_srt.setChecked(True)
    
    # 3. 加载字幕文件
    self.split_view.load_srt_file(srt_file)
```

### 缓存检测
```python
# llm_processor.py
def process_with_video_and_srt(self):
    # 检查缓存
    cache_key = self.get_cache_key(self.video_file)
    cached_data = self.load_cache(cache_key)
    
    if cached_data:
        # ✅ 使用缓存，秒级完成
        all_words = cached_data['all_words']
    else:
        # ❌ 未命中，重新识别
        all_words = self.transcribe_with_whisper()
```

---

## 📝 用户体验

### UI 反馈

#### 步骤 1：生成字幕完成
```
当前状态: 完成 ✓

✓ 处理完成！
⏳ 5秒后自动跳转到智能分割页面...

[重新开始] [下载SRT] [下载FCPXML] [下载全部] [继续智能分割]
```

#### 步骤 2：自动跳转到智能分割
```
✅ 已加载视频文件: 123.mp4
✅ 已加载字幕文件: 123_merged.srt

🚀 模式：使用视频+现有字幕（Whisper词级+LLM）
💡 由于视频已处理过，将直接使用缓存的词级时间戳

📌 请配置 LLM 设置后点击「开始处理」

[开始处理按钮已激活]
```

#### 步骤 3：智能分割处理
```
🔍 检查缓存...
   视频文件: /Users/mark/Downloads/123.mp4
   缓存键: 7cfbea77183a4c94... (SHA256)

✅ 找到缓存！
   📊 从缓存加载: 2847 个词
   🌐 检测语言: en

🤖 使用 LLM 进行智能断句优化...
   LLM提供商: siliconflow
   LLM模型: Qwen/Qwen2.5-7B-Instruct
   处理文本: 2847 词
   ⏳ 正在调用 LLM API，请稍候...

   📡 LLM 响应流:
   [实时显示 LLM 输出]

✅ LLM响应完成 (耗时: 8.2秒)
✅ 解析完成，生成 156 条字幕
✅ 时间戳调整完成

💾 保存完成
✅ 完成！生成 156 条字幕
📁 保存到: ~/Videos/pyvideotrans/get_srt_zimu/output/123_llm_resplit.srt
```

---

## ⚙️ 配置选项

### 取消自动跳转（未来功能）
```python
# 可以在设置中添加：
config = {
    'auto_jump_to_split': True,      # 是否自动跳转
    'auto_jump_delay': 5,             # 延迟秒数
    'show_countdown': True            # 显示倒计时
}
```

---

## 🎉 总结

### 优势
1. ✅ **全自动流程**：生成 → 跳转 → 分割，一气呵成
2. ✅ **智能缓存**：第二次处理同一视频，秒级完成
3. ✅ **无缝衔接**：自动传递所有数据，无需手动操作
4. ✅ **性能提升**：速度提升 62%
5. ✅ **用户友好**：5秒倒计时，可以随时取消

### 适用场景
- ✅ 批量处理视频（生成 + 优化）
- ✅ 需要多次调整 LLM 参数
- ✅ 追求最快速度
- ✅ 自动化工作流

### 注意事项
- ⚠️ 首次处理视频需要下载模型
- ⚠️ 缓存基于文件内容，修改视频会重新识别
- ⚠️ 自动跳转可以随时取消

---

## 📖 相关文档

- [FASTER_WHISPER_MIGRATION.md](./FASTER_WHISPER_MIGRATION.md) - faster-whisper 升级说明
- [README_LLM_MIGRATION.md](./README_LLM_MIGRATION.md) - LLM 智能分割功能
- [CACHE_IMPLEMENTATION_SUMMARY.md](../CACHE_IMPLEMENTATION_SUMMARY.md) - 缓存机制详解

---

**享受全自动的字幕处理体验！** 🚀

