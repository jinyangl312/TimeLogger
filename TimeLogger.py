from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from sys import argv, exit
import re
import time
import sys
import sqlite3
import pandas as pd
import os


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

        if not os.path.exists('data'):
            os.mkdir('data')
        self.initTodayLogging("data/time_logging.sqlite")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(50, 10, 500, 550))
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
            "主线工作",
            "支线工作",
            "文献阅读",
            "日常安排",
            "服务打杂"
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

        self.taskBox = QtWidgets.QComboBox()
        self.taskBox.addItems(list(self.task_dict))
        # self.taskBox.setCurrentIndex(0)
        self.taskBox.setEditable(True)
        self.taskBox.lineEdit().setPlaceholderText("Task")
        self.taskBox.setFont(font)
        self.verticalLayout.addWidget(self.taskBox)

        # completer = QtWidgets.QCompleter(list(self.task_dict))
        # completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # self.taskLine = QtWidgets.QLineEdit()
        # self.taskLine.setCompleter(completer)
        # self.taskLine.setPlaceholderText("Task")
        # self.taskLine.setFont(font)
        # self.verticalLayout.addWidget(self.taskLine)

        self.buttonStart = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.buttonStart.setObjectName("startEndButton")
        self.buttonStart.setText('开始工作')
        self.buttonStart.clicked.connect(self.onStartButtonClick)
        self.buttonStart.setFont(font)

        self.buttonPause = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.buttonPause.setObjectName("pauseButton")
        self.buttonPause.setText('暂停工作')
        self.buttonPause.clicked.connect(self.onPauseButtonClick)
        self.buttonPause.setFont(font)

        self.buttonDailyJournal = QtWidgets.QPushButton(
            self.verticalLayoutWidget)
        self.buttonDailyJournal.setText('日统计')
        self.buttonDailyJournal.clicked.connect(self.onStartDailyJournal)
        self.buttonDailyJournal.setFont(font)

        self.buttonWeeklyJournal = QtWidgets.QPushButton(
            self.verticalLayoutWidget)
        self.buttonWeeklyJournal.setText('阶段统计')
        self.buttonWeeklyJournal.clicked.connect(self.onStartWeeklyJournal)
        self.buttonWeeklyJournal.setFont(font)

        horizontalLayout1 = QtWidgets.QHBoxLayout()
        horizontalLayout1.addWidget(self.buttonStart)
        horizontalLayout1.addWidget(self.buttonPause)
        self.verticalLayout.addLayout(horizontalLayout1)
        horizontalLayout2 = QtWidgets.QHBoxLayout()
        horizontalLayout2.addWidget(self.buttonDailyJournal)
        horizontalLayout2.addWidget(self.buttonWeeklyJournal)
        self.verticalLayout.addLayout(horizontalLayout2)

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
            localtime = time.localtime(time.time())  # 本地时间
            if self.date != '%s-%s-%s' % (localtime.tm_year,
                                          localtime.tm_mon, localtime.tm_mday):
                self.date = '%s-%s-%s' % (localtime.tm_year,
                                          localtime.tm_mon, localtime.tm_mday)  # 转换成日期
            self.initTodayLogging("data/time_logging.sqlite")
            self.displayTodayLogging()

            # Start the counting
            self.buttonStart.setText('结束工作')
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

            self.buttonStart.setText('开始工作')
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
            self.buttonPause.setText('恢复工作')
            self.w.startPause()
            self.start_pause = time.time()
            self.workHints.setText('暂停计时')
            self.pauseButtonOn = True
        else:
            # Stop pause and take records
            self.buttonPause.setText('暂停工作')
            self.w.resumeWork()
            self.workHints.setText('')
            self.end_pause = time.time()
            self.pause_duration += self.end_pause - self.start_pause
            self.pauseButtonOn = False

    def onStartDailyJournal(self):
        self.childDailyJournal = DailyJournal()
        self.childDailyJournal.show()
        self.childDailyJournal.exec_()

    def onStartWeeklyJournal(self):
        self.childWeeklyJournal = WeeklyJournal()
        self.childWeeklyJournal.show()
        self.childWeeklyJournal.exec_()

    def displayTodayLogging(self):
        totalmin = self.todayLogging["总计时"]
        totalhour = totalmin//60
        workmin_1 = self.todayLogging['主线工作']
        workhour_1 = workmin_1//60
        workmin_2 = self.todayLogging['支线工作']
        workhour_2 = workmin_2//60
        workmin_3 = self.todayLogging['文献阅读']
        workhour_3 = workmin_3//60
        workmin_4 = self.todayLogging['日常安排']
        workhour_4 = workmin_4//60
        workmin_5 = self.todayLogging['服务打杂']
        workhour_5 = workmin_5//60

        self.dailyPannel.setText("""
今天是%s\n\n\
主线工作:\t%dh %2dmin\t%.1f
支线工作:\t%dh %2dmin\t%.1f
文献阅读:\t%dh %2dmin\t%.1f
日常安排:\t%dh %2dmin\t%.1f
服务打杂:\t%dh %2dmin\t%.1f
总计时:\t\t%dh %2dmin\t%.1f
"""
                                 % (
                                     self.date,
                                     workhour_1, workmin_1 % 60, workmin_1/25,
                                     workhour_2, workmin_2 % 60, workmin_2/25,
                                     workhour_3, workmin_3 % 60, workmin_3/25,
                                     workhour_4, workmin_4 % 60, workmin_4/25,
                                     workhour_5, workmin_5 % 60, workmin_5/25,
                                     totalhour, totalmin % 60, totalmin/25,
                                 ))

    def initTodayLogging(self, db_path):
        connection = sqlite3.connect(db_path)
        connection.execute(
            "create table if not exists logging(date, start_time, end_time, duration, class, target, task)")

        cursor = connection.cursor()
        self.todayLogging = {
            '总计时': 0, '主线工作': 0, '支线工作': 0, '文献阅读': 0, '日常安排': 0, '服务打杂': 0}
        for row in cursor.execute(f"SELECT date, duration, class from logging\
            where date = '{self.date}'"):
            self.todayLogging[row[2]] += row[1]
        self.todayLogging['总计时'] = sum(self.todayLogging.values())

        localtime = time.localtime(time.time())  # 本地时间
        cur_date = '%s-%s-%s' % (localtime.tm_year,
                                 localtime.tm_mon, localtime.tm_mday)  # 转换成日期

        # Select history target and task from the past 10 days into memory
        self.target_dict = set()
        self.task_dict = set()
        for tmp_date in pd.date_range(end=cur_date, periods=10):
            for row in cursor.execute(f"SELECT target from logging\
                where date = '{tmp_date.year}-{tmp_date.month}-{tmp_date.day}'"):
                self.target_dict.add(row[0])
            for row in cursor.execute(f"SELECT task from logging\
                where date = '{tmp_date.year}-{tmp_date.month}-{tmp_date.day}'"):
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
                self.taskBox.currentText()))
        connection.commit()
        cursor.close()
        connection.close()


