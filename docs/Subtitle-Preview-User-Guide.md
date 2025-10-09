# Subtitle Preview Feature User Guide

## 🎬 Feature Introduction

In the "Video, Audio, and Subtitle Merge" page, we've added a **real-time subtitle preview** feature! Now you can visually see how subtitles will appear on your actual video while adjusting subtitle styles.

## 📋 How to Use

### Step 1: Open the Feature
1. Launch the application
2. Navigate to and open "Video, Audio, and Subtitle Merge" feature

### Step 2: Select Video File
1. Click the "Select Video File" button
2. Choose the video file you want to process
3. **Auto Preview**: The system will automatically extract a frame from the video and display it in the preview area

### Step 3: Adjust Subtitle Parameters
Now you can adjust various subtitle parameters, and the preview will automatically update after each change (with a 0.5-second delay):

#### Position and Margins
- **Position**: Choose where subtitles appear in the video (top-left, center, bottom, etc.)
- **Left Margin**: Adjust distance from the left edge
- **Vertical Margin**: Adjust distance from top/bottom
- **Right Margin**: Adjust distance from the right edge

#### Font Style
- **Font Size**: Enter a number to set font size (e.g., 16, 20, 24)
- **Select Font**: Click button to choose your preferred font
- **Font Color**: Click button to select text color (supports transparency)

#### Effect Settings
- **Outline**: Set the thickness of font outline
- **Shadow**: Set the size of font shadow
- **Background Color**: Set background or shadow color
- **Border Color**: Set outline color
- **Background Style**: Check to use background blocks instead of outline strokes

### Step 4: View Preview
- The preview area will display your subtitle settings in real-time
- For immediate preview, click the "Refresh Preview" button

## 💡 Usage Tips

### 1. Quick Adjustments
- When rapidly adjusting multiple parameters, the preview waits 0.5 seconds after you stop
- This prevents frequent rendering and improves responsiveness

### 2. Manual Refresh
- If automatic updates feel slow, click "Refresh Preview" for immediate update
- Manual refresh skips the delay and shows the latest effect instantly

### 3. Soft Subtitle Mode
- When "Embedded Soft Subtitles" is checked, only the original video frame is shown
- This is because soft subtitles are stored in the video container, not drawn on frames

### 4. Preview Text
- Preview uses sample text: "这是字幕预览效果 / Subtitle Preview Effect"
- Actual processing will use your selected subtitle file

## 📐 Preview Area Details

- **Size**: Preview area is fixed at 640×360 pixels
- **Location**: Displayed at the top of the interface
- **Background**: Dark gray background for better subtitle visibility
- **Scaling**: Video frames automatically scale to fit while maintaining aspect ratio

## ⚙️ Supported Subtitle Parameters

✅ Subtitle position (9 position options)  
✅ Left, vertical, and right margins  
✅ Font type and size  
✅ Font color (with transparency)  
✅ Background color (with transparency)  
✅ Outline color (with transparency)  
✅ Outline size  
✅ Shadow size  
✅ Background block style  

## ❓ FAQ

### Q1: Why does it take a few seconds after selecting a video?
A: The system needs to use FFmpeg to extract a frame from the video. This may take several seconds for large video files.

### Q2: Are preview subtitles the same as actual processed subtitles?
A: The preview uses sample text, but the style settings are identical. Actual processing will use your selected subtitle file content.

### Q3: Why can't I see subtitles in soft subtitle mode?
A: Soft subtitles are embedded as separate tracks in the video file, not drawn directly on frames. Players can choose whether to display soft subtitles.

### Q4: Can I preview frames from different time points?
A: Currently, the preview uses a frame from the middle of the video. To check other time points, review the output video after actual processing.

### Q5: What if the preview is laggy?
A: Preview uses a debounce mechanism with a 0.5-second wait. If it feels slow, adjust all parameters first, then click the "Refresh Preview" button.

## 🔧 Technical Requirements

- ✅ FFmpeg must be installed
- ✅ Python environment with PySide6 required
- ✅ Sufficient temporary storage space needed

## 📝 Important Notes

1. **Temporary Files**: Preview creates temporary files that are automatically cleaned up
2. **Performance**: Preview calls FFmpeg; first preview may take several seconds
3. **Resolution**: Preview area resolution is fixed; doesn't affect final output resolution
4. **Update Frequency**: Auto-update has 0.5-second delay to avoid frequent rendering

## 🎉 Usage Examples

### Scenario 1: Bottom Subtitle Adjustment
1. Select video file
2. Position: bottom-center
3. Vertical margin: 20
4. Font size: 24
5. Font color: White
6. Outline: Black, size 2
7. Review preview and confirm

### Scenario 2: Top Title Creation
1. Select video file
2. Position: top-center
3. Vertical margin: 30
4. Font size: 32
5. Choose bold font
6. Background style: Checked
7. Background shadow: Semi-transparent black
8. Review preview

## 📞 Feedback & Support

If you encounter issues or have suggestions for improvement, please provide feedback!

---

**Last Updated**: October 9, 2025  
**Version**: 1.0

