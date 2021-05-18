#-*- coding = utf-8 -*-
#@Time : 2021/5/11 17:38
#@Author : ZXREAPER zhangxu
#@File : logicwindow.py
#@Software : PyCharm

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from startwindow import *
from BackendLogic import Solve

class myLogicwindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(myLogicwindow, self).__init__(parent)
        self.setupUi(self)

        # 获取当前程序文件位置
        self.cwd = os.getcwd()

        self.model = QStandardItemModel(0, 0)  # 存储任意结构数据
        self.model.setHorizontalHeaderLabels(['文件名','文件路径'])
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面

        # 设置信号
        self.btn_chooseMutiFile.clicked.connect(self.slot_btn_chooseMutiFile)
        self.btn_chooseOutpufilepath.clicked.connect(self.slot_btn_chooseOutpufilepath)
        self.btn_DataAnalysisTable.clicked.connect(self.slot_btn_DataAnalysisTable)
        self.btn_generateHeatMap.clicked.connect(self.slot_btn_generateHeatMap)

        # 设置所选需要分析的文件列表
        self.files = []

        # 设置分析结果输出的路径
        self.result_save_path = ''

        # 设置sol对象
        self.sol = None

        self.this_processed_table = None

    def slot_btn_chooseMutiFile(self):
        self.files, filetype = QFileDialog.getOpenFileNames(None,
                                    "文件选择",
                                    self.cwd, # 起始路径
                                    "All Files (*);;Excel Files (*.xlsx);;Excel Files (*.xls)")

        if len(self.files) == 0:
            print("\n取消选择")
            return

        print("\n你选择的文件为:")
        for file in self.files:
            print(file)

        # 清空tableview当前显示的内容
        self.tableView.clearSpans()

        for row in range(len(self.files)):
            i = len(self.files[row])-1
            while i >= 0:
                if self.files[row][i] == '/':
                    break
                i -= 1
            cur_file_name = self.files[row][i+1:]
            cur_file_path = self.files[row]
            print(cur_file_name,cur_file_path)
            content = QStandardItem(cur_file_name)
            self.model.setItem(row, 0, content)
            content = QStandardItem(cur_file_path)
            self.model.setItem(row, 1, content)
            self.tableView.setModel(self.model)
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        print("文件筛选器类型: ", filetype)

        # 当重新选择文件时应该重新构建一个Sol对象并且把self.this_processed_table置为None
        self.sol = Solve(filepath=self.files, changci=len(self.files))
        self.this_processed_table = None

    def slot_btn_chooseOutpufilepath(self):
        self.result_save_path = QFileDialog.getExistingDirectory(None,
                                                              "选取保存结果所在文件夹",
                                                              self.cwd)
        print(self.result_save_path)

        self.lineEdit.setText(self.result_save_path)

    def slot_btn_DataAnalysisTable(self):
        if self.this_processed_table is None:
            self.this_processed_table = self.sol.enter_data_process()

        # 为了防止选择以后又在lineedit上进行修改，所以再获取一次lineedit上的内容
        self.result_save_path = self.lineEdit.text()
        print("文件保存路径为 %s"%(self.result_save_path))

        self.sol.enter_generate_table(save_file_path=self.result_save_path, processed_table_list=self.this_processed_table)
        print("表格生成结束！！！")

    def slot_btn_generateHeatMap(self):
        if self.this_processed_table is None:
            self.this_processed_table = self.sol.enter_data_process()

        self.sol.enter_draw(self.this_processed_table)
        print("热力图生成结束！！！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = myLogicwindow()
    myWin.show()
    sys.exit(app.exec_())