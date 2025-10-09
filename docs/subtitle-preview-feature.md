# 字幕预览功能说明 / Subtitle Preview Feature

## 功能介绍 / Feature Description

在"视频、音频、字幕三者合并"界面中，新增了实时字幕预览功能。该功能可以在调整字幕参数时，实时在视频帧上预览字幕效果，帮助用户更直观地调整字幕样式。

A real-time subtitle preview feature has been added to the "Video, Audio, and Subtitle Merge" interface. This feature allows you to preview subtitle effects on video frames in real-time while adjusting subtitle parameters, helping users adjust subtitle styles more intuitively.

## 使用方法 / How to Use

### 1. 选择视频文件 / Select Video File

点击"选择视频文件"按钮，选择需要处理的视频文件。选择后，系统会自动：
- 从视频中间位置截取一帧作为预览背景
- 在预览区域显示这一帧

Click the "Select Video File" button to choose the video file to process. After selection, the system will automatically:
- Extract a frame from the middle of the video as the preview background
- Display this frame in the preview area

### 2. 调整字幕参数 / Adjust Subtitle Parameters

调整以下任意字幕参数时，预览会自动更新：

When adjusting any of the following subtitle parameters, the preview will automatically update:

- **位置** / Position: 字幕在视频中的位置（left-top, center, bottom等）
- **边距** / Margins: 左边距、垂直边距、右边距
- **字体大小** / Font Size: 字幕文字大小
- **字体** / Font: 点击"选择字体"按钮选择字体
- **字体颜色** / Text Color: 点击"字体颜色"按钮选择颜色
- **背景阴影色** / Background Color: 点击"背景阴影色"按钮选择背景色
- **轮廓色** / Border Color: 点击"轮廓色"按钮选择轮廓颜色
- **轮廓大小** / Outline: 字幕轮廓的大小
- **阴影大小** / Shadow: 字幕阴影的大小
- **背景色块风格** / Background Style: 勾选后使用背景色块风格

### 3. 手动刷新预览 / Manual Refresh

如果需要手动刷新预览，可以点击预览区域下方的"刷新预览"按钮。

If you need to manually refresh the preview, click the "Refresh Preview" button below the preview area.

### 4. 软字幕模式 / Soft Subtitle Mode

当勾选"嵌入软字幕"选项时，预览区域将只显示原始视频帧，不会绘制硬字幕效果。这是因为软字幕是嵌入到视频容器中的，而不是直接绘制在视频画面上。

When the "Embedded Soft Subtitles" option is checked, the preview area will only display the original video frame without rendering hard subtitle effects. This is because soft subtitles are embedded in the video container rather than drawn directly on the video frames.

## 技术细节 / Technical Details

### 实现原理 / Implementation Principle

1. **视频帧提取** / Frame Extraction: 使用FFmpeg从视频中间位置提取一帧图片
2. **ASS字幕生成** / ASS Subtitle Generation: 根据用户设置的参数动态生成ASS格式字幕文件
3. **字幕绘制** / Subtitle Rendering: 使用FFmpeg的subtitles滤镜将字幕绘制到视频帧上
4. **实时预览** / Real-time Preview: 通过Qt信号槽机制，当参数改变时自动触发预览更新

### 临时文件 / Temporary Files

预览功能会在临时目录中生成以下文件，这些文件会在使用后自动清理：
- 视频帧截图 (video_frame_*.jpg)
- 预览字幕文件 (preview_*.srt, preview_*.ass)
- 预览结果图片 (preview_*.jpg)

The preview feature generates the following files in the temporary directory, which are automatically cleaned up after use:
- Video frame screenshots (video_frame_*.jpg)
- Preview subtitle files (preview_*.srt, preview_*.ass)
- Preview result images (preview_*.jpg)

## 注意事项 / Notes

1. 预览功能需要FFmpeg支持，请确保已正确安装FFmpeg
2. 预览使用的是示例字幕文本"这是字幕预览效果 / Subtitle Preview Effect"
3. 实际处理时会使用您选择的真实字幕文件
4. 预览区域固定为640x360像素，但不影响最终输出视频的分辨率

1. The preview feature requires FFmpeg support, please ensure FFmpeg is properly installed
2. The preview uses sample subtitle text "这是字幕预览效果 / Subtitle Preview Effect"
3. The actual processing will use your selected real subtitle file
4. The preview area is fixed at 640x360 pixels, but this does not affect the final output video resolution

## 修改文件列表 / Modified Files

- `videotrans/ui/vasrt.py`: UI界面定义，添加了预览控件和预览更新方法
- `videotrans/winform/fn_vas.py`: 功能实现，添加了视频帧提取功能

## 版本信息 / Version Information

- 功能添加日期 / Feature Added: 2025-10-09
- 开发者 / Developer: AI Assistant

