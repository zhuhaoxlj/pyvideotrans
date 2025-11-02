#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM智能字幕分割工具 - 独立启动脚本 (get_srt_zimu 版本)
可以直接运行，无需启动整个应用

使用方法：
    python llm_split.py
    或
    uv run python llm_split.py
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
    
    # 设置工作目录
    HOME_DIR = str(Path.home() / "Videos" / "pyvideotrans" / "get_srt_zimu")
    
    # 确保输出目录存在
    Path(HOME_DIR).mkdir(parents=True, exist_ok=True)
    Path(HOME_DIR, "output").mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🤖 LLM智能字幕分割工具 (get_srt_zimu)")
    print("=" * 60)
    print(f"项目目录: {ROOT_DIR}")
    print(f"工作目录: {HOME_DIR}")
    print(f"输出目录: {HOME_DIR}/output")
    print("=" * 60)
    print()
    
    # 创建 Qt 应用
    from PySide6.QtWidgets import QApplication, QMainWindow
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    
    # 设置高DPI缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("LLM智能字幕分割")
    app.setApplicationVersion("1.0.0")
    
    # 设置图标（如果存在）
    icon_path = ROOT_DIR / "resource" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 导入 split_view
    from ui.split_view import SplitView
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("🤖 LLM智能字幕分割")
    main_window.setMinimumSize(1200, 800)
    
    # 创建并设置 split_view
    split_view = SplitView()
    main_window.setCentralWidget(split_view)
    
    # 显示窗口
    main_window.show()
    
    print("✅ 窗口已打开")
    print()
    print("使用说明：")
    print()
    print("【方式1：仅重新分割现有字幕】（推荐入门）")
    print("  1. 点击'📂 选择 SRT 文件'")
    print("  2. 选择你要优化的字幕文件")
    print("  3. 配置 LLM 设置：")
    print("     - 选择提供商（推荐：SiliconFlow）")
    print("     - 输入 API Key")
    print("     - 选择模型")
    print("  4. 点击'✨ 开始智能分割'")
    print()
    print("【方式2：从视频生成+智能分割】（完整流程）")
    print("  1. 勾选'从视频生成字幕'")
    print("  2. 点击'📁 选择视频文件'")
    print("  3. 可选：勾选'使用现有字幕'并选择原字幕")
    print("  4. 配置 Whisper 设置（语言、模型）")
    print("  5. 配置 LLM 设置")
    print("  6. 点击'✨ 开始智能分割'")
    print()
    print("💡 LLM 提供商推荐：")
    print("   ✅ SiliconFlow - 国内速度快，价格低")
    print("      https://siliconflow.cn/")
    print("      推荐模型：Qwen/Qwen2.5-7B-Instruct")
    print()
    print("   ✅ OpenAI - 质量最高")
    print("      https://platform.openai.com/api-keys")
    print("      推荐模型：gpt-4o-mini")
    print()
    print("   ✅ Claude - 高质量")
    print("      https://console.anthropic.com/")
    print("      推荐模型：claude-3-5-sonnet-20241022")
    print()
    print("   ✅ DeepSeek - 国产大模型，价格实惠")
    print("      https://platform.deepseek.com/")
    print("      推荐模型：deepseek-chat")
    print()
    print("🎯 功能特性：")
    print("   • 智能断句 - 基于语义理解，而非简单规则")
    print("   • 流式输出 - 实时查看 LLM 处理过程")
    print("   • 自动映射 - 精确保持时间戳同步")
    print("   • 缓存机制 - 避免重复识别（Whisper）")
    print("   • API 管理 - 自动保存配置到 .env")
    print()
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

