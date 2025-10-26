#!/usr/bin/env python3
"""
字幕断句工具 GUI 测试脚本
直接运行此脚本可以打开字幕分割工具窗口
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from videotrans.configure import config

def main():
    """启动字幕分割工具窗口"""
    # 初始化配置
    config.ROOT_DIR = str(Path(__file__).parent)
    config.HOME_DIR = str(Path.home() / "VideoTranslate")
    Path(config.HOME_DIR).mkdir(exist_ok=True)
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 导入并打开窗口
    from videotrans.winform import fn_split_srt
    fn_split_srt.openwin()
    
    print("✅ 字幕断句工具已启动！")
    print("📋 功能说明：")
    print("  • 自动将长时间跨度的字幕分割成短句")
    print("  • 支持中英文句子识别，按标点符号智能分割")
    print("  • 自动平均分配时间，保持时间轴连续性")
    print("\n💡 使用方法：")
    print("  1. 点击 '选择字幕文件' 按钮选择.srt文件")
    print("  2. 设置单条字幕最大持续时间（推荐3-5秒）")
    print("  3. 点击 '开始分割' 按钮")
    print("  4. 查看结果预览和保存路径")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

