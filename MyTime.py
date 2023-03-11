from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from sys import argv, exit
import time
import sys
import sqlite3


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(16)  # 括号里的数字可以设置成自己想要的字体大小

        self.w = UI_TimeCounter()

        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle('TimeLogger')
        MainWindow.resize(600, 600)

        self.startButtonOn = False  # 开关标志
        self.pauseButtonOn = False
        self.start_time = 0  # 前一次计时时间
        self.pause_duration = 0

        localtime = time.localtime(time.time())  # 本地时间
        self.date = '%s-%s-%s' % (localtime.tm_year,
                                  localtime.tm_mon, localtime.tm_mday)  # 转换成日期

        self.initTodayLogging("data/time_logging.sqlite")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(50, 50, 500, 500))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.dailyPannel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.dailyPannel.setObjectName("dailyPannel")
        self.dailyPannel.setFont(font)
        self.verticalLayout.addWidget(self.dailyPannel)

        self.workHints = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.workHints.setObjectName("workHints")
        self.verticalLayout.addWidget(self.workHints)

        class_items = [
            "技术工作",
            "文献阅读",
            "日常工作",
            "服务工作"
        ]
        self.classBox = QtWidgets.QComboBox()
        self.classBox.addItems(class_items)
        self.classBox.setCurrentIndex(0)
        self.classBox.setFont(font)
        self.verticalLayout.addWidget(self.classBox)

        # https://blog.csdn.net/u012828517/article/details/105158680
        self.targetBox = QtWidgets.QComboBox()
        self.targetBox.addItems(list(self.target_dict))
        # self.targetBox.setCurrentIndex(0)
        self.targetBox.setEditable(True)
        self.targetBox.lineEdit().setPlaceholderText("Target")
        self.targetBox.setFont(font)
        self.verticalLayout.addWidget(self.targetBox)

        completer = QtWidgets.QCompleter(list(self.task_dict))
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.taskLine = QtWidgets.QLineEdit()
        self.taskLine.setCompleter(completer)
        self.taskLine.setPlaceholderText("Task")
        self.taskLine.setFont(font)
        self.verticalLayout.addWidget(self.taskLine)

        self.button1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button1.setObjectName("startEndButton")
        self.button1.setText('开始工作')
        self.button1.clicked.connect(self.onStartButtonClick)
        self.button1.setFont(font)
        self.verticalLayout.addWidget(self.button1)

        self.button2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button2.setObjectName("pauseButton")
        self.button2.setText('暂停工作')
        self.button2.clicked.connect(self.onPauseButtonClick)
        self.button2.setFont(font)
        self.verticalLayout.addWidget(self.button2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.displayTodayLogging()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def onStartButtonClick(self):
        if not self.startButtonOn:
            # Start the counting
            self.button1.setText('结束工作')
            self.w.show()
            self.w.startWork()
            self.start_time = time.time()
            self.start_time_l = time.localtime()
            self.workHints.setText('正在计时')
            self.startButtonOn = True
        else:
            # Stop the counting and take records
            if self.pauseButtonOn:
                self.onPauseButtonClick()

            self.button1.setText('开始工作')
            self.w.show()
            # self.w.hide()
            self.w.startRest()
            self.workHints.setText('')
            self.end_time = time.time()
            self.end_time_l = time.localtime()
            self.startButtonOn = False

            self.todayLogging["总计时"] += (self.end_time -
                                         self.start_time - self.pause_duration)//60
            self.todayLogging[self.classBox.currentText()
                              ] += (self.end_time-self.start_time - self.pause_duration)//60
            self.writeTimeLogging("data/time_logging.sqlite")
            self.displayTodayLogging()

            self.pause_duration = 0

    def onPauseButtonClick(self):
        if not self.pauseButtonOn:
            # Start pause
            self.button2.setText('恢复工作')
            self.w.startPause()
            self.start_pause = time.time()
            self.workHints.setText('暂停计时')
            self.pauseButtonOn = True
        else:
            # Stop pause and take records
            self.button2.setText('暂停工作')
            self.w.resumeWork()
            self.workHints.setText('')
            self.end_pause = time.time()
            self.pause_duration += self.end_pause - self.start_pause
            self.pauseButtonOn = False

    def displayTodayLogging(self):
        totalmin = self.todayLogging["总计时"]
        totalhour = totalmin//60
        workmin = self.todayLogging['技术工作']
        workhour = workmin//60
        studymin = self.todayLogging['文献阅读']
        studyhour = studymin//60
        moyumin = self.todayLogging['日常工作']
        moyuhour = moyumin//60
        playmin = self.todayLogging['服务工作']
        playhour = playmin//60
        self.dailyPannel.setText("""
今天是%s\n\n\
技术工作:\t%dh %2dmin\t%.1f
文献阅读:\t%dh %2dmin\t%.1f
日常工作:\t%dh %2dmin\t%.1f
服务工作:\t%dh %2dmin\t%.1f
总计时:\t\t%dh %2dmin\t%.1f
"""
                                 % (
                                     self.date,
                                     workhour, workmin % 60, workmin/25,
                                     studyhour, studymin % 60, studymin/25,
                                     moyuhour, moyumin % 60, moyumin/25,
                                     playhour, playmin % 60, playmin/25,
                                     totalhour, totalmin % 60, totalmin/25,
                                 ))

    def initTodayLogging(self, db_path):
        connection = sqlite3.connect(db_path)
        connection.execute(
            "create table if not exists logging(date, start_time, end_time, duration, class, target, task)")

        cursor = connection.cursor()
        self.todayLogging = {
            '总计时': 0, '技术工作': 0, '文献阅读': 0, '日常工作': 0, '服务工作': 0}
        for row in cursor.execute(f"SELECT date, duration, class from logging\
            where date = '{self.date}'"):
            self.todayLogging[row[2]] += row[1]
        self.todayLogging['总计时'] = sum(self.todayLogging.values())
        self.target_dict = set()
        for row in cursor.execute(f"SELECT target from logging"):
            self.target_dict.add(row[0])
        self.task_dict = set()
        for row in cursor.execute(f"SELECT task from logging"):
            self.task_dict.add(row[0])
        cursor.close()
        connection.close()

    def writeTimeLogging(self, db_path):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            "insert into logging(date, start_time, end_time, duration, class, target, task) \
            values (?,?,?,?,?,?,?)",
            (
                self.date,
                '%d:%02d' % (self.start_time_l[3], self.start_time_l[4]),
                '%d:%02d' % (self.end_time_l[3], self.end_time_l[4]),
                (self.end_time-self.start_time-self.pause_duration)//60,
                self.classBox.currentText(),
                self.targetBox.currentText(),
                self.taskLine.text()))
        connection.commit()
        cursor.close()
        connection.close()

    def closeEvent(self, event):
        for widget in QtWidgets.QApplication.instance().allWidgets():
            if isinstance(widget, QtWidgets.QWidget) and widget != self:
                widget.close()
        event.accept()
        sys.exit(0)


