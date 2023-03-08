from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from sys import argv, exit
from os import path
import time
import json
import sys
import sqlite3


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(16)  # 括号里的数字可以设置成自己想要的字体大小

        self.w = AnotherWindow()

        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle('MyTime')
        MainWindow.resize(600, 600)

        self.on = False  # 开关标志
        self.start_time = 0  # 前一次计时时间

        localtime = time.localtime(time.time())  # 本地时间
        self.date = '%s-%s-%s' % (localtime.tm_year,
                                  localtime.tm_mon, localtime.tm_mday)  # 转换成日期

        # 读取记录
        self.con = sqlite3.connect("data/time_logging.sqlite")
        self.con.execute(
            "create table if not exists logging(date, start_time, end_time, duration, class, target, task)")

        cur = self.con.cursor()
        self.todayLogging = {
            '总计时': 0, '技术任务': 0, '文献阅读': 0, '日常任务': 0, '服务任务': 0}
        for row in cur.execute(f"SELECT date, duration, class from logging\
            where date = '{self.date}'"):
            self.todayLogging[row[2]] += row[1]
        self.todayLogging['总计时'] = sum(self.todayLogging.values())
        target_dict = set()
        for row in cur.execute(f"SELECT target from logging"):
            target_dict.add(row[0])
        task_dict = set()
        for row in cur.execute(f"SELECT task from logging"):
            task_dict.add(row[0])
        cur.close()

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(50, 50, 500, 500))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label_0 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_0.setObjectName("label_0")
        self.label_0.setFont(font)
        self.verticalLayout.addWidget(self.label_0)

        self.label_1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_1.setObjectName("label")
        self.verticalLayout.addWidget(self.label_1)

        class_items = [
            "技术任务",
            "文献阅读",
            "日常任务",
            "服务任务"
        ]
        self.classBox = QtWidgets.QComboBox()
        self.classBox.addItems(class_items)
        self.classBox.setCurrentIndex(0)
        self.classBox.setFont(font)
        self.verticalLayout.addWidget(self.classBox)

        # https://blog.csdn.net/u012828517/article/details/105158680
        self.targetBox = QtWidgets.QComboBox()
        self.targetBox.addItems(list(target_dict))
        # self.targetBox.setCurrentIndex(0)
        self.targetBox.setEditable(True)
        self.targetBox.lineEdit().setPlaceholderText("Target")
        self.targetBox.setFont(font)
        self.verticalLayout.addWidget(self.targetBox)

        completer = QtWidgets.QCompleter(list(task_dict))
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.taskLine = QtWidgets.QLineEdit()
        self.taskLine.setCompleter(completer)
        self.taskLine.setPlaceholderText("Task")
        self.taskLine.setFont(font)
        self.verticalLayout.addWidget(self.taskLine)

        self.button1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button1.setObjectName("pushButton")
        self.button1.setText('开始')
        self.button1.clicked.connect(self.onButtonClick)
        self.button1.setFont(font)
        self.verticalLayout.addWidget(self.button1)
        # self.button1.clicked.connect(self.show_new_window)

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
        totalmin = self.todayLogging["总计时"]//60
        totalhour = totalmin//60
        workmin = self.todayLogging['技术任务']//60
        workhour = workmin//60
        studymin = self.todayLogging['文献阅读']//60
        studyhour = studymin//60
        moyumin = self.todayLogging['日常任务']//60
        moyuhour = moyumin//60
        playmin = self.todayLogging['服务任务']//60
        playhour = playmin//60
        self.label_0.setText("今天是%s\n\n技术任务:\t%dh %dmin %ds\n文献阅读:\t%dh %dmin %ds\n日常任务:\t%dh %dmin %ds\n服务任务:\t%dh %dmin %ds\n总计时:\t\t%dh %dmin %ds\n"
                             % (
                                 self.date,
                                 workhour, workmin % 60, self.todayLogging['技术任务'] % 60,
                                 studyhour, studymin % 60, self.todayLogging['文献阅读'] % 60,
                                 moyuhour, moyumin % 60, self.todayLogging['日常任务'] % 60,
                                 playhour, playmin % 60, self.todayLogging['服务任务'] % 60,
                                 totalhour, totalmin % 60, self.todayLogging["总计时"] % 60,
                             ))

    def onButtonClick(self):
        if not self.on:
            # Start the counting
            self.button1.setText('结束')
            self.w.show()
            self.start_time = time.time()
            self.label_1.setText('正在计时')
            self.on = True
        else:
            # Stop the counting and take records
            self.button1.setText('开始')
            self.w.hide()
            self.label_1.setText('暂停计时')
            self.end_time = time.time()
            self.on = False

            self.todayLogging["总计时"] += self.end_time-self.start_time
            self.todayLogging[self.classBox.currentText()
                              ] += self.end_time-self.start_time
            self.display()

            cur = self.con.cursor()
            cur.execute(
                "insert into logging(date, start_time, end_time, duration, class, target, task) \
                values (?,?,?,?,?,?,?)",
                (
                    self.date,
                    self.start_time,
                    self.end_time,
                    self.end_time-self.start_time,
                    self.classBox.currentText(),
                    self.targetBox.currentText(),
                    self.taskLine.text()))
            self.con.commit()
            cur.close()
            self.con.close()
            self.con = sqlite3.connect("data/time_logging.sqlite")

    def closeEvent(self, event):
        self.con.close()

        for widget in QtWidgets.QApplication.instance().allWidgets():
            if isinstance(widget, QtWidgets.QWidget) and widget != self:
                widget.close()
        event.accept()
        sys.exit(0)


class AnotherWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    # https://zhuanlan.zhihu.com/p/463920533

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.FramelessWindowHint)

        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(18)  # 括号里的数字可以设置成自己想要的字体大小
        self.label.setFont(font)

    # https://blog.csdn.net/FanMLei/article/details/79433229
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos()-self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(Qt.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos()-self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(Qt.QCursor(QtCore.Qt.ArrowCursor))

    def closeEvent(self, event):
        sys.exit(0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    exit(app.exec_())
