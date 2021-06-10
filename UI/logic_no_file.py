#-*- coding = utf-8 -*-
#@Time : 2021/5/23 21:50
#@Author : ZXREAPER zhangxu
#@File : logic_no_file.py
#@Software : PyCharm

from UI.no_file_reminder import Ui_Form
from PyQt5.QtWidgets import *


class LogicNoFileForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(LogicNoFileForm, self).__init__(parent)
        self.setupUi(self)