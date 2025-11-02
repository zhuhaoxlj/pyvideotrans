"""
FCPXML Generator - Generate Final Cut Pro XML files from SRT
"""

from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
from utils.srt_utils import parse_srt


def generate_fcpxml(srt_path, fps, project_name, language):
    """Generate FCPXML file from SRT"""
    subtitles = parse_srt(srt_path)
    
    if not subtitles:
        raise ValueError("No subtitles found in SRT file")
    
    # Calculate total duration
    last_subtitle = subtitles[-1]
    total_frame = srt_time_to_frame(last_subtitle['end'], fps)
    hundred_fold_total_frame = 100 * total_frame
    hundred_fold_fps = int(fps * 100)
    
    # Create XML structure
    fcpxml = ET.Element('fcpxml', version='1.9')
    
    # Resources
    resources = ET.SubElement(fcpxml, 'resources')
    
    # Format
    format_elem = ET.SubElement(resources, 'format',
        id='r1',
        name=f'FFVideoFormat1080p{hundred_fold_fps}',
        frameDuration=f'100/{hundred_fold_fps}s',
        width='1920',
        height='1080',
        colorSpace='1-1-1 (Rec. 709)'
    )
    
    # Effect
    effect = ET.SubElement(resources, 'effect',
        id='r2',
        name='Basic Title',
        uid='.../Titles.localized/Bumper:Opener.localized/Basic Title.localized/Basic Title.moti'
    )
    
    # Library
    library = ET.SubElement(fcpxml, 'library')
    
    # Event
    event = ET.SubElement(library, 'event', name='Whisper Auto Captions')
    
    # Project
    project = ET.SubElement(event, 'project', name=project_name)
    
    # Sequence
    sequence = ET.SubElement(project, 'sequence',
        format='r1',
        tcStart='0s',
        tcFormat='NDF',
        audioLayout='stereo',
        audioRate='48k',
        duration=f'{total_frame}/{hundred_fold_fps}s'
    )
    
    # Spine
    spine = ET.SubElement(sequence, 'spine')
    
    # Gap
    gap = ET.SubElement(spine, 'gap',
        name='Gap',
        offset='0s',
        duration=f'{hundred_fold_total_frame}/{hundred_fold_fps}s'
    )
    
    # Add titles for each subtitle
    is_chinese = language in ["Chinese Simplified", "Chinese Traditional"]
    
    for i, subtitle in enumerate(subtitles):
        offset_frame = srt_time_to_frame(subtitle['start'], fps)
        end_frame = srt_time_to_frame(subtitle['end'], fps)
        duration_frame = end_frame - offset_frame
        
        hundred_fold_offset = 100 * offset_frame
        hundred_fold_duration = 100 * duration_frame
        
        subtitle_text = subtitle['text']
        
        # Format English text if too long
        if language == "English" and len(subtitle_text.split()) > 16:
            subtitle_text = format_text(subtitle_text)
        
        # Create title element
        title = ET.SubElement(gap, 'title',
            ref='r2',
            lane='1',
            offset=f'{hundred_fold_offset}/{hundred_fold_fps}s',
            duration=f'{hundred_fold_duration}/{hundred_fold_fps}s',
            name=f'{subtitle_text} - Basic Title'
        )
        
        # Position parameter
        param1 = ET.SubElement(title, 'param',
            name='Position',
            key='9999/999166631/999166633/1/100/101',
            value='0 -465'
        )
        
        # Flatten parameter
        param2 = ET.SubElement(title, 'param',
            name='Flatten',
            key='999/999166631/999166633/2/351',
            value='1'
        )
        
        # Alignment parameter
        param3 = ET.SubElement(title, 'param',
            name='Alignment',
            key='9999/999166631/999166633/2/354/999169573/401',
            value='1 (Center)'
        )
        
        # Text
        text_elem = ET.SubElement(title, 'text')
        text_style = ET.SubElement(text_elem, 'text-style', ref=f'ts{i}')
        text_style.text = subtitle_text
        
        # Text style definition
        text_style_def = ET.SubElement(title, 'text-style-def', id=f'ts{i}')
        
        if is_chinese:
            # Chinese text style
            text_style2 = ET.SubElement(text_style_def, 'text-style',
                font='PingFang SC',
                fontSize='50',
                fontFace='Semibold',
                fontColor='1 1 1 1',
                bold='1',
                shadowColor='0 0 0 0.75',
                shadowOffset='4 315',
                alignment='center'
            )
        else:
            # English text style
            text_style2 = ET.SubElement(text_style_def, 'text-style',
                font='Helvetica',
                fontSize='45',
                fontFace='Regular',
                fontColor='1 1 1 1',
                shadowColor='0 0 0 0.75',
                shadowOffset='4 315',
                alignment='center'
            )
    
    # Convert to pretty XML string
    xml_str = prettify_xml(fcpxml)
    
    # Write to file
    output_path = Path(srt_path).parent / f"{project_name}.fcpxml"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    return str(output_path)


def srt_time_to_frame(srt_time, fps):
    """Convert SRT time to frame number"""
    # Parse: HH:MM:SS,mmm
    parts = srt_time.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split(',')
    seconds = int(seconds_parts[0])
    milliseconds = int(seconds_parts[1])
    
    # Convert to total milliseconds
    total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
    
    # Convert to frames
    frame = int(total_ms / (1000 / fps))
    return frame


def format_text(full_text):
    """Format text by breaking into lines of 16 words"""
    words = full_text.split()
    lines = []
    for i in range(0, len(words), 16):
        line = ' '.join(words[i:i+16])
        lines.append(line)
    return '\n'.join(lines)


def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')

