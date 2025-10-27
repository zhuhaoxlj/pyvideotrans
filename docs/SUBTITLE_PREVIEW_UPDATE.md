# 字幕预览功能更新说明

## 功能概述

为"视频、音频、字幕三者合并"页面添加了实时字幕预览功能，用户可以在调整字幕参数时，直观地看到字幕在视频上的显示效果。

## 主要功能

### 1. 自动视频帧提取
- 当用户选择视频文件时，系统会自动从视频中间位置截取一帧
- 这一帧将作为字幕预览的背景图像

### 2. 实时预览更新
当用户修改以下任意参数时，预览会自动更新：
- 字幕位置（left-top, center, bottom等）
- 左边距、垂直边距、右边距
- 字体大小
- 字体样式（通过字体选择器）
- 字体颜色
- 背景阴影色
- 轮廓色
- 轮廓大小
- 阴影大小
- 背景色块风格

### 3. 性能优化
- 使用防抖机制（500ms延迟），避免频繁更新导致的性能问题
- 用户快速调整参数时，只会在最后一次修改后500ms执行预览更新

### 4. 手动刷新
- 提供"刷新预览"按钮，用户可以随时手动刷新预览
- 手动刷新会立即执行，不使用防抖延迟

### 5. 软字幕兼容
- 当选择"嵌入软字幕"选项时，预览区域只显示原始视频帧
- 这是因为软字幕不会直接绘制在视频画面上

## 代码修改详情

### 文件1: `videotrans/ui/vasrt.py`

**新增组件：**
1. `preview_label` - QLabel：640x360的预览区域
2. `refresh_preview_btn` - QPushButton：刷新预览按钮
3. `preview_update_timer` - QTimer：防抖定时器
4. `video_frame_path` - str：存储视频帧路径

**新增方法：**
1. `update_subtitle_preview()` - 触发预览更新（使用防抖）
2. `_do_update_preview()` - 实际执行预览更新
3. `_create_preview_ass(srt_file, ass_file)` - 创建预览用的ASS字幕文件
4. `_format_milliseconds(milliseconds)` - 时间格式转换辅助方法

**信号连接：**
- `position.currentTextChanged` → 更新预览
- `marginL.textChanged` → 更新预览
- `marginV.textChanged` → 更新预览
- `marginR.textChanged` → 更新预览
- `outline.textChanged` → 更新预览
- `shadow.textChanged` → 更新预览
- `font_size_edit.textChanged` → 更新预览
- `ysphb_borderstyle.toggled` → 更新预览
- `choose_font()` → 更新预览
- `choose_color()` → 更新预览
- `choose_backgroundcolor()` → 更新预览
- `choose_bordercolor()` → 更新预览

### 文件2: `videotrans/winform/fn_vas.py`

**新增函数：**
1. `extract_video_frame(video_path)` - 从视频中截取帧并更新预览

**修改函数：**
1. `get_file(type='video')` - 在选择视频后调用 `extract_video_frame()`

## 技术实现

### 视频帧提取
```python
# 使用FFmpeg从视频中间位置截取一帧
cmd = [
    '-y',
    '-ss', str(seek_time),  # 定位到视频中间
    '-i', video_path,
    '-vframes', '1',        # 只提取一帧
    '-q:v', '2',           # 高质量
    frame_path
]
tools.runffmpeg(cmd)
```

### 字幕渲染
```python
# 使用FFmpeg的subtitles滤镜将字幕绘制到视频帧上
cmd = [
    '-y',
    '-i', self.video_frame_path,
    '-vf', f"subtitles={os.path.basename(preview_ass)}:charenc=utf-8",
    '-frames:v', '1',
    preview_output
]
tools.runffmpeg(cmd)
```

### 防抖机制
```python
# 使用QTimer实现防抖
self.preview_update_timer = QTimer()
self.preview_update_timer.setSingleShot(True)
self.preview_update_timer.timeout.connect(self._do_update_preview)

def update_subtitle_preview(self):
    self.preview_update_timer.stop()    # 停止之前的定时器
    self.preview_update_timer.start(500) # 500ms后执行
```

## 临时文件管理

预览功能会创建以下临时文件（自动清理）：
- `video_frame_{timestamp}.jpg` - 提取的视频帧
- `preview_{timestamp}.srt` - 临时字幕文件
- `preview_{timestamp}.ass` - 临时ASS字幕文件
- `preview_{timestamp}.jpg` - 渲染后的预览图片

## 使用示例

1. 打开"视频、音频、字幕三者合并"窗口
2. 点击"选择视频文件"，选择一个视频
3. 预览区域会自动显示视频的一帧，并绘制示例字幕
4. 调整字幕参数（位置、大小、颜色等）
5. 预览会在500ms后自动更新
6. 如需立即查看效果，点击"刷新预览"按钮

## 预览文本

预览使用的示例字幕文本为：
```
这是字幕预览效果
Subtitle Preview Effect
```

实际处理时会使用用户选择的真实字幕文件。

## 注意事项

1. 预览功能需要FFmpeg支持
2. 预览区域固定为640x360像素
3. 预览不影响最终输出视频的分辨率
4. 软字幕模式下不会显示字幕效果

## 测试建议

1. 测试不同格式的视频文件（mp4, avi, mkv等）
2. 测试各种字幕参数组合
3. 测试快速连续调整参数时的防抖效果
4. 测试软字幕/硬字幕切换
5. 测试刷新预览按钮

## 已知限制

1. 预览只截取视频的一帧，无法预览动态字幕效果
2. 某些特殊字体在预览中可能显示效果与最终结果略有差异
3. 预览需要调用FFmpeg，对于大视频文件可能需要几秒时间

## 未来改进方向

1. 支持选择预览帧的时间位置
2. 支持预览实际字幕文件的内容
3. 支持多行字幕预览
4. 优化预览生成速度

---

更新日期: 2025-10-09

