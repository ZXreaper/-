#-*- coding = utf-8 -*-
#@Time : 2021/5/11 17:38
#@Author : ZXREAPER zhangxu
#@File : logicwindow.py
#@Software : PyCharm

import sys
import os
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap
from UI.startwindow import Ui_MainWindow
from BackendLogic import Solve
from UI import logic_no_file
from UI import logic_no_savepath

class myLogicwindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(myLogicwindow, self).__init__(parent)
        self.setupUi(self)

        # 获取当前程序文件位置
        self.cwd = os.getcwd()

        # tableview
        self.model = QStandardItemModel(0, 0)  # 存储任意结构数据
        self.model.setHorizontalHeaderLabels(['文件名','文件路径'])
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面

        # tableview2
        self.model2 = QStandardItemModel(0, 0)  # 存储任意结构数据
        self.model2.setHorizontalHeaderLabels(['文件名', '文件路径'])
        self.tableView_2.setModel(self.model2)
        self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面

        # 设置信号
        self.btn_chooseMutiFile.clicked.connect(self.slot_btn_chooseMutiFile)
        self.btn_chooseOutpufilepath.clicked.connect(self.slot_btn_chooseOutpufilepath)
        self.btn_DataAnalysisTable.clicked.connect(self.slot_btn_DataAnalysisTable)
        self.btn_generateHeatMap.clicked.connect(self.slot_btn_generateSpeedHeatMap)
        self.btn_choosePreviousperchase.clicked.connect(self.slot_btn_choosePreviousperchase)
        self.comboBox.activated.connect(self.slot_lineEdit_2)
        self.comboBox_2.activated.connect(self.slot_setHeatmapTheme)
        self.btn_generateFrequenceHeatmap.clicked.connect(self.slot_btn_generateFrequenceHeatMap)
        self.btn_generateEnsembleHeatmap.clicked.connect(self.slot_btn_generateEnsembleHeatMap)

        # 设置所选需要分析的散客文件列表
        self.files = []

        # 设置所选开票前预留文件列表
        self.previous_files = []

        # 设置分析结果输出的路径
        self.result_save_path = ''

        # 设置sol对象
        self.sol = None

        self.this_processed_table = None

        # 设置没有选择分析文件的提示弹窗
        self.no_file_reminder_win = None

        # 设置没有保存路径的提示弹窗
        self.no_savepath_reminder_win = None

        # 设置显示处理进度的提示弹窗
        self.generate_frequcenheatmap_win = None

        # 设置当前选择的场次的名称
        self.name_of_theater = "《巴黎圣母院》"

        # 设置当前热力图显示主题
        self.theme = "rainbow"

    def slot_lineEdit_2(self):
        self.this_processed_table = None        # 当改变了场次，应该将处理表置为None
        self.name_of_theater = self.comboBox.currentText()
        self.lineEdit_2.setText(self.name_of_theater)
        print(self.name_of_theater)

    def slot_setHeatmapTheme(self):
        self.this_processed_table = None        # 当改变了热力图主题，应该将处理表置为None
        self.theme = self.comboBox_2.currentText()
        print(self.theme)

    def slot_btn_generateFrequenceHeatMap(self):
        # 弹窗提醒未选择要分析的文件
        if len(self.files) == 0:
            self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
            self.no_file_reminder_win.show()
            return

        # # 弹窗提醒未选择预留表文件
        # if len(self.previous_files) == 0:
        #     self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
        #     self.no_file_reminder_win.show()
        #     return

        # 弹窗提醒未设置文件保存路径
        if self.result_save_path == '':
            self.no_savepath_reminder_win = logic_no_savepath.LogicNoSavepathForm()
            self.no_savepath_reminder_win.show()
            return

        # if self.this_processed_table is None:
        #     self.sol = Solve(filepath=self.files, previous_filepath=self.previous_files, changci=len(self.files),
        #                      changciname=self.name_of_theater, heatmaptheme=self.theme)
        #     self.this_processed_table = self.sol.enter_data_process()
        #
        # self.sol.enter_draw_frequence_heatmap(save_file_path=self.result_save_path, table=self.this_processed_table)
        # print("购票频次热力图生成结束！！！")
            # 开一个线程
        self.FrequenceHeatmap_thread = WorkThread(type=1, filepath=self.files,
                                                    previous_filepath=self.previous_files,
                                                    changci=len(self.files),
                                                    changciname=self.name_of_theater,
                                                    heatmaptheme=self.theme,
                                                    this_processed_table=self.this_processed_table,
                                                    result_save_path=self.result_save_path)
        self.FrequenceHeatmap_thread.progressbarValue.connect(self.setProgressbarValue)
        self.FrequenceHeatmap_thread.start()

    def slot_btn_choosePreviousperchase(self):
        self.previous_files, filetype = QFileDialog.getOpenFileNames(None,
                                                            "文件选择",
                                                            self.cwd,  # 起始路径
                                                            "All Files (*);;Excel Files (*.xlsx);;Excel Files (*.xls)")

        if len(self.previous_files) == 0:
            self.model2.removeRows(0, self.model2.rowCount())
            print("\n取消选择")
            return

        print("\n你选择的预留表文件为:")
        for file in self.previous_files:
            print(file)

        # 清空tableview当前显示的内容
        # self.tableView.clearSpans()
        self.model2.removeRows(0, self.model2.rowCount())

        for row in range(len(self.previous_files)):
            i = len(self.previous_files[row])-1
            while i >= 0:
                if self.previous_files[row][i] == '/':
                    break
                i -= 1
            cur_file_name = self.previous_files[row][i+1:]
            cur_file_path = self.previous_files[row]
            print(cur_file_name,cur_file_path)
            content = QStandardItem(cur_file_name)
            self.model2.setItem(row, 0, content)
            content = QStandardItem(cur_file_path)
            self.model2.setItem(row, 1, content)
            self.tableView_2.setModel(self.model2)
            self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        print("文件筛选器类型: ", filetype)

    def slot_btn_chooseMutiFile(self):
        self.files, filetype = QFileDialog.getOpenFileNames(None,
                                                            "文件选择",
                                                            self.cwd, # 起始路径
                                                            "All Files (*);;Excel Files (*.xlsx);;Excel Files (*.xls)")

        if len(self.files) == 0:
            self.model.removeRows(0, self.model.rowCount())
            print("\n取消选择")
            return

        print("\n你选择的文件为:")
        for file in self.files:
            print(file)

        # 清空tableview当前显示的内容
        # self.tableView.clearSpans()
        self.model.removeRows(0, self.model.rowCount())

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

        # 当重新选择文件时应该把self.this_processed_table置为None
        # self.sol = Solve(filepath=self.files, changci=len(self.files))
        self.this_processed_table = None

    def slot_btn_chooseOutpufilepath(self):
        self.result_save_path = QFileDialog.getExistingDirectory(None,
                                                              "选取保存结果所在文件夹",
                                                              self.cwd)
        print(self.result_save_path)

        self.lineEdit.setText(self.result_save_path)

    def slot_btn_DataAnalysisTable(self):

        # 弹窗提醒未选择要分析的文件
        if len(self.files) == 0:
            self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
            self.no_file_reminder_win.show()
            return

        # # 弹窗提醒未选择预留表文件
        # if len(self.previous_files) == 0:
        #     self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
        #     self.no_file_reminder_win.show()
        #     return

        #弹窗提醒未设置文件保存路径
        if self.result_save_path == '':
            self.no_savepath_reminder_win = logic_no_savepath.LogicNoSavepathForm()
            self.no_savepath_reminder_win.show()
            return

        # 为了防止选择以后又在lineedit上进行修改，所以再获取一次lineedit上的内容
        self.result_save_path = self.lineEdit.text()
        print("文件保存路径为 %s" % (self.result_save_path))

        # if self.this_processed_table is None:
        #     self.sol = Solve(filepath=self.files, previous_filepath=self.previous_files ,changci=len(self.files),
        #                      changciname=self.name_of_theater, heatmaptheme=self.theme)
        #     self.this_processed_table = self.sol.enter_data_process()
        #
        # self.sol.enter_generate_table(save_file_path=self.result_save_path, processed_table_list=self.this_processed_table)
        # print("表格生成结束！！！")
        # # 弹窗：表格生成成功
        # 开一个线程
        self.DataAnalysisTable_thread = WorkThread(type=2, filepath=self.files,
                                                     previous_filepath=self.previous_files,
                                                     changci=len(self.files),
                                                     changciname=self.name_of_theater,
                                                     heatmaptheme=self.theme,
                                                     this_processed_table=self.this_processed_table,
                                                     result_save_path=self.result_save_path)
        self.DataAnalysisTable_thread.progressbarValue.connect(self.setProgressbarValue)
        self.DataAnalysisTable_thread.start()

    def slot_btn_generateSpeedHeatMap(self):
        # 弹窗提醒未选择要分析的文件
        if len(self.files) == 0:
            self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
            self.no_file_reminder_win.show()
            return

        # # 弹窗提醒未选择预留表文件
        # if len(self.previous_files) == 0:
        #     self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
        #     self.no_file_reminder_win.show()
        #     return

        # 弹窗提醒未设置文件保存路径
        if self.result_save_path == '':
            self.no_savepath_reminder_win = logic_no_savepath.LogicNoSavepathForm()
            self.no_savepath_reminder_win.show()
            return

        # if self.this_processed_table is None:
        #     self.sol = Solve(filepath=self.files, previous_filepath=self.previous_files, changci=len(self.files),
        #                      changciname=self.name_of_theater, heatmaptheme=self.theme)
        #     self.this_processed_table = self.sol.enter_data_process()
        #
        # self.sol.enter_draw_speed_heatmap(save_file_path=self.result_save_path, table=self.this_processed_table)
        # print("购票速度热力图生成结束！！！")

        # 开一个线程
        self.draw_speed_heatmap_thread = WorkThread(type = 3,filepath=self.files,
                                                     previous_filepath=self.previous_files, changci=len(self.files),
                                                     changciname=self.name_of_theater, heatmaptheme=self.theme,
                                                     this_processed_table = self.this_processed_table,
                                                     result_save_path = self.result_save_path)
        self.draw_speed_heatmap_thread.progressbarValue.connect(self.setProgressbarValue)
        self.draw_speed_heatmap_thread.start()

    def slot_btn_generateEnsembleHeatMap(self):
        # 弹窗提醒未选择要分析的文件
        if len(self.files) == 0:
            self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
            self.no_file_reminder_win.show()
            return

        # # 弹窗提醒未选择预留表文件
        # if len(self.previous_files) == 0:
        #     self.no_file_reminder_win = logic_no_file.LogicNoFileForm()
        #     self.no_file_reminder_win.show()
        #     return

        # 弹窗提醒未设置文件保存路径
        if self.result_save_path == '':
            self.no_savepath_reminder_win = logic_no_savepath.LogicNoSavepathForm()
            self.no_savepath_reminder_win.show()
            return

        # 开一个线程
        self.draw_ensemble_heatmap_thread = WorkThread(type=4, filepath=self.files,
                                                    previous_filepath=self.previous_files, changci=len(self.files),
                                                    changciname=self.name_of_theater, heatmaptheme=self.theme,
                                                    this_processed_table=self.this_processed_table,
                                                    result_save_path=self.result_save_path)
        self.draw_ensemble_heatmap_thread.progressbarValue.connect(self.setProgressbarValue)
        self.draw_ensemble_heatmap_thread.start()

    def setProgressbarValue(self, v):
        if v == 5:
            self.label_process.setText('正在处理，请稍后……')
        if v == 100:
            self.progressBar.setValue(v)
            self.label_process.setText('已完成!')
            return
        self.progressBar.setValue(v)


    # 重写closeEvent()函数
    def closeEvent(self, event):
        reply = QMessageBox.question(self,
                                     '确认退出',
                                     "是否要退出程序？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class WorkThread(QThread):
    progressbarValue = pyqtSignal(int)

    def __init__(self,type,filepath,previous_filepath,changci,changciname,heatmaptheme,this_processed_table,result_save_path,parent = None):
        super(WorkThread, self).__init__(parent)
        self.type = type
        self.filepath = filepath
        self.previous_filepath = previous_filepath
        self.changci = changci
        self.changciname = changciname
        self.heatmaptheme = heatmaptheme
        self.this_processed_table = this_processed_table
        self.result_save_path = result_save_path

    def run(self):

        a = Solve(filepath=self.filepath, previous_filepath=self.previous_filepath, changci=self.changci,changciname=self.changciname, heatmaptheme=self.heatmaptheme,WorkThread=self)
        self.progressbarValue.emit(5)
        self.this_processed_table = a.enter_data_process()
        self.progressbarValue.emit(35)
        if self.type == 1:
            a.enter_draw_frequence_heatmap(save_file_path=self.result_save_path, table=self.this_processed_table)
            print("购票频次热力图生成结束！！！")
        elif self.type == 2:
            a.enter_generate_table(save_file_path=self.result_save_path, processed_table_list=self.this_processed_table)
            print("分析表格生成结束！！！")
        elif self.type == 3:
            a.enter_draw_speed_heatmap(save_file_path=self.result_save_path, table=self.this_processed_table)
            print("购票速度热力图生成结束！！！")
        else:
            a.enter_draw_ensemble_heatmap(save_file_path=self.result_save_path, table=self.this_processed_table)
            print("整体综合热力图生成结束！！！")
        self.progressbarValue.emit(100)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap(":/icon/picture.png"))
    splash.showMessage("loading, please wait!")
    splash.show()
    MainWindow = QMainWindow()  # 创建主窗口
    myWin = myLogicwindow()
    sleep(2)
    myWin.show()
    splash.finish(myWin)
    sys.exit(app.exec_())