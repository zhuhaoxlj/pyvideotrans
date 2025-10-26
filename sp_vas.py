"""
视频、音频、字幕三合并 - 独立启动脚本
直接启动视频音频字幕合并窗口，无需加载完整主程序
"""

import sys
import os

# 设置环境变量
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

def main():
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
    import videotrans.ui.dark.darkstyle_rc
    try:
        with open('./videotrans/styles/style.qss', 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"加载样式失败: {e}")
    
    # 初始化配置
    from videotrans.configure import config
    
    # 设置全局异常处理
    from videotrans.configure._guiexcept import global_exception_hook, exception_handler
    sys.excepthook = global_exception_hook
    
    def show_global_error_dialog(tb_str):
        from videotrans.util.tools import show_error
        show_error(tb_str)
    
    exception_handler.show_exception_signal.connect(show_global_error_dialog)
    
    # 直接打开视频音频字幕合并窗口
    from videotrans.winform.fn_vas import openwin
    
    try:
        openwin()
        sys.exit(app.exec())
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

