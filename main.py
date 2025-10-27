#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyVideoTrans 工具集主菜单 - 主启动脚本

使用方法：
    uv run python main.py
    或
    python main.py
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
    
    # 设置环境变量
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
    
    # 初始化配置
    from videotrans.configure import config
    config.ROOT_DIR = str(ROOT_DIR)
    config.HOME_DIR = str(Path.home() / "Videos" / "pyvideotrans")
    
    # 确保输出目录存在
    Path(config.HOME_DIR).mkdir(parents=True, exist_ok=True)
    
    # 设置默认语言
    config.defaulelang = 'zh'  # 或 'en'
    
    print("=" * 60)
    print("🎬 PyVideoTrans 工具集")
    print("=" * 60)
    print(f"工作目录: {config.HOME_DIR}")
    print("=" * 60)
    print()
    
    # 创建 Qt 应用
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    
    # Windows 打包需要
    import multiprocessing
    multiprocessing.freeze_support()
    
    # 设置 HighDpi
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except AttributeError:
        pass
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 导入样式资源
    try:
        import videotrans.ui.dark.darkstyle_rc
    except:
        pass
    
    try:
        with open('./videotrans/styles/style.qss', 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"加载样式失败: {e}")
    
    # 设置全局异常处理
    from videotrans.configure._guiexcept import global_exception_hook
    sys.excepthook = global_exception_hook
    
    # 创建主菜单窗口
    from videotrans.component import MainMenuForm
    main_menu = MainMenuForm()
    
    # 连接按钮事件
    def open_llm_split():
        """打开 LLM 智能分割字幕窗口"""
        from videotrans.winform import fn_llm_split
        fn_llm_split.openwin()
    
    def open_ai_translate():
        """打开 AI 字幕翻译窗口"""
        # TODO: 实现 AI 字幕翻译功能
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            main_menu,
            "提示" if config.defaulelang == 'zh' else "Notice",
            "AI 字幕翻译功能即将推出！" if config.defaulelang == 'zh' else "AI Subtitle Translation coming soon!"
        )
    
    def open_render_subtitle():
        """打开视频渲染字幕窗口"""
        from videotrans.winform import fn_vas
        fn_vas.openwin()
    
    # 连接信号
    main_menu.btn_llm_split.clicked.connect(open_llm_split)
    main_menu.btn_ai_translate.clicked.connect(open_ai_translate)
    main_menu.btn_render_subtitle.clicked.connect(open_render_subtitle)
    
    # 设置窗口图标
    try:
        icon_path = f"{config.ROOT_DIR}/videotrans/styles/icon.ico"
        main_menu.setWindowIcon(QIcon(icon_path))
    except:
        pass
    
    # 居中显示窗口
    from PySide6.QtGui import QGuiApplication
    screen = QGuiApplication.primaryScreen()
    if screen:
        screen_geometry = screen.availableGeometry()
        window_geometry = main_menu.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        main_menu.move(window_geometry.topLeft())
    
    # 显示窗口
    main_menu.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

