#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 main.py 的所有依赖关系
"""

import os
import ast
import sys
from pathlib import Path
from typing import Set, List

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def extract_imports_from_file(file_path: Path) -> Set[str]:
    """从Python文件中提取所有导入的模块"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
                    
    except Exception as e:
        print(f"解析文件失败 {file_path}: {e}")
    
    return imports

def get_module_file_path(module_name: str, base_dir: Path) -> List[Path]:
    """获取模块对应的文件路径"""
    paths = []
    
    # 处理 videotrans 开头的模块
    if module_name.startswith('videotrans'):
        parts = module_name.split('.')
        
        # 尝试作为包目录
        dir_path = base_dir / '/'.join(parts)
        if dir_path.is_dir():
            init_file = dir_path / '__init__.py'
            if init_file.exists():
                paths.append(init_file)
            # 递归添加包目录下的所有Python文件
            for py_file in dir_path.rglob('*.py'):
                paths.append(py_file)
        
        # 尝试作为模块文件
        file_path = base_dir / '/'.join(parts[:-1]) / f"{parts[-1]}.py"
        if file_path.exists():
            paths.append(file_path)
    
    return paths

def analyze_dependencies(start_file: Path, base_dir: Path) -> Set[Path]:
    """递归分析所有依赖的文件"""
    all_files = set()
    to_process = {start_file}
    processed = set()
    
    while to_process:
        current_file = to_process.pop()
        
        if current_file in processed:
            continue
        
        processed.add(current_file)
        all_files.add(current_file)
        
        print(f"分析: {current_file.relative_to(base_dir)}")
        
        # 提取导入
        imports = extract_imports_from_file(current_file)
        
        # 找到对应的文件
        for imp in imports:
            if imp.startswith('videotrans'):
                module_files = get_module_file_path(imp, base_dir)
                for module_file in module_files:
                    if module_file not in processed:
                        to_process.add(module_file)
    
    return all_files

def find_resource_files(base_dir: Path) -> Set[Path]:
    """查找需要的资源文件"""
    resources = set()
    
    # 样式文件
    styles_dir = base_dir / 'videotrans' / 'styles'
    if styles_dir.exists():
        for file in styles_dir.iterdir():
            if file.is_file():
                resources.add(file)
    
    # UI 资源
    ui_dark_dir = base_dir / 'videotrans' / 'ui' / 'dark'
    if ui_dark_dir.exists():
        for file in ui_dark_dir.rglob('*'):
            if file.is_file():
                resources.add(file)
    
    return resources

def main():
    print("开始分析 main.py 的依赖关系...")
    print("=" * 60)
    
    main_file = ROOT_DIR / 'main.py'
    
    # 分析Python依赖
    print("\n分析 Python 模块依赖...")
    python_files = analyze_dependencies(main_file, ROOT_DIR)
    
    print(f"\n找到 {len(python_files)} 个Python文件")
    
    # 查找资源文件
    print("\n查找资源文件...")
    resource_files = find_resource_files(ROOT_DIR)
    print(f"找到 {len(resource_files)} 个资源文件")
    
    # 所有需要保留的文件
    all_needed_files = python_files | resource_files
    
    # 添加配置文件和其他必要文件
    essential_files = [
        ROOT_DIR / 'requirements.txt',
        ROOT_DIR / 'requirements-mac.txt',
        ROOT_DIR / 'requirements-colab.txt',
        ROOT_DIR / 'pyproject.toml',
        ROOT_DIR / 'uv.lock',
        ROOT_DIR / 'README.md',
        ROOT_DIR / 'LICENSE',
        ROOT_DIR / 'version.json',
    ]
    
    for file in essential_files:
        if file.exists():
            all_needed_files.add(file)
    
    # 输出需要保留的文件列表
    output_file = ROOT_DIR / 'needed_files.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for file in sorted(all_needed_files):
            try:
                rel_path = file.relative_to(ROOT_DIR)
                f.write(f"{rel_path}\n")
            except:
                f.write(f"{file}\n")
    
    print(f"\n需要保留的文件列表已保存到: {output_file}")
    print(f"总共需要保留: {len(all_needed_files)} 个文件")
    
    # 统计可以删除的文件
    print("\n统计可以删除的文件...")
    all_python_files = set(ROOT_DIR.rglob('*.py'))
    deletable_files = all_python_files - python_files
    
    print(f"可以删除的 Python 文件: {len(deletable_files)} 个")
    
    # 保存可删除文件列表
    deletable_output = ROOT_DIR / 'deletable_files.txt'
    with open(deletable_output, 'w', encoding='utf-8') as f:
        for file in sorted(deletable_files):
            try:
                rel_path = file.relative_to(ROOT_DIR)
                # 跳过一些特殊目录
                if any(part in rel_path.parts for part in ['venv', '__pycache__', '.git', 'models', 'logs', 'tmp']):
                    continue
                f.write(f"{rel_path}\n")
            except:
                pass
    
    print(f"可删除的文件列表已保存到: {deletable_output}")

if __name__ == '__main__':
    main()

