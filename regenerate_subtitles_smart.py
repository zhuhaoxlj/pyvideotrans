"""
基于 Faster-Whisper AI 的智能字幕生成和断句工具
使用词级时间戳精确分割字幕，而不是简单的平均分配
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple


def regenerate_with_word_level_timestamps(
    video_file: str, 
    language: str = 'en', 
    model_size: str = 'large-v3-turbo',
    max_duration: float = 5.0,
    max_words: int = 15,
    device: str = 'cpu'
):
    """
    使用 Faster-Whisper 重新生成字幕，基于词级时间戳智能断句
    
    Args:
        video_file: 视频文件路径
        language: 语言代码 (en, zh, ja, etc.)
        model_size: 模型大小 (base, small, medium, large-v3, large-v3-turbo)
        max_duration: 单条字幕最大持续时间（秒）
        max_words: 单条字幕最大词数
        device: 设备类型 (cpu, cuda, mps)
    
    Returns:
        生成的SRT文件路径
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("❌ 未安装 faster-whisper")
        print("请运行: pip install faster-whisper")
        sys.exit(1)
    
    print(f"📥 加载 Faster-Whisper 模型: {model_size}")
    
    # 显示设备信息
    device_names = {
        'cpu': 'CPU',
        'cuda': 'CUDA (NVIDIA GPU)',
        'mps': 'MPS (Apple Silicon GPU)'
    }
    print(f"⚙️  设备: {device_names.get(device, device.upper())}")
    
    # 根据设备选择计算类型
    if device == 'cuda':
        compute_type = "float16"
    elif device == 'mps':
        compute_type = "float16"
    else:
        compute_type = "int8"
    
    # 加载模型
    try:
        model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            download_root="./models"
        )
    except ValueError as e:
        if 'unsupported device' in str(e).lower() and device == 'mps':
            # faster-whisper 还不支持 MPS，回退到 CPU
            print("⚠️  faster-whisper 暂不支持 MPS")
            print("📥 自动回退到 CPU 模式...")
            device = 'cpu'
            compute_type = 'int8'
            model = WhisperModel(
                model_size,
                device='cpu',
                compute_type='int8',
                download_root="./models"
            )
        else:
            raise
    
    print(f"🎤 开始识别语音: {video_file}")
    print(f"🌍 语言: {language}")
    print(f"⏱️  最大持续时间: {max_duration}秒")
    print(f"📝 最大词数: {max_words}词")
    print(f"⏳ 此过程可能需要几分钟，请耐心等待...")
    
    # 转录音频，获取词级时间戳
    import time
    start_time = time.time()
    segments, info = model.transcribe(
        video_file,
        language=language if language != 'auto' else None,
        word_timestamps=True,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(
            threshold=0.5,
            min_speech_duration_ms=250,
            max_speech_duration_s=float('inf'),
            min_silence_duration_ms=2000,
            speech_pad_ms=400
        )
    )
    transcribe_time = time.time() - start_time
    
    print(f"✅ 识别完成！检测到的语言: {info.language} (耗时: {transcribe_time:.1f}秒)")
    print(f"📊 开始收集词级时间戳...")
    
    # 收集所有词 - 添加进度反馈
    collect_start = time.time()
    all_words = []
    segment_count = 0
    for segment in segments:
        segment_count += 1
        if segment_count % 10 == 0:  # 每10个片段报告一次
            print(f"   处理片段: {segment_count}...")
        
        if hasattr(segment, 'words') and segment.words:
            for word in segment.words:
                all_words.append({
                    'word': word.word,  # 保留原始空格
                    'start': word.start,
                    'end': word.end
                })
    
    if not all_words:
        print("❌ 未检测到任何语音内容")
        sys.exit(1)
    
    collect_time = time.time() - collect_start
    print(f"✅ 收集完成！共 {len(all_words)} 个词，{segment_count} 个片段 (耗时: {collect_time:.1f}秒)")
    print(f"🔄 开始智能断句处理...")
    
    # 智能分割成字幕条目
    split_start = time.time()
    subtitles = smart_split_by_words(
        all_words, 
        max_duration=max_duration,
        max_words=max_words,
        language=language
    )
    split_time = time.time() - split_start
    
    print(f"✅ 断句完成！生成 {len(subtitles)} 条字幕 (耗时: {split_time:.1f}秒)")
    
    # 保存为SRT
    video_path = Path(video_file)
    output_file = video_path.parent / f"{video_path.stem}_smart.srt"
    
    save_srt(subtitles, output_file)
    
    print(f"💾 保存字幕到: {output_file}")
    print(f"\n🎉 完成！")
    
    # 打印统计信息
    print_statistics(subtitles, max_duration)
    
    return str(output_file)


