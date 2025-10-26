"""
使用 Whisper AI 重新生成精确的字幕
自动识别语音并生成准确的时间对齐字幕
"""

import sys
import os
from pathlib import Path


def regenerate_subtitles_with_whisper(video_file, language='en', model_size='base'):
    """
    使用 Whisper 重新生成字幕
    
    Args:
        video_file: 视频文件路径
        language: 语言代码 (en, zh, ja, etc.)
        model_size: 模型大小 (tiny, base, small, medium, large)
    
    Returns:
        生成的SRT文件路径
    """
    try:
        import whisper
    except ImportError:
        print("❌ 未安装 Whisper，正在安装...")
        print("请运行: pip install openai-whisper")
        sys.exit(1)
    
    print(f"📥 加载 Whisper 模型: {model_size}")
    model = whisper.load_model(model_size)
    
    print(f"🎤 开始识别语音: {video_file}")
    result = model.transcribe(
        video_file,
        language=language,
        word_timestamps=True,  # 获取单词级别的时间戳
        verbose=True
    )
    
    # 生成 SRT 文件
    video_path = Path(video_file)
    output_file = video_path.parent / f"{video_path.stem}_whisper.srt"
    
    print(f"💾 保存字幕到: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result['segments'], 1):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n")
            f.write("\n")
    
    print(f"✅ 完成！共生成 {len(result['segments'])} 条字幕")
    return str(output_file)


def format_timestamp(seconds):
    """将秒转换为 SRT 时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("🎬 Whisper AI 字幕生成器")
        print("=" * 70)
        print("\n用法:")
        print("  python regenerate_subtitles.py <视频文件> [语言] [模型大小]")
        print("\n参数:")
        print("  视频文件    - 视频文件路径 (必需)")
        print("  语言       - 语言代码，默认: en")
        print("              en=英语, zh=中文, ja=日语, es=西班牙语, etc.")
        print("  模型大小    - 模型大小，默认: base")
        print("              tiny   - 最快，准确度低")
        print("              base   - 快速，准确度中等 (推荐)")
        print("              small  - 较慢，准确度较高")
        print("              medium - 慢，准确度高")
        print("              large  - 最慢，准确度最高")
        print("\n示例:")
        print("  python regenerate_subtitles.py video.mp4")
        print("  python regenerate_subtitles.py video.mp4 en base")
        print("  python regenerate_subtitles.py video.mp4 zh small")
        print("=" * 70)
        sys.exit(1)
    
    video_file = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'en'
    model_size = sys.argv[3] if len(sys.argv) > 3 else 'base'
    
    if not Path(video_file).exists():
        print(f"❌ 错误: 文件不存在: {video_file}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("🎬 Whisper AI 字幕生成器")
    print("=" * 70)
    print(f"视频文件: {video_file}")
    print(f"语言: {language}")
    print(f"模型: {model_size}")
    print("=" * 70 + "\n")
    
    output_file = regenerate_subtitles_with_whisper(video_file, language, model_size)
    
    print("\n" + "=" * 70)
    print("✅ 字幕生成完成！")
    print(f"📁 输出文件: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()

