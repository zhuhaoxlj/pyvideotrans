# 🚀 快速开始 - 字幕渲染工具

解决字幕叠加显示问题，让每次只显示一句话！

## ⚡ 最快的方法

```bash
# 方法1：分割现有字幕（5秒完成）
python split_subtitles.py "你的字幕.srt" 3
python sp_vas.py
```

```bash
# 方法2：AI生成精确字幕（推荐，需要几分钟）
pip install openai-whisper
python regenerate_subtitles.py "你的视频.mp4" en base
python sp_vas.py
```

## 📝 你的具体例子

### 快速修复（现在就能用）

```bash
# 已经为你处理好了！
cd /Users/mark/Downloads/pyvideotrans

# 使用分割后的字幕
python sp_vas.py

# 在GUI中选择：
# - 视频：resource/How parades can build community  Chantelle Rytter  TEDxAtlanta-1760538972.mp4
# - 字幕：resource/How parades can build community  Chantelle Rytter  TEDxAtlanta_split.srt
```

### 最佳效果（使用AI）

```bash
# 使用 Whisper AI 重新生成字幕（英语视频）
python regenerate_subtitles.py \
  "resource/How parades can build community  Chantelle Rytter  TEDxAtlanta-1760538972.mp4" \
  en base

# 会生成：*_whisper.srt 文件
# 然后在 sp_vas.py 中使用这个文件
```

## 🎯 解决的问题

**之前的问题：**
```
00:00:35,566 --> 00:00:51,848 (16秒！)
every single time I look out... And I think... And I think, God... People are full...
每次看到游行... 我觉得... 我想，天哪... 人们心中充满...
```
❌ 4个句子叠加显示，看不清楚

**现在的效果：**
```
00:00:35,566 --> 00:00:39,636 (4秒)
every single time I look out at the parade lineup.
每次 看到游行队伍时，我仍然会眼眶湿润。

00:00:39,636 --> 00:00:43,707 (4秒)
And I think I just get chills, you know?
我觉得我只是感到寒冷，你知道吗？

00:00:43,707 --> 00:00:47,777 (4秒)
And I think, God, people are so wonderful.
我想，天哪，人们真是太棒了。

00:00:47,777 --> 00:00:51,848 (4秒)
People are full of the loveliest surprises.
人们心中充满了 最美好的惊喜。
```
✅ 每次只显示一句，清晰易读！

## 🛠️ 工具说明

### 1. `split_subtitles.py` - 智能分割

**作用：** 将长时间跨度的字幕按句子分割

**用法：**
```bash
python split_subtitles.py <字幕文件> [最大秒数]
```

**示例：**
```bash
# 分割字幕，每条最多3秒
python split_subtitles.py subtitle.srt 3

# 分割字幕，每条最多2秒
python split_subtitles.py subtitle.srt 2
```

**输出：** `字幕文件_split.srt`

---

### 2. `regenerate_subtitles.py` - AI生成 ⭐

**作用：** 使用 Whisper AI 重新生成精确字幕

**用法：**
```bash
python regenerate_subtitles.py <视频> [语言] [模型]
```

**示例：**
```bash
# 英语视频
python regenerate_subtitles.py video.mp4 en base

# 中文视频
python regenerate_subtitles.py video.mp4 zh small

# 日语视频
python regenerate_subtitles.py video.mp4 ja base
```

**模型选择：**
- `tiny` - 最快（几秒）
- `base` - 推荐（1-2分钟）⭐
- `small` - 更准确（3-5分钟）
- `medium` - 很准确（10-15分钟）
- `large` - 最准确（20-30分钟）

**输出：** `视频文件_whisper.srt`

---

### 3. `sp_vas.py` - 字幕渲染工具

**作用：** 将字幕渲染到视频上

**用法：**
```bash
python sp_vas.py
```

**在GUI中：**
1. 选择视频文件
2. 选择处理后的字幕（*_split.srt 或 *_whisper.srt）
3. 调整字体、颜色、位置
4. 点击"开始执行"

---

## 📊 效果对比

| 方案 | 时间 | 效果 | 推荐场景 |
|------|------|------|---------|
| 智能分割 | 5秒 | ⭐⭐⭐ | 快速修复 |
| Whisper AI | 5-10分钟 | ⭐⭐⭐⭐⭐ | 最佳效果 |

## 💡 推荐工作流程

### 场景1：快速处理
```bash
python split_subtitles.py "字幕.srt" 3
python sp_vas.py
# 选择 *_split.srt
```

### 场景2：最佳质量
```bash
pip install openai-whisper
python regenerate_subtitles.py "视频.mp4" en base
python sp_vas.py  
# 选择 *_whisper.srt
```

### 场景3：一键处理
```bash
./process_and_render.sh "视频.mp4" "字幕.srt" 3
# 或
./process_and_render.sh "视频.mp4" auto en base
```

## 🎬 现在就试试！

```bash
cd /Users/mark/Downloads/pyvideotrans

# 你的字幕已经处理好了，直接用：
python sp_vas.py

# 在GUI中选择：
# - 视频：resource/How parades can build community...mp4
# - 字幕：resource/How parades can build community..._split.srt
# - 点击"开始执行"
```

## ❓ 常见问题

**Q: 字幕还是太长？**
A: 减小最大持续时间，例如用 2 秒代替 3 秒：
```bash
python split_subtitles.py subtitle.srt 2
```

**Q: 想要更精确的时间对齐？**
A: 使用 Whisper AI：
```bash
pip install openai-whisper
python regenerate_subtitles.py video.mp4 en base
```

**Q: 双语字幕会被分开吗？**
A: 不会！工具会保持英文和中文配对，每次显示一对。

**Q: 支持其他语言吗？**
A: 是的！Whisper 支持 99+ 种语言：
- `en` 英语
- `zh` 中文
- `ja` 日语
- `es` 西班牙语
- `fr` 法语
- `de` 德语
- 等等...

---

🎉 享受清晰的字幕效果吧！