class UI_TimeCounter(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    # https://zhuanlan.zhihu.com/p/463920533

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.timeDisplayLabel = QtWidgets.QLabel()
        layout.addWidget(self.timeDisplayLabel)
        self.setLayout(layout)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.FramelessWindowHint)
        self.start_time = time.time()
        self.pause_duration = 0
        self.onWork = False
        self.onPause = False
        self.statusShowTime()

    def statusShowTime(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.showCurrentTime(
            self.timeDisplayLabel))  # 这个通过调用槽函数来刷新时间
        self.timer.start(1000)  # 每隔一秒刷新一次，这里设置为1000ms  即1s

    # https://blog.csdn.net/HG0724/article/details/116308195
    def showCurrentTime(self, timeLabel):
        cur_time = time.time()
        if self.onWork or not self.onPause:
            duration = int(cur_time - self.start_time - self.pause_duration)
        else:
            duration = int(cur_time - self.start_pause)
        # 设置系统时间的显示格式
        timeDisplay = '{:2d}:{:02d}:{:02d}'.format(
            duration//3600, duration // 60 % 60, duration % 60)
        # print(timeDisplay)
        timeLabel.setText(timeDisplay)

        if self.onWork and int(cur_time - self.last_start_time + 1) % (25 * 60) == 0:
            self.showWork25min()

    def startWork(self):
        self.onWork = True
        self.onPause = False
        self.start_time = time.time()
        self.last_start_time = self.start_time
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(18)  # 括号里的数字可以设置成自己想要的字体大小
        self.timeDisplayLabel.setFont(font)
        self.timeDisplayLabel.setStyleSheet("color:red")
        self.showCurrentTime(self.timeDisplayLabel)

    def startRest(self):
        self.onWork = False
        self.onPause = False
        self.start_time = time.time()
        self.pause_duration = 0
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(18)  # 括号里的数字可以设置成自己想要的字体大小
        self.timeDisplayLabel.setFont(font)
        self.timeDisplayLabel.setStyleSheet("color:green")
        self.showCurrentTime(self.timeDisplayLabel)

    def resumeWork(self):
        self.onWork = True
        self.onPause = False
        self.pause_duration = time.time() - self.start_pause
        self.last_start_time = time.time()
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(18)  # 括号里的数字可以设置成自己想要的字体大小
        self.timeDisplayLabel.setFont(font)
        self.timeDisplayLabel.setStyleSheet("color:red")
        self.showCurrentTime(self.timeDisplayLabel)

    def startPause(self):
        self.onWork = False
        self.onPause = True
        self.start_pause = time.time()
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(18)  # 括号里的数字可以设置成自己想要的字体大小
        self.timeDisplayLabel.setFont(font)
        self.timeDisplayLabel.setStyleSheet("color:yellow")
        self.showCurrentTime(self.timeDisplayLabel)

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

    def showWork25min(self):
        QtWidgets.QMessageBox.information(
            self, "TimeLogger", "25 minutes reached!")

    def closeEvent(self, event):
        sys.exit(0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    exit(app.exec_())
