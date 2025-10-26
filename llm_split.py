#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM智能字幕分割工具 - 独立启动脚本
可以直接运行，无需启动整个应用

使用方法：
    uv run python llm_split.py
    或
    python llm_split.py
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
    print("🤖 LLM智能字幕分割工具")
    print("=" * 60)
    print(f"工作目录: {config.HOME_DIR}")
    print(f"输出目录: {config.HOME_DIR}/SmartSplit")
    print("=" * 60)
    print()
    
    # 创建 Qt 应用
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QTranslator
    from PySide6.QtGui import QIcon
    
    # 设置高DPI缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("LLM智能字幕分割")
    app.setApplicationVersion("1.0.0")
    
    # 设置图标
    icon_path = ROOT_DIR / "videotrans" / "styles" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 初始化子窗口字典
    config.child_forms = {}
    
    # 打开LLM分割窗口
    from videotrans.winform import fn_llm_split
    
    print("正在启动LLM智能字幕分割窗口...")
    fn_llm_split.openwin()
    
    print("✅ 窗口已打开")
    print()
    print("使用说明：")
    print("1. 勾选'启用 LLM 智能断句优化'")
    print("2. 选择LLM提供商（推荐：SiliconFlow）")
    print("   - SiliconFlow 会自动填充 URL 和推荐模型！")
    print("3. 输入API Key")
    print("4. 点击'测试 LLM 连接'验证配置")
    print("5. 选择视频文件")
    print("6. 可选：勾选'使用现有字幕'并选择.srt文件")
    print("7. 点击'开始生成智能字幕'")
    print()
    print("💡 提示：")
    print("   - SiliconFlow: https://siliconflow.cn/ (国内推荐，自动配置)")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - 勾选LLM后，最大时间/词数会自动隐藏（LLM自动优化）")
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

