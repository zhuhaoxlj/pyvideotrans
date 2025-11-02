"""
SRT Utilities - Merge and manipulate SRT files
"""

from pathlib import Path
import re


def merge_srt_files(srt_files, project_name):
    """Merge multiple SRT files into one"""
    if len(srt_files) == 1:
        # No need to merge, just return the single file
        return srt_files[0]
    
    merged_path = Path(srt_files[0]).parent / f"{project_name}_merged.srt"
    
    merged_subtitles = []
    subtitle_index = 1
    
    for file_index, srt_path in enumerate(srt_files):
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            continue
            
        # Split into subtitle blocks
        blocks = content.split('\n\n')
        
        for block in blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            # Parse time range (line 1 is index, line 2 is time range)
            time_line = lines[1]
            text_lines = lines[2:]
            
            # Adjust time for segment offset
            adjusted_time = adjust_srt_time(time_line, file_index)
            
            # Build new subtitle block
            subtitle_text = '\n'.join(text_lines)
            merged_subtitles.append(f"{subtitle_index}\n{adjusted_time}\n{subtitle_text}")
            subtitle_index += 1
    
    # Write merged file
    with open(merged_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(merged_subtitles))
        if merged_subtitles:
            f.write('\n\n')
    
    return str(merged_path)


def adjust_srt_time(time_range, segment_index):
    """Adjust SRT time range for segment offset"""
    if segment_index == 0:
        return time_range
    
    # Parse time range
    match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_range)
    if not match:
        return time_range
    
    start_time = match.group(1)
    end_time = match.group(2)
    
    # Adjust times
    adjusted_start = adjust_single_time(start_time, segment_index)
    adjusted_end = adjust_single_time(end_time, segment_index)
    
    return f"{adjusted_start} --> {adjusted_end}"


def adjust_single_time(time_str, segment_index):
    """Adjust a single SRT timestamp"""
    # Parse time: HH:MM:SS,mmm
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split(',')
    seconds = int(seconds_parts[0])
    milliseconds = seconds_parts[1]
    
    # Add offset (10 minutes per segment)
    offset_minutes = segment_index * 10
    
    total_minutes = hours * 60 + minutes + offset_minutes
    new_hours = total_minutes // 60
    new_minutes = total_minutes % 60
    
    return f"{new_hours:02d}:{new_minutes:02d}:{seconds:02d},{milliseconds}"


def parse_srt(srt_path):
    """Parse an SRT file and return list of subtitles"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    subtitles = []
    blocks = content.split('\n\n')
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        time_line = lines[1]
        text = '\n'.join(lines[2:])
        
        match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
        if match:
            subtitles.append({
                'start': match.group(1),
                'end': match.group(2),
                'text': text
            })
    
    return subtitles