class My_QMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

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
        elif int(cur_time - self.last_start_time + 1) % (10 * 60) == 0:
            self.showRest10min()

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
        
    def showRest10min(self):
        QtWidgets.QMessageBox.information(
            self, "TimeLogger", "10 minutes reached!")

    def closeEvent(self, event):
        sys.exit(0)

# https://blog.csdn.net/li_l_il/article/details/103117414


class DailyJournal(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle('DailyJournal')
        self.resize(900, 900)

        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(16)  # 括号里的数字可以设置成自己想要的字体大小

        layout = QtWidgets.QVBoxLayout()
        horizontalLayout = QtWidgets.QHBoxLayout()
        self.hintPannel = QtWidgets.QLabel()
        self.hintPannel.setFont(font)
        self.hintPannel.setText("时间：")
        horizontalLayout.addWidget(self.hintPannel)

        localtime = time.localtime(time.time())  # 本地时间
        date = '%s-%s-%s' % (localtime.tm_year,
                             localtime.tm_mon, localtime.tm_mday)  # 转换成日期

        self.timeLine = QtWidgets.QLineEdit()
        self.timeLine.setText(date)
        self.timeLine.setFont(font)
        horizontalLayout.addWidget(self.timeLine)

        self.buttonStart = QtWidgets.QPushButton()
        self.buttonStart.setText('开始')
        self.buttonStart.clicked.connect(self.onStartButtonClick)
        self.buttonStart.setFont(font)
        horizontalLayout.addWidget(self.buttonStart)
        layout.addLayout(horizontalLayout)

        self.verticalLayoutWidget = QtWidgets.QWidget()
        self.rollWindow = QtWidgets.QScrollArea()
        self.journalPannel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.journalPannel.setFont(font)
        self.rollWindow.setWidget(self.journalPannel)
        layout.addWidget(self.rollWindow)

        self.setLayout(layout)

    def onStartButtonClick(self):
        def target_details(df):
            res = ""
            if len(df) == 0:
                return res
            res += f"\n{df['target'].iloc[0]}\tsum: \t{df['duration'].sum()}\tclock: {'%.1f' % (df['duration'].sum()/25)}\n"
            for _, line in df[['start_time', 'end_time', 'duration', 'target', 'task']].iterrows():
                res += f"{line['start_time']}\t{line['end_time']}\t{line['duration']}\t{line['target']}\t{line['task']}\n"
            return res

        res = ""
        date = self.timeLine.text()
        date = re.search("(\d{4}\-\d{1,2}\-\d{1,2})", date).group()
        date = re.sub("((?<=\d{4}\-)0*)", "", date)
        date = re.sub("((?<=\-)0*(?=\d+$))", "", date)

        con = sqlite3.connect("data/time_logging.sqlite")
        cur = con.cursor()

        lines = [x for x in cur.execute(f"SELECT * from logging\
            where date = '{date}'")]
        cur.close()
        con.close()

        df = pd.DataFrame(lines, columns=[
                          'date', 'start_time', 'end_time', 'duration', 'class', 'target', 'task'])

        for class_label in ('主线工作', '支线工作', '文献阅读', '日常安排', '服务打杂'):
            res += f"{class_label}\t\t{'%.1f' %(df[df['class'] == class_label]['duration'].sum()/25)}\n"
        res += f"总时间\t\t{df['duration'].sum()}\t\t{'%.1f' % (df['duration'].sum()/25)}\n\n"

        if len(df[df['class'] == '主线工作']) > 0:
            for x in df[df['class'] ==
                        '主线工作'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '支线工作']) > 0:
            for x in df[df['class'] ==
                        '支线工作'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '文献阅读']) > 0:
            for x in df[df['class'] ==
                        '文献阅读'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '日常安排']) > 0:
            for x in df[df['class'] ==
                        '日常安排'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '服务打杂']) > 0:
            for x in df[df['class'] ==
                        '服务打杂'].groupby('target').apply(target_details):
                res += x

        self.journalPannel.setText(res)
        self.journalPannel.adjustSize()
        return


