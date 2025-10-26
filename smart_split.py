#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能字幕分割工具 - 独立启动脚本（规则引擎版本）
可以直接运行，无需启动整个应用

使用方法：
    uv run python smart_split.py
    或
    python smart_split.py
"""

import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

def main():
    """主函数"""
    import warnings
    warnings.filterwarnings('ignore')
    
    # 初始化配置
    from videotrans.configure import config
    config.ROOT_DIR = str(ROOT_DIR)
    config.HOME_DIR = str(Path.home() / "Videos" / "pyvideotrans")
    
    # 确保输出目录存在
    Path(config.HOME_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.HOME_DIR, "SmartSplit").mkdir(parents=True, exist_ok=True)
    
    # 设置默认语言
    config.defaulelang = 'zh'  # 或 'en'
    
    print("=" * 60)
    print("🎯 AI智能字幕分割工具（规则引擎版本）")
    print("=" * 60)
    print(f"工作目录: {config.HOME_DIR}")
    print(f"输出目录: {config.HOME_DIR}/SmartSplit")
    print("=" * 60)
    print()
    
    # 创建 Qt 应用
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    
    # 设置高DPI缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("AI智能字幕分割")
    app.setApplicationVersion("1.0.0")
    
    # 设置图标
    icon_path = ROOT_DIR / "videotrans" / "styles" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 初始化子窗口字典
    config.child_forms = {}
    
    # 打开智能分割窗口
    from videotrans.winform import fn_smart_split
    
    print("正在启动AI智能字幕分割窗口...")
    fn_smart_split.openwin()
    
    print("✅ 窗口已打开")
    print()
    print("使用说明：")
    print("1. 选择Whisper模型（推荐：large-v3-turbo）")
    print("2. 选择语言")
    print("3. 设置最大持续时间和最大词数")
    print("4. 选择视频文件")
    print("5. 可选：勾选'使用现有字幕'并选择.srt文件")
    print("6. 点击'开始生成智能字幕'")
    print()
    print("💡 特点：")
    print("   ✅ 完全免费，无需API")
    print("   ✅ 基于语法规则的智能断句")
    print("   ✅ 支持CPU/CUDA加速")
    print("   ⚠️  质量略低于LLM版本（约85分 vs 98分）")
    print()
    print("💡 如需更高质量，请使用：uv run python llm_split.py")
    print("=" * 60)
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

