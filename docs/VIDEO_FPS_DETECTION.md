# 视频帧率检测功能 / Video FPS Detection Feature

## 功能简介 / Overview

在 PyVideoTrans 工具集的主界面中，现在新增了一个视频帧率检测区域。您可以通过拖拽视频文件到该区域，快速查看视频的详细信息，包括帧率、分辨率、编码格式等。

The main menu of PyVideoTrans Tools now includes a video FPS detection area. You can drag and drop video files to quickly view detailed information including FPS, resolution, codec, and more.

## 功能特点 / Features

### 中文版

- **双重交互方式**：
  - 🖱️ 点击区域打开文件选择对话框
  - 📂 拖拽视频文件直接到检测区域
- **多格式支持**：支持常见的视频格式（MP4、MOV、AVI、MKV、FLV、WMV、WEBM、M4V、MPEG、MPG）
- **详细信息**：显示视频的完整信息，包括：
  - 帧率 (FPS) - 白色大字清晰显示
  - 分辨率（宽×高）
  - 视频编码格式
  - 视频时长
- **实时分析**：选择或拖入视频后立即分析并显示结果
- **友好提示**：清晰的视觉反馈和错误提示
- **简洁美观**：无背景条干扰，纯白色字体显示

### English

- **Dual Interaction Methods**:
  - 🖱️ Click area to open file selection dialog
  - 📂 Drag and drop video files directly to the detection area
- **Multi-format Support**: Supports common video formats (MP4, MOV, AVI, MKV, FLV, WMV, WEBM, M4V, MPEG, MPG)
- **Detailed Information**: Displays complete video information including:
  - Frame rate (FPS) - Clearly displayed in large white text
  - Resolution (width×height)
  - Video codec
  - Duration
- **Real-time Analysis**: Instant analysis and display of results after selecting or dropping video
- **User-friendly**: Clear visual feedback and error messages
- **Clean & Beautiful**: No background bars, pure white text display

## 使用方法 / How to Use

### 中文版

1. **启动程序**：运行 PyVideoTrans 主程序
   ```bash
   python main.py
   ```

2. **找到检测区域**：在主界面下方可以看到一个灰色的虚线边框区域，标有"📹 点击或拖入视频文件检测帧率"

3. **选择视频**：有两种方式
   - **方法一**：点击该区域，会弹出文件选择对话框，选择视频文件
   - **方法二**：将视频文件从文件管理器拖拽到该区域

4. **查看结果**：系统会自动分析视频并显示详细信息
   - 文件名、分辨率、编码、时长会显示在区域中部
   - 帧率会以大号白色字体显示在下方

### English

1. **Start Program**: Run the PyVideoTrans main program
   ```bash
   python main.py
   ```

2. **Locate Detection Area**: Find the gray dashed border area at the bottom of the main interface, marked "📹 Click or Drag Video to Detect FPS"

3. **Select Video**: Two methods available
   - **Method 1**: Click the area to open file selection dialog and choose a video file
   - **Method 2**: Drag and drop video files from file manager to the area

4. **View Results**: The system will automatically analyze the video and display detailed information
   - Filename, resolution, codec, and duration will be shown in the middle
   - FPS will be displayed in large white text at the bottom

## 界面说明 / Interface Description

### 中文版

检测区域包含三个部分：

1. **提示标签**：显示"📹 点击或拖入视频文件检测帧率"，提示用户可以点击或拖拽
2. **信息标签**：显示视频文件的详细信息（文件名、分辨率、编码、时长）
3. **帧率标签**：以大号白色字体显示视频的帧率（分析前隐藏）

**交互反馈**：
- 鼠标悬停时光标变为手型，提示可点击
- 拖入文件时边框颜色会变化
- 点击后会弹出系统文件选择对话框

### English

The detection area consists of three parts:

1. **Hint Label**: Shows "📹 Click or Drag Video to Detect FPS", indicating users can click or drag
2. **Info Label**: Displays detailed video information (filename, resolution, codec, duration)
3. **FPS Label**: Shows the video frame rate in large white text (hidden before analysis)

