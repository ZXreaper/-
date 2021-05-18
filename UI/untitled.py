#-*- coding = utf-8 -*-
#@Time : 2021/5/11 15:39
#@Author : ZXREAPER zhangxu
#@File : untitled.py
#@Software : PyCharm

#QTableView组件的使用
from PyQt5.QtWidgets import QTableView, QHeaderView, QFormLayout,   QVBoxLayout,QWidget,QApplication ,QHBoxLayout, QPushButton,QMainWindow,QGridLayout,QLabel
import sys
from PyQt5.QtCore import  *
from PyQt5.QtGui import  QStandardItemModel,QStandardItem

class WindowClass(QWidget):
    #如果集成QMainWindow 则self.setLayout(self.layout) 替换成
    """
        widget=QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
    """
    #即可， 注意集成QWidget和集成QMainWindow时候区别

    def __init__(self,parent=None):
        super(WindowClass, self).__init__(parent)
        self.layout=QVBoxLayout()
        self.model=QStandardItemModel(4,4)#存储任意结构数据
        self.model.setHorizontalHeaderLabels(['序号','姓名','年龄','地址'])
        for row in range(4):
            for column in range(4):
                i=QStandardItem("row %s,column %s"%(row,column))
                self.model.setItem(row,column,i)
        self.tableView=QTableView()
        self.tableView.setModel(self.model)
        self.layout.addWidget(self.tableView)

        #继承QMainWidow使用下面三行代码
        # widget=QWidget()
        # widget.setLayout(self.layout)
        # self.setCentralWidget(widget)

        #继承QWidget则使用下面这样代码
        self.setLayout(self.layout)

        #设置表格充满这个布局QHeaderView
        #self.tableView.horizontalHeader().setStretchLastSection(True)#最后一列决定充满剩下的界面
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)#所有列自动拉伸，充满界面


if __name__=="__main__":
    app=QApplication(sys.argv)
    win=WindowClass()
    win.show()
    sys.exit(app.exec_())