# 字幕预览功能快速参考 / Subtitle Preview Quick Reference

## 🚀 快速开始 / Quick Start

```
1. 打开"视频、音频、字幕三者合并"窗口
   Open "Video, Audio, and Subtitle Merge" window
   
2. 点击"选择视频文件"
   Click "Select Video File"
   
3. 调整字幕参数，查看实时预览
   Adjust subtitle parameters and view real-time preview
   
4. 点击"刷新预览"立即更新（可选）
   Click "Refresh Preview" for immediate update (optional)
```

## 🎨 支持的参数 / Supported Parameters

| 参数 / Parameter | 说明 / Description |
|-----------------|-------------------|
| 位置 / Position | 9种位置选项 / 9 position options |
| 左边距 / Left Margin | 数字，如10 / Number, e.g., 10 |
| 垂直边距 / Vertical Margin | 数字，如10 / Number, e.g., 10 |
| 右边距 / Right Margin | 数字，如10 / Number, e.g., 10 |
| 字体大小 / Font Size | 数字，如16、20、24 / Number, e.g., 16, 20, 24 |
| 字体 / Font | 点击按钮选择 / Click button to select |
| 字体颜色 / Text Color | 支持透明度 / Supports transparency |
| 背景色 / Background Color | 支持透明度 / Supports transparency |
| 轮廓色 / Outline Color | 支持透明度 / Supports transparency |
| 轮廓大小 / Outline Size | 数字，如1、2 / Number, e.g., 1, 2 |
| 阴影大小 / Shadow Size | 数字，如1、2 / Number, e.g., 1, 2 |

## ⚡ 快捷提示 / Quick Tips

### ✅ 自动更新
- 修改参数后等待 **0.5秒** 自动更新
- Auto-updates after **0.5 seconds** when parameters change

### ✅ 手动刷新
- 点击"刷新预览"按钮 **立即** 更新
- Click "Refresh Preview" for **immediate** update

### ✅ 软字幕
- 勾选"嵌入软字幕"时，只显示原始视频帧
- When "Embedded Soft Subtitles" is checked, shows only original frame

### ✅ 预览文本
- 预览使用示例文本，实际处理时使用您的字幕文件
- Preview uses sample text; actual processing uses your subtitle file

## 🎯 常用位置 / Common Positions

```
left-top        center-top       right-top
    ↑               ↑                ↑
left-center  ←  center  →      right-center
    ↓               ↓                ↓
left-bottom    center-bottom   right-bottom
```

## 💡 推荐设置 / Recommended Settings

### 📺 标准底部字幕 / Standard Bottom Subtitles
```
位置 / Position: bottom-center
垂直边距 / Vertical: 20
字体大小 / Size: 20-24
颜色 / Color: 白色 / White
轮廓 / Outline: 黑色，2 / Black, 2
```

### 📄 顶部标题 / Top Title
```
位置 / Position: top-center
垂直边距 / Vertical: 30
字体大小 / Size: 28-32
粗体 / Bold: 是 / Yes
背景色块 / Background: 是 / Yes
```

### 🎬 电影风格 / Movie Style
```
位置 / Position: bottom-center
垂直边距 / Vertical: 40
字体大小 / Size: 18-20
轮廓大小 / Outline: 1
阴影大小 / Shadow: 1
```

## ⌨️ 键盘快捷键建议 / Keyboard Shortcut Suggestions

```
暂无内置快捷键，建议使用 Tab 键在字段间快速切换
No built-in shortcuts; use Tab key to navigate between fields
```

## 🔍 预览说明 / Preview Details

### 预览区域 / Preview Area
- **尺寸 / Size**: 640×360 像素 / pixels
- **位置 / Location**: 窗口顶部 / Top of window
- **示例文本 / Sample Text**: "这是字幕预览效果 / Subtitle Preview Effect"

### 提取帧位置 / Frame Position
- **默认 / Default**: 视频中间 / Middle of video
- **原因 / Reason**: 通常中间帧最有代表性 / Middle frames are usually most representative

## ⚠️ 重要提示 / Important Notes

1. **首次加载** / First Load
   - 首次预览需要几秒提取视频帧
   - First preview needs seconds to extract frame
   
2. **预览 ≠ 实际** / Preview ≠ Actual
   - 预览文本是示例，实际会用您的字幕文件
   - Preview text is sample; actual uses your subtitle file
   
3. **分辨率** / Resolution
   - 预览固定640×360，不影响最终输出
   - Preview is 640×360; doesn't affect final output

## 🐛 故障排除 / Troubleshooting

### 问题 / Issue: 预览不更新
**解决 / Solution**: 点击"刷新预览"按钮

### 问题 / Issue: 看不到字幕
**解决 / Solution**: 检查是否勾选了"嵌入软字幕"

### 问题 / Issue: 预览很慢
**解决 / Solution**: 正常现象，等待FFmpeg处理完成

### 问题 / Issue: 预览区域空白
**解决 / Solution**: 确保已选择视频文件

## 📞 获取帮助 / Get Help

查看详细文档 / See detailed documentation:
- `docs/字幕预览功能使用指南.md` (中文)
- `docs/Subtitle-Preview-User-Guide.md` (English)

---

**版本 / Version**: 1.0  
**更新 / Updated**: 2025-10-09

