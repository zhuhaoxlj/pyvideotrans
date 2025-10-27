# 代码修改总结 / Code Changes Summary

## 📋 修改概述 / Overview

为"视频、音频、字幕三者合并"功能添加了实时字幕预览功能，用户可以在调整字幕参数时直观地看到字幕效果。

Added real-time subtitle preview feature to the "Video, Audio, and Subtitle Merge" function, allowing users to visually see subtitle effects while adjusting parameters.

## 📁 修改的文件 / Modified Files

### 1. `videotrans/ui/vasrt.py` (+187 行)

**主要修改：**

#### 新增导入
```python
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel
```

#### 新增UI组件
- `preview_label` (QLabel) - 640×360 预览区域
- `refresh_preview_btn` (QPushButton) - 刷新预览按钮
- `preview_update_timer` (QTimer) - 防抖定时器
- `video_frame_path` (str) - 视频帧路径存储

#### 新增方法
1. **`update_subtitle_preview()`**
   - 功能：触发预览更新（使用防抖机制）
   - 延迟：500毫秒
   
2. **`_do_update_preview()`**
   - 功能：实际执行预览更新
   - 处理：创建临时字幕文件，使用FFmpeg渲染，显示结果
   
3. **`_create_preview_ass(srt_file, ass_file)`**
   - 功能：创建预览用的ASS格式字幕文件
   - 参数：根据UI设置生成完整的ASS样式
   
4. **`_format_milliseconds(milliseconds)`**
   - 功能：将毫秒转换为ASS时间格式 (HH:mm:ss.zz)
   - 返回：格式化的时间字符串

#### 信号连接（Signal Connections）
```python
# 参数改变时自动更新预览
self.position.currentTextChanged.connect(lambda: self.update_subtitle_preview())
self.marginL.textChanged.connect(lambda: self.update_subtitle_preview())
self.marginV.textChanged.connect(lambda: self.update_subtitle_preview())
self.marginR.textChanged.connect(lambda: self.update_subtitle_preview())
self.outline.textChanged.connect(lambda: self.update_subtitle_preview())
self.shadow.textChanged.connect(lambda: self.update_subtitle_preview())
self.font_size_edit.textChanged.connect(lambda: self.update_subtitle_preview())
self.ysphb_borderstyle.toggled.connect(lambda: self.update_subtitle_preview())
```

#### 修改的现有方法
- `choose_font()` - 添加预览更新
- `choose_color()` - 添加预览更新
- `choose_backgroundcolor()` - 添加预览更新
- `choose_bordercolor()` - 添加预览更新
- `update_language()` - 添加预览更新

### 2. `videotrans/winform/fn_vas.py` (+42 行)

**主要修改：**

#### 新增函数
```python
def extract_video_frame(video_path):
    """从视频中截取一帧用于预览"""
    # 1. 获取视频时长
    # 2. 计算中间位置
    # 3. 使用FFmpeg截取帧
    # 4. 更新预览显示
```

#### 修改的现有函数
```python
def get_file(type='video'):
    # ... 原有代码 ...
    if type == 'video':
        winobj.ysphb_videoinput.setText(fname.replace('\\', '/'))
        # 新增：从视频中截取一帧用于预览
        extract_video_frame(fname)
```

## 🎯 功能特性 / Features

### ✅ 自动视频帧提取
- 选择视频后自动截取中间帧
- 使用FFmpeg高质量提取
- 自动缩放以适应预览区域

### ✅ 实时预览更新
- 支持所有字幕参数的实时预览
- 防抖机制避免频繁渲染（500ms延迟）
- 手动刷新按钮提供即时更新

### ✅ 完整的样式支持
- ✓ 9种位置选项
- ✓ 边距调整（左、右、垂直）
- ✓ 字体选择和大小
- ✓ 字体颜色（含透明度）
- ✓ 背景颜色（含透明度）
- ✓ 轮廓颜色和大小
- ✓ 阴影大小
- ✓ 背景色块风格

### ✅ 性能优化
- 防抖机制减少不必要的渲染
- 临时文件自动清理
- 异步更新不阻塞UI

### ✅ 软字幕兼容
- 软字幕模式下显示原始视频帧
- 硬字幕模式下显示完整效果