def smart_split_by_words(
    words: List[Dict], 
    max_duration: float = 5.0,
    max_words: int = 15,
    language: str = 'en'
) -> List[Dict]:
    """
    基于词级时间戳智能分割字幕
    
    策略:
    1. 按句子边界分割（句号、问号、感叹号）
    2. 如果句子太长，按从句边界分割（逗号、分号）
    3. 如果还太长，按最大词数强制分割
    4. 如果持续时间超过阈值，在合适的位置分割
    """
    if not words:
        return []
    
    subtitles = []
    current_words = []
    current_start = words[0]['start']
    total_words = len(words)
    
    # 句子结束标点
    sentence_ends = {'.', '!', '?', '。', '！', '？'}
    # 从句分隔标点
    clause_separators = {',', ';', ':', '，', '；', '：'}
    
    # 进度报告间隔
    report_interval = max(100, total_words // 10)  # 至少每100个词或10%报告一次
    
    for i, word in enumerate(words):
        # 定期报告进度
        if i > 0 and i % report_interval == 0:
            progress = int((i / total_words) * 100)
            print(f"   断句进度: {progress}% ({i}/{total_words} 词)")
        
        current_words.append(word)
        
        # 当前字幕的持续时间
        duration = word['end'] - current_start
        
        # 检查是否需要分割
        should_split = False
        split_reason = ""
        
        # 1. 检查句子结束
        word_text = word['word'].strip()
        if word_text and word_text[-1] in sentence_ends:
            should_split = True
            split_reason = "sentence_end"
        
        # 2. 检查是否超过最大持续时间
        elif duration >= max_duration:
            # 在最近的从句边界分割
            if word_text and word_text[-1] in clause_separators:
                should_split = True
                split_reason = "duration_clause"
            # 或者直接分割
            elif len(current_words) >= 3:  # 至少3个词才分割
                should_split = True
                split_reason = "duration_force"
        
        # 3. 检查是否超过最大词数
        elif len(current_words) >= max_words:
            # 尝试在从句边界分割
            if word_text and word_text[-1] in clause_separators:
                should_split = True
                split_reason = "words_clause"
            # 或者强制分割
            elif len(current_words) > max_words + 3:
                should_split = True
                split_reason = "words_force"
        
        # 4. 从句边界且已有足够词数（优化可读性）
        elif len(current_words) >= 5 and word_text and word_text[-1] in clause_separators:
            # 检查下一个词是否会导致过长
            if i + 1 < len(words):
                next_duration = words[i + 1]['end'] - current_start
                if next_duration > max_duration * 0.8:  # 接近阈值
                    should_split = True
                    split_reason = "preemptive"
        
        # 执行分割
        if should_split and current_words:
            # 创建字幕条目
            subtitle = {
                'start': current_start,
                'end': current_words[-1]['end'],
                'text': ''.join([w['word'] for w in current_words]).strip(),  # join后再strip首尾空格
                'words': len(current_words),
                'duration': current_words[-1]['end'] - current_start,
                'reason': split_reason
            }
            subtitles.append(subtitle)
            
            # 重置
            current_words = []
            if i + 1 < len(words):
                current_start = words[i + 1]['start']
    
    # 添加最后一个字幕
    if current_words:
        subtitle = {
            'start': current_start,
            'end': current_words[-1]['end'],
            'text': ''.join([w['word'] for w in current_words]).strip(),  # join后再strip首尾空格
            'words': len(current_words),
            'duration': current_words[-1]['end'] - current_start,
            'reason': 'final'
        }
        subtitles.append(subtitle)
    
    return subtitles


def format_timestamp(seconds: float) -> str:
    """将秒转换为 SRT 时间格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def save_srt(subtitles: List[Dict], output_file: Path):
    """保存字幕为SRT格式"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(sub['start'])} --> {format_timestamp(sub['end'])}\n")
            f.write(f"{sub['text']}\n")
            f.write("\n")


