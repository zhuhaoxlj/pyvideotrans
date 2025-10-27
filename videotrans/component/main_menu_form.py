# 主菜单窗口Form

from PySide6.QtWidgets import QMainWindow
from videotrans.ui.main_menu import Ui_MainMenu


class MainMenuForm(QMainWindow, Ui_MainMenu):
    def __init__(self):
        super(MainMenuForm, self).__init__()
        self.setupUi(self)