## 🔧 技术实现 / Technical Implementation

### 视频帧提取 / Frame Extraction
```python
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

### 字幕渲染 / Subtitle Rendering
```python
cmd = [
    '-y',
    '-i', self.video_frame_path,
    '-vf', f"subtitles={os.path.basename(preview_ass)}:charenc=utf-8",
    '-frames:v', '1',
    preview_output
]
tools.runffmpeg(cmd)
```

### 防抖实现 / Debounce Implementation
```python
self.preview_update_timer = QTimer()
self.preview_update_timer.setSingleShot(True)
self.preview_update_timer.timeout.connect(self._do_update_preview)

def update_subtitle_preview(self):
    self.preview_update_timer.stop()
    self.preview_update_timer.start(500)  # 500ms延迟
```

## 📦 临时文件 / Temporary Files

预览功能会创建以下临时文件（自动清理）：

1. `video_frame_{timestamp}.jpg` - 提取的视频帧
2. `preview_{timestamp}.srt` - 临时字幕文件
3. `preview_{timestamp}.ass` - 临时ASS字幕文件
4. `preview_{timestamp}.jpg` - 渲染后的预览图片

## 📚 文档文件 / Documentation Files

### 新增文档：
1. `docs/subtitle-preview-feature.md` - 功能技术文档
2. `docs/字幕预览功能使用指南.md` - 中文用户指南
3. `docs/Subtitle-Preview-User-Guide.md` - 英文用户指南
4. `SUBTITLE_PREVIEW_UPDATE.md` - 更新说明
5. `CHANGES_SUMMARY.md` - 本文件

## 🧪 测试建议 / Testing Recommendations

### 基础功能测试
- [ ] 选择不同格式的视频文件（mp4, avi, mkv等）
- [ ] 验证视频帧正确提取
- [ ] 验证预览区域正确显示

### 参数调整测试
- [ ] 测试所有9个位置选项
- [ ] 调整边距值，验证预览更新
- [ ] 修改字体大小，验证效果
- [ ] 选择不同字体，验证显示
- [ ] 调整各种颜色（字体、背景、轮廓）
- [ ] 修改轮廓和阴影大小

### 性能测试
- [ ] 快速连续调整参数，验证防抖效果
- [ ] 测试大视频文件的帧提取速度
- [ ] 验证临时文件正确清理

### 兼容性测试
- [ ] 软字幕模式切换
- [ ] 硬字幕模式切换
- [ ] 特殊字符和中文显示
- [ ] 不同操作系统（Windows, macOS, Linux）

## ⚠️ 注意事项 / Important Notes

1. **依赖要求**：需要FFmpeg支持
2. **预览文本**：使用固定示例文本，非实际字幕内容
3. **预览分辨率**：固定640×360，不影响最终输出
4. **更新延迟**：自动更新有500ms延迟（防抖）
5. **临时文件**：会在临时目录创建文件，自动清理

## 🔄 版本兼容性 / Version Compatibility

- **Python**: 3.x
- **PySide6**: 6.x
- **FFmpeg**: 任何版本 (Any version)
- **操作系统**: Windows, macOS, Linux

## 📊 代码统计 / Code Statistics

```
Modified files: 2
Total lines added: +229
- videotrans/ui/vasrt.py: +187 lines
- videotrans/winform/fn_vas.py: +42 lines

Documentation files: 5
- Technical docs: 2
- User guides: 2
- Summary: 1
```

## 🎉 功能亮点 / Highlights

1. **直观可视化** - 实时预览字幕效果
2. **性能优化** - 防抖机制提高响应速度
3. **完整支持** - 所有字幕参数都可预览
4. **自动化** - 自动提取视频帧和更新预览
5. **用户友好** - 简单易用，无需额外配置

## 🚀 未来改进 / Future Improvements

1. 支持选择预览帧的时间位置
2. 支持预览实际字幕文件内容
3. 支持多行字幕的完整预览
4. 优化预览生成速度
5. 添加预览历史记录功能

---

**修改日期 / Modified Date**: 2025-10-09  
**开发者 / Developer**: AI Assistant  
**状态 / Status**: ✅ 完成 / Completed

