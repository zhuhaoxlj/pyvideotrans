"""
智能字幕分割工具
自动将长时间跨度的字幕条目分割成短句，确保每次只显示一句话
"""

import re
import sys
from pathlib import Path


def parse_srt(srt_file):
    """解析SRT字幕文件"""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割成单独的字幕块
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        # 解析序号
        index = lines[0].strip()
        
        # 解析时间戳
        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', lines[1])
        if not time_match:
            continue
        
        start_time = time_match.group(1)
        end_time = time_match.group(2)
        
        # 解析文本（可能多行）
        text = '\n'.join(lines[2:])
        
        subtitles.append({
            'index': index,
            'start': start_time,
            'end': end_time,
            'text': text,
            'start_ms': time_to_ms(start_time),
            'end_ms': time_to_ms(end_time)
        })
    
    return subtitles


def time_to_ms(time_str):
    """将时间字符串转换为毫秒"""
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)


def ms_to_time(ms):
    """将毫秒转换为时间字符串"""
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    ms_part = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms_part:03d}"


def split_by_sentences(text):
    """将文本按句子分割
    
    支持英文和中文句子分割，特别处理双语字幕
    返回配对的句子列表
    """
    sentences = []
    
    # 检测是否为双语字幕（包含换行符）
    if '\n' in text:
        # 分离不同语言的部分（通常是英文和中文）
        parts = [p.strip() for p in text.split('\n') if p.strip()]
        
        if len(parts) == 2:
            # 双语字幕：英文和中文
            lang1_sentences = split_single_language_text(parts[0])
            lang2_sentences = split_single_language_text(parts[1])
            
            # 配对句子（取较长的列表长度）
            max_len = max(len(lang1_sentences), len(lang2_sentences))
            for i in range(max_len):
                # 获取对应的句子，如果不够就用空字符串
                s1 = lang1_sentences[i] if i < len(lang1_sentences) else ""
                s2 = lang2_sentences[i] if i < len(lang2_sentences) else ""
                
                # 组合成双语字幕
                if s1 and s2:
                    sentences.append(f"{s1}\n{s2}")
                elif s1:
                    sentences.append(s1)
                elif s2:
                    sentences.append(s2)
        else:
            # 多行文本，但不是标准双语格式，逐行处理
            for part in parts:
                sub_sentences = split_single_language_text(part)
                sentences.extend(sub_sentences)
        
        return sentences if sentences else [text]
    else:
        return split_single_language_text(text)


def split_single_language_text(text):
    """分割单一语言的文本"""
    sentences = []
    
    # 分割模式：句号、问号、感叹号后面跟空格或结尾
    # 英文: . ! ?
    # 中文: 。！？
    pattern = r'([^.!?。！？]+[.!?。！？]+\s*)'
    matches = re.findall(pattern, text)
    
    if matches:
        sentences = [m.strip() for m in matches if m.strip()]
        # 检查是否有剩余文本（没有结束标点的部分）
        remaining = re.sub(pattern, '', text).strip()
        if remaining:
            sentences.append(remaining)
    else:
        # 如果没有明确的句子分隔符，尝试按逗号或其他标点分割
        if len(text) > 100:  # 如果文本太长
            # 按逗号、分号等分割
            parts = re.split(r'[,，;；]\s*', text)
            sentences = [p.strip() for p in parts if p.strip()]
        else:
            sentences = [text]
    
    return sentences


def smart_split_subtitles(subtitles, max_duration_ms=3000):
    """智能分割字幕
    
    Args:
        subtitles: 原始字幕列表
        max_duration_ms: 单个字幕最大持续时间（毫秒），默认3秒
    
    Returns:
        新的字幕列表
    """
    new_subtitles = []
    new_index = 1
    
    for sub in subtitles:
        duration = sub['end_ms'] - sub['start_ms']
        text = sub['text']
        
        # 如果持续时间较短，直接保留
        if duration <= max_duration_ms:
            new_subtitles.append({
                'index': str(new_index),
                'start': sub['start'],
                'end': sub['end'],
                'text': text,
                'start_ms': sub['start_ms'],
                'end_ms': sub['end_ms']
            })
            new_index += 1
            continue
        
        # 如果持续时间较长，需要分割
        sentences = split_by_sentences(text)
        
        if len(sentences) <= 1:
            # 无法分割，保留原样
            new_subtitles.append({
                'index': str(new_index),
                'start': sub['start'],
                'end': sub['end'],
                'text': text,
                'start_ms': sub['start_ms'],
                'end_ms': sub['end_ms']
            })
            new_index += 1
            continue
        
        # 按句子数量平均分配时间
        time_per_sentence = duration / len(sentences)
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            # 计算这个句子的开始和结束时间
            sentence_start_ms = sub['start_ms'] + int(i * time_per_sentence)
            sentence_end_ms = sub['start_ms'] + int((i + 1) * time_per_sentence)
            
            # 确保最后一个句子的结束时间与原字幕一致
            if i == len(sentences) - 1:
                sentence_end_ms = sub['end_ms']
            
            new_subtitles.append({
                'index': str(new_index),
                'start': ms_to_time(sentence_start_ms),
                'end': ms_to_time(sentence_end_ms),
                'text': sentence.strip(),
                'start_ms': sentence_start_ms,
                'end_ms': sentence_end_ms
            })
            new_index += 1
    
    return new_subtitles


def save_srt(subtitles, output_file):
    """保存字幕为SRT格式"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for sub in subtitles:
            f.write(f"{sub['index']}\n")
            f.write(f"{sub['start']} --> {sub['end']}\n")
            f.write(f"{sub['text']}\n")
            f.write("\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python split_subtitles.py <字幕文件.srt> [最大持续时间(秒)]")
        print("示例: python split_subtitles.py input.srt 3")
        sys.exit(1)
    
    input_file = sys.argv[1]
    max_duration_sec = 3  # 默认3秒
    
    if len(sys.argv) >= 3:
        try:
            max_duration_sec = float(sys.argv[2])
        except ValueError:
            print("警告: 无效的最大持续时间，使用默认值3秒")
    
    if not Path(input_file).exists():
        print(f"错误: 文件不存在: {input_file}")
        sys.exit(1)
    
    print(f"正在处理: {input_file}")
    print(f"最大持续时间: {max_duration_sec}秒")
    
    # 解析字幕
    subtitles = parse_srt(input_file)
    print(f"原始字幕条目: {len(subtitles)}")
    
    # 智能分割
    new_subtitles = smart_split_subtitles(subtitles, max_duration_ms=int(max_duration_sec * 1000))
    print(f"分割后字幕条目: {len(new_subtitles)}")
    
    # 生成输出文件名
    input_path = Path(input_file)
    output_file = input_path.parent / f"{input_path.stem}_split{input_path.suffix}"
    
    # 保存
    save_srt(new_subtitles, output_file)
    print(f"已保存到: {output_file}")


if __name__ == "__main__":
    main()