class WeeklyJournal(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle('WeeklyJournal')
        self.resize(900, 900)

        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(16)  # 括号里的数字可以设置成自己想要的字体大小

        localtime = time.localtime(time.time())  # 本地时间
        date = '%s-%s-%s' % (localtime.tm_year,
                             localtime.tm_mon, localtime.tm_mday)  # 转换成日期

        layout = QtWidgets.QVBoxLayout()
        horizontalLayout = QtWidgets.QHBoxLayout()
        self.hintPannel1 = QtWidgets.QLabel()
        self.hintPannel1.setFont(font)
        self.hintPannel1.setText("起始：")
        horizontalLayout.addWidget(self.hintPannel1)

        self.timeLine1 = QtWidgets.QLineEdit()
        self.timeLine1.setText(date)
        self.timeLine1.setFont(font)
        horizontalLayout.addWidget(self.timeLine1)

        self.hintPannel2 = QtWidgets.QLabel()
        self.hintPannel2.setFont(font)
        self.hintPannel2.setText("终止：")
        horizontalLayout.addWidget(self.hintPannel2)

        self.timeLine2 = QtWidgets.QLineEdit()
        self.timeLine2.setText(date)
        self.timeLine2.setFont(font)
        horizontalLayout.addWidget(self.timeLine2)

        self.buttonStart = QtWidgets.QPushButton()
        self.buttonStart.setText('开始')
        self.buttonStart.clicked.connect(self.onStartButtonClick)
        self.buttonStart.setFont(font)
        horizontalLayout.addWidget(self.buttonStart)
        layout.addLayout(horizontalLayout)

        self.verticalLayoutWidget = QtWidgets.QWidget()
        self.rollWindow = QtWidgets.QScrollArea()
        self.journalPannel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.journalPannel.setFont(font)
        self.rollWindow.setWidget(self.journalPannel)
        layout.addWidget(self.rollWindow)

        self.setLayout(layout)

    def onStartButtonClick(self):
        def target_details(df):
            res = ""
            if len(df) == 0:
                return res
            res += f"\n{df['target'].iloc[0]}\tsum: \t{df['duration'].sum()}\tclock: {'%.1f' % (df['duration'].sum()/25)}\n"
            for _, line in df[['date', 'start_time', 'end_time', 'duration', 'target', 'task']].iterrows():
                res += f"{line['date']}\t{line['start_time']}\t{line['end_time']}\t{line['duration']}\t{line['target']}\t{line['task']}\n"
            return res

        res = ""
        start_date = self.timeLine1.text()
        end_date = self.timeLine2.text()
        date_range = pd.date_range(start_date, end_date)

        con = sqlite3.connect("data/time_logging.sqlite")
        cur = con.cursor()

        lines = []
        for date in date_range:
            lines.extend([x for x in cur.execute(f"SELECT * from logging\
                where date = '{date.year}-{date.month}-{date.day}'")])

        cur.close()
        con.close()

        df = pd.DataFrame(lines, columns=[
                          'date', 'start_time', 'end_time', 'duration', 'class', 'target', 'task'])

        for class_label in ('主线工作', '支线工作', '文献阅读', '日常安排', '服务打杂'):
            res += f"{class_label}\t\t{'%.1f' %(df[df['class'] == class_label]['duration'].sum()/25)}\n"
        res += f"总时间\t\t{df['duration'].sum()}\t\t{'%.1f' % (df['duration'].sum()/25)}\n\n"

        if len(df[df['class'] == '主线工作']) > 0:
            for x in df[df['class'] ==
                        '主线工作'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '支线工作']) > 0:
            for x in df[df['class'] ==
                        '支线工作'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '文献阅读']) > 0:
            for x in df[df['class'] ==
                        '文献阅读'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '日常安排']) > 0:
            for x in df[df['class'] ==
                        '日常安排'].groupby('target').apply(target_details):
                res += x
        if len(df[df['class'] == '服务打杂']) > 0:
            for x in df[df['class'] ==
                        '服务打杂'].groupby('target').apply(target_details):
                res += x

        self.journalPannel.setText(res)
        self.journalPannel.adjustSize()
        return


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = My_QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    exit(app.exec_())
