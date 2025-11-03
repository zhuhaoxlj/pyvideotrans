#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理项目中不需要的文件
"""

import os
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).parent

# 需要保留的文件列表（从 needed_files.txt 读取）
needed_files = set()
with open(ROOT_DIR / 'needed_files.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            needed_files.add(ROOT_DIR / line)

# 忽略的目录（不删除，也不进入）
IGNORE_DIRS = {
    'venv', '.venv', '__pycache__', '.git', 'models', 'logs', 'tmp', 
    'uvr5_weights', 'dubbing_cache', '.pytest_cache', '.mypy_cache',
    'node_modules', 'dist', 'build', '.eggs', '*.egg-info'
}

# 需要删除的目录（整个目录删除）
DIRS_TO_DELETE = [
    'get_srt_zimu',  # 这个目录不在 main.py 的依赖中
    'docs',  # 文档目录
]

# 需要删除的根目录文件（明确不需要的）
FILES_TO_DELETE = [
    'api.py',
    'cli.py',
    'down_hf-mirror.py',
    'down_huggingface.py',
    'llm_split.py',
    'regenerate_subtitles.py',
    'regenerate_subtitles_smart.py',
    'smart_split.py',
    'sp.py',
    'sp_vas.py',
    'split_subtitles.py',
    'test_fps_detection.py',
    'test_split_gui.py',
    'test_whisper_cache.py',
    'testcuda.py',
    'whisper_error_checker.py',
    'whisper_timestamp_checker.py',
    'analyze_dependencies.py',  # 这个脚本本身也可以删除了
    'clean_project.py',  # 执行后可以删除自己
]

def should_ignore_dir(dir_path: Path) -> bool:
    """检查目录是否应该忽略"""
    return any(ignore_name in dir_path.parts for ignore_name in IGNORE_DIRS)

def delete_file(file_path: Path):
    """删除文件"""
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"✓ 删除文件: {file_path.relative_to(ROOT_DIR)}")
            return True
    except Exception as e:
        print(f"✗ 删除失败: {file_path.relative_to(ROOT_DIR)} - {e}")
    return False

def delete_directory(dir_path: Path):
    """删除目录"""
    try:
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            print(f"✓ 删除目录: {dir_path.relative_to(ROOT_DIR)}")
            return True
    except Exception as e:
        print(f"✗ 删除目录失败: {dir_path.relative_to(ROOT_DIR)} - {e}")
    return False

def main():
    print("开始清理项目...")
    print("=" * 60)
    
    deleted_files = 0
    deleted_dirs = 0
    
    # 删除指定的目录
    print("\n删除不需要的目录...")
    for dir_name in DIRS_TO_DELETE:
        dir_path = ROOT_DIR / dir_name
        if delete_directory(dir_path):
            deleted_dirs += 1
    
    # 删除根目录下不需要的文件
    print("\n删除根目录下不需要的文件...")
    for file_name in FILES_TO_DELETE:
        file_path = ROOT_DIR / file_name
        if delete_file(file_path):
            deleted_files += 1
    
    # 遍历项目目录，删除不需要的 Python 文件
    print("\n扫描并删除不需要的 Python 文件...")
    
    for py_file in ROOT_DIR.rglob('*.py'):
        # 忽略特定目录
        if should_ignore_dir(py_file):
            continue
        
        # 如果不在需要保留的列表中，删除
        if py_file not in needed_files:
            if delete_file(py_file):
                deleted_files += 1
    
    # 删除其他不需要的文件类型
    print("\n删除其他不需要的文件...")
    
    # .sh 脚本文件（除了可能需要的）
    keep_scripts = {'setup_subtitle_integration.sh'}
    for sh_file in ROOT_DIR.glob('*.sh'):
        if sh_file.name not in keep_scripts:
            if delete_file(sh_file):
                deleted_files += 1
    
    # .bat 文件（Windows批处理文件）
    for bat_file in ROOT_DIR.glob('*.bat'):
        if delete_file(bat_file):
            deleted_files += 1
    
    # .md 文件（文档，除了 README.md）
    for md_file in ROOT_DIR.glob('*.md'):
        if md_file.name != 'README.md' and md_file.name != 'LICENSE':
            if delete_file(md_file):
                deleted_files += 1
    
    # JSON 配置文件（不在需要列表中的）
    keep_json = {'version.json'}
    for json_file in ROOT_DIR.glob('*.json'):
        if json_file.name not in keep_json and json_file not in needed_files:
            if delete_file(json_file):
                deleted_files += 1
    
    # 清理临时文件和辅助文件
    temp_files = [
        'needed_files.txt',
        'deletable_files.txt',
    ]
    for temp_file in temp_files:
        temp_path = ROOT_DIR / temp_file
        if delete_file(temp_path):
            deleted_files += 1
    
    print("\n" + "=" * 60)
    print(f"清理完成！")
    print(f"删除了 {deleted_dirs} 个目录")
    print(f"删除了 {deleted_files} 个文件")
    print("=" * 60)
    
    # 显示保留的主要目录结构
    print("\n保留的主要目录结构:")
    print("├── main.py  （主入口）")
    print("├── videotrans/  （核心模块）")
    print("│   ├── component/  （UI组件）")
    print("│   ├── configure/  （配置）")
    print("│   ├── mainwin/  （主窗口）")
    print("│   ├── winform/  （功能窗口）")
    print("│   ├── ui/  （UI定义）")
    print("│   ├── util/  （工具函数）")
    print("│   ├── translator/  （翻译模块）")
    print("│   ├── tts/  （语音合成）")
    print("│   ├── recognition/  （语音识别）")
    print("│   ├── task/  （任务处理）")
    print("│   ├── process/  （处理流程）")
    print("│   ├── separate/  （音频分离）")
    print("│   └── styles/  （样式文件）")
    print("├── requirements.txt")
    print("├── pyproject.toml")
    print("└── README.md")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        import traceback
        traceback.print_exc()

