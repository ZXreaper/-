#-*- coding = utf-8 -*-
#@Time : 2021/5/23 22:09
#@Author : ZXREAPER zhangxu
#@File : logic_no_savepath.py
#@Software : PyCharm

from PyQt5.QtWidgets import *
from UI.no_savepath_reminder import Ui_Form


class LogicNoSavepathForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(LogicNoSavepathForm, self).__init__(parent)
        self.setupUi(self)