def print_statistics(subtitles: List[Dict], max_duration: float):
    """打印统计信息"""
    if not subtitles:
        return
    
    durations = [s['duration'] for s in subtitles]
    word_counts = [s['words'] for s in subtitles]
    
    print("\n" + "=" * 70)
    print("📊 字幕统计信息")
    print("=" * 70)
    print(f"总条目数: {len(subtitles)}")
    print(f"\n⏱️  持续时间:")
    print(f"  平均: {sum(durations) / len(durations):.2f}秒")
    print(f"  最短: {min(durations):.2f}秒")
    print(f"  最长: {max(durations):.2f}秒")
    print(f"  超过阈值({max_duration}秒)的: {sum(1 for d in durations if d > max_duration)} 条")
    
    print(f"\n📝 词数:")
    print(f"  平均: {sum(word_counts) / len(word_counts):.1f}词")
    print(f"  最少: {min(word_counts)}词")
    print(f"  最多: {max(word_counts)}词")
    
    print(f"\n📋 分割原因统计:")
    reasons = {}
    for sub in subtitles:
        reason = sub.get('reason', 'unknown')
        reasons[reason] = reasons.get(reason, 0) + 1
    
    reason_names = {
        'sentence_end': '句子结束',
        'duration_clause': '时长限制(从句)',
        'duration_force': '时长限制(强制)',
        'words_clause': '词数限制(从句)',
        'words_force': '词数限制(强制)',
        'preemptive': '预防性分割',
        'final': '最后一条'
    }
    
    for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        name = reason_names.get(reason, reason)
        percentage = count / len(subtitles) * 100
        print(f"  {name}: {count} 条 ({percentage:.1f}%)")
    
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("🎬 Faster-Whisper 智能字幕生成器（基于词级时间戳）")
        print("=" * 70)
        print("\n用法:")
        print("  python regenerate_subtitles_smart.py <视频文件> [选项]")
        print("\n参数:")
        print("  视频文件           - 视频文件路径 (必需)")
        print("  --language LANG    - 语言代码，默认: en")
        print("                      en=英语, zh=中文, ja=日语, es=西班牙语")
        print("  --model MODEL      - 模型大小，默认: large-v3-turbo")
        print("                      base, small, medium, large-v3, large-v3-turbo")
        print("  --max-duration SEC - 单条字幕最大持续时间(秒)，默认: 5")
        print("  --max-words NUM    - 单条字幕最大词数，默认: 15")
        print("  --device DEVICE    - 设备类型: cpu, cuda, mps，默认: cpu")
        print("\n示例:")
        print("  # 基础用法")
        print("  python regenerate_subtitles_smart.py video.mp4")
        print("\n  # 中文视频，使用CUDA加速")
        print("  python regenerate_subtitles_smart.py video.mp4 --language zh --device cuda")
        print("\n  # Mac M1/M2，使用MPS加速")
        print("  python regenerate_subtitles_smart.py video.mp4 --language en --device mps")
        print("\n  # 自定义参数")
        print("  python regenerate_subtitles_smart.py video.mp4 --max-duration 4 --max-words 12")
        print("\n✨ 特点:")
        print("  • 基于词级时间戳，精确到每个词")
        print("  • 智能识别句子和从句边界")
        print("  • 自动优化字幕长度和持续时间")
        print("  • 比简单平均分配更准确")
        print("=" * 70)
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    # 解析参数
    language = 'en'
    model_size = 'large-v3-turbo'
    max_duration = 5.0
    max_words = 15
    device = 'cpu'
    
    # 注意：faster-whisper 暂不支持 MPS
    # 如果用户指定 --device mps，程序会自动回退到 CPU
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--language' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--model' and i + 1 < len(sys.argv):
            model_size = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--max-duration' and i + 1 < len(sys.argv):
            max_duration = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--max-words' and i + 1 < len(sys.argv):
            max_words = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--device' and i + 1 < len(sys.argv):
            device = sys.argv[i + 1].lower()
            i += 2
        elif sys.argv[i] == '--cuda':  # 向后兼容
            device = 'cuda'
            i += 1
        else:
            print(f"⚠️  未知参数: {sys.argv[i]}")
            i += 1
    
    if not Path(video_file).exists():
        print(f"❌ 错误: 文件不存在: {video_file}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("🎬 Faster-Whisper 智能字幕生成器")
    print("=" * 70)
    print(f"视频文件: {video_file}")
    print(f"语言: {language}")
    print(f"模型: {model_size}")
    print(f"最大持续时间: {max_duration}秒")
    print(f"最大词数: {max_words}词")
    print(f"设备: {device.upper()}")
    print("=" * 70 + "\n")
    
    output_file = regenerate_with_word_level_timestamps(
        video_file,
        language=language,
        model_size=model_size,
        max_duration=max_duration,
        max_words=max_words,
        device=device
    )
    
    print("\n" + "=" * 70)
    print("✅ 字幕生成完成！")
    print(f"📁 输出文件: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()