**Interaction Feedback**:
- Cursor changes to pointer on hover, indicating clickable
- Border color changes when dragging files
- File selection dialog appears after clicking

## 技术实现 / Technical Implementation

### 中文版

该功能基于 FFmpeg 的 ffprobe 工具实现，通过调用 `get_video_info()` 函数获取视频的完整信息。主要包括：

- **双重交互处理**：
  - 实现了 `mousePressEvent` 方法处理点击事件，打开文件选择对话框
  - 实现了 `dragEnterEvent` 和 `dropEvent` 方法处理拖放事件
- **文件格式验证**：检查文件扩展名是否为支持的视频格式
- **视频信息提取**：使用 ffprobe 分析视频文件
- **界面优化**：
  - 鼠标悬停时显示手型光标
  - 使用纯白色文字，无背景条干扰
  - 自适应布局，合理的边距和间距
- **友好的错误处理**：捕获并显示分析过程中的错误

### English

This feature is implemented using FFmpeg's ffprobe tool, calling the `get_video_info()` function to retrieve complete video information. Key components include:

- **Dual Interaction Handling**:
  - Implements `mousePressEvent` method to handle click events and open file selection dialog
  - Implements `dragEnterEvent` and `dropEvent` methods to handle drag & drop events
- **File Format Validation**: Checks if file extension matches supported video formats
- **Video Information Extraction**: Uses ffprobe to analyze video files
- **UI Optimization**:
  - Shows pointer cursor on hover
  - Uses pure white text without background bars
  - Adaptive layout with proper margins and spacing
- **User-friendly Error Handling**: Captures and displays errors during analysis

## 代码示例 / Code Example

### 测试脚本 / Test Script

项目中包含了一个测试脚本 `test_fps_detection.py`，可以用来测试视频信息获取功能：

```bash
python test_fps_detection.py
```

输出示例 / Sample Output:
```
📹 测试视频: How parades can build community _ Chantelle Rytter _ TEDxAtlanta.mp4
============================================================
✅ 视频信息获取成功！
   帧率 (FPS): 29.97
   分辨率: 1280x720
   视频编码: h264
   音频编码: aac
   时长: 511.72 秒
   视频流数量: 2
   音频流数量: 1
   像素格式: yuv420p
============================================================
✅ 测试通过！帧率检测功能正常工作。
```

## 相关文件 / Related Files

- `videotrans/ui/main_menu.py` - 主界面 UI 定义
- `videotrans/component/set_form.py` - 主菜单窗口实现（包含拖放逻辑）
- `videotrans/util/help_ffmpeg.py` - FFmpeg 工具函数（包含 `get_video_info()`）
- `test_fps_detection.py` - 测试脚本

## 注意事项 / Notes

### 中文版

1. 需要确保系统中已安装 FFmpeg 并配置了正确的路径
2. 大型视频文件可能需要稍长的分析时间
3. 如果分析失败，会显示错误消息提示

### English

1. Ensure FFmpeg is installed and properly configured in your system
2. Large video files may require more time for analysis
3. Error messages will be displayed if analysis fails

## 更新日志 / Changelog

### v1.1.0 (2025-11-01)

- ✨ 新增点击选择文件功能
- 🎨 优化界面显示，去除背景条
- 🎨 改用纯白色字体显示帧率信息
- 🎨 增大字体，提升可读性
- 🖱️ 添加鼠标悬停手型光标提示
- 📝 更新提示文字为"点击或拖入视频文件检测帧率"

### v1.0.0 (2025-11-01)

- ✨ 新增视频帧率检测区域
- ✨ 支持拖拽视频文件
- ✨ 显示完整的视频信息（帧率、分辨率、编码、时长）
- ✨ 支持中英文界面
- ✨ 添加友好的错误处理和提示

---

**Developed with ❤️ for PyVideoTrans**

