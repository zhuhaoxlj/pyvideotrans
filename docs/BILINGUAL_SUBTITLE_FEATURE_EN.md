# Bilingual Subtitle Feature Guide

## Overview

The AI Subtitle Translation feature now supports generating bilingual subtitle files. Users can choose:
- **Monolingual Mode**: Only translated text
- **Bilingual Mode**: Both source and translated text

## How to Use

### 1. Open AI Subtitle Translation Window

Click the **"AI Subtitle Translation"** button in the main interface.

### 2. Configure Translation Options

- **LLM Provider**: Choose your LLM service provider (OpenAI, Anthropic, Gemini, DeepSeek, SiliconFlow, etc.)
- **API Key**: Enter your API key
- **Model**: Select or enter model name
- **API Base URL**: Optional, custom API endpoint
- **Source Language**: Select the source language (supports auto-detection)
- **Target Language**: Select the target language for translation
- **Batch Size**: Number of subtitles to translate per batch (1-50)
- **🌏 Bilingual Subtitles (Source + Translation)**: Check this option to generate bilingual subtitles

### 3. Select Subtitle File

Click **"📁 Select Subtitle File (.srt)"** to choose the SRT file to translate.

### 4. Start Translation

Click **"🚀 Start Translation"** to begin the translation process.

## Output Format

### Monolingual Mode (Bilingual option unchecked)

```
1
00:00:00,000 --> 00:00:05,000
This is the translated text

2
00:00:05,000 --> 00:00:10,000
Another translated text
```

### Bilingual Mode (Bilingual option checked)

```
1
00:00:00,000 --> 00:00:05,000
This is the original text
这是翻译后的文本

2
00:00:05,000 --> 00:00:10,000
Another original text
另一条翻译后的文本
```

## File Naming Convention

Translated files are saved in the `LLMTranslate` subfolder of the source file directory:

- **Monolingual Mode**: `original_filename_translated_targetlang.srt`
  - Example: `video_translated_zh.srt`

- **Bilingual Mode**: `original_filename_translated_targetlang_bilingual.srt`
  - Example: `video_translated_zh_bilingual.srt`

## Configuration Persistence

Your settings are automatically saved, including:
- LLM provider, model, and API URL
- Bilingual subtitle option
- Batch size

These configurations will be automatically loaded the next time you open the window.

## Notes

1. **Bilingual Format**: In bilingual mode, source and translated text are separated by a newline, which is supported by most players
2. **File Size**: Bilingual subtitle files will be slightly larger than monolingual files
3. **Compatibility**: The bilingual format follows SRT standards and is compatible with most video players
4. **Translation Quality**: Quality depends on the chosen LLM model; newer models typically provide better results

## FAQ

### Q: Bilingual subtitles don't display correctly in my player. What should I do?

A: Most modern players (VLC, PotPlayer, MPC-HC, etc.) support multi-line subtitles. If display issues occur:
- Update your player to the latest version
- Adjust subtitle settings in your player
- Use monolingual mode instead

### Q: Can I keep only the source text without translation?

A: Uncheck the **"Bilingual Subtitles"** option to generate only translated text. If you need only the source text, use the original subtitle file directly.

### Q: Can I swap the order of source and translated text?

A: The current version uses a fixed format: "source text on top, translated text below". To adjust, manually edit the generated SRT file.

## Technical Details

- **Implementation**: After translation completes, source and translated text are combined or only translation is kept based on user selection
- **Format Standard**: Strictly follows SRT subtitle format specifications
- **Encoding**: UTF-8 encoding ensures support for all language characters

## Changelog

### v1.0 (2025-10-27)
- ✨ Added bilingual subtitle feature
- ✅ Support for displaying both source and translated text
- 💾 Automatic configuration save and load
- 📝 File naming automatically distinguishes monolingual and bilingual modes

