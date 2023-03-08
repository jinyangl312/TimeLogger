from PyQt5 import QtCore, QtWidgets
from sys import argv, exit
from os import path
import time
import json


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle('MyTime')
        MainWindow.resize(800, 600)

        self.on = False  # 开关标志
        self.t1 = 0  # 前一次计时时间

        localtime = time.localtime(time.time())  # 本地时间
        self.date = '%s-%s-%s' % (localtime.tm_year,
                                  localtime.tm_mon, localtime.tm_mday)  # 转换成日期

        # 读取记录
        self.history = {}
        self.read_history()
        if self.date not in self.history.keys():
            self.history[self.date] = {
                '总计时': 0, '文献阅读': 0, '技术任务': 0, '日常任务': 0, '服务任务': 0}

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(190, 150, 421, 241))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label_0 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_0.setObjectName("label_0")
        self.verticalLayout.addWidget(self.label_0)

        self.label_1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_1.setObjectName("label")
        self.verticalLayout.addWidget(self.label_1)

        self.button1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button1.setObjectName("pushButton")
        self.button1.setText('开始')
        self.button1.clicked.connect(self.onButtonClick)
        self.verticalLayout.addWidget(self.button1)

        items = [
            "技术任务",
            "文献阅读",
            "日常任务",
            "服务任务"
        ]
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItems(items)
        self.comboBox.setCurrentIndex(0)
        self.verticalLayout.addWidget(self.comboBox)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.display()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def display(self):
        totalmin = self.history[self.date]["总计时"]//60
        totalhour = totalmin//60
        workmin = self.history[self.date]['技术任务']//60
        workhour = workmin//60
        studymin = self.history[self.date]['文献阅读']//60
        studyhour = studymin//60
        moyumin = self.history[self.date]['日常任务']//60
        moyuhour = moyumin//60
        playmin = self.history[self.date]['服务任务']//60
        playhour = playmin//60
        self.label_0.setText("今天是%s\n\n技术任务:%dh %dmin %ds\n文献阅读:%dh %dmin %ds\n日常任务:%dh %dmin %ds\n服务任务:%dh %dmin %ds\n总计时:%dh %dmin %ds"
                             % (
                                 self.date,
                                 workhour, workmin % 60, self.history[self.date]['技术任务'] % 60,
                                 studyhour, studymin % 60, self.history[self.date]['文献阅读'] % 60,
                                 moyuhour, moyumin % 60, self.history[self.date]['日常任务'] % 60,
                                 playhour, playmin % 60, self.history[self.date]['服务任务'] % 60,
                                 totalhour, totalmin % 60, self.history[self.date]["总计时"] % 60,
                             ))

    def onButtonClick(self):
        if not self.on:
            self.button1.setText('结束')
            self.t1 = time.time()
            self.label_1.setText('开始计时，加油！')
            self.on = True
        else:
            self.button1.setText('开始')
            self.history[self.date]["总计时"] += time.time()-self.t1
            self.history[self.date][self.comboBox.currentText()
                                    ] += time.time()-self.t1
            self.label_1.setText('已停止计时，快来！')
            self.display()
            self.on = False
            with open('data/data.json', 'w') as f:
                json.dump(self.history, f)

    def read_history(self):
        if path.exists('data/data.json'):
            with open('data/data.json', 'r') as f:
                self.history = json.load(f)


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    exit(app.exec_())
