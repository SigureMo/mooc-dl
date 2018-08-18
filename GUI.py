import sys
import os
sys.path.append(os.path.abspath('..'))
from MOOC_Downloading import VERSION as version
from Easyload import *

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5 import QtCore
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

class MOOC_Downloading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.refSettings()
        self.settings['mob_token'] = ''
        self.initUI()
        
    def initUI(self):
        #任务栏
        self.statusBar()

        #菜单栏
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&设置')
        helpMenu = menubar.addMenu('&帮助')
        
        switchAction = QAction('&切换用户', self)
        switchAction.setShortcut('Alt+Q')
        switchAction.setStatusTip('切换登录账号')
        switchAction.triggered.connect(self.switchUser)
        fileMenu.addAction(switchAction)
        
        courseAction = QAction('&订阅课程', self)
        courseAction.setShortcut('Alt+D')
        courseAction.setStatusTip('修改订阅课程配置')
        courseAction.triggered.connect(self.courseConfig)
        fileMenu.addAction(courseAction)

        settingAction = QAction('&全局配置', self)
        settingAction.setShortcut('Alt+S')
        settingAction.setStatusTip('修改全局配置')
        settingAction.triggered.connect(self.chSettings)
        fileMenu.addAction(settingAction)

        aboutAction = QAction('&关于', self)
        aboutAction.setShortcut('Alt+A')
        aboutAction.setStatusTip('关于本程序')
        aboutAction.triggered.connect(self.about)
        helpMenu.addAction(aboutAction)

        helpAction = QAction('&使用帮助', self)
        helpAction.setShortcut('Alt+H')
        helpAction.setStatusTip('使用帮助')
        helpAction.triggered.connect(self.about)
        helpMenu.addAction(helpAction)

        self.canvas = Canvas(self.settings)
        self.setCentralWidget(self.canvas)

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('MOOC_Downloading')
        self.setWindowIcon(QIcon('timg.ico'))
        self.switchUser()
        self.show()

    def switchUser(self):
        LoginDialog(self.settings).exec_()
        self.refSettings()

    def courseConfig(self):
        if self.settings.get('mob_token'):
            CourseDialog(self.settings).exec_()
            self.refSettings()
        else:
            self.canvas.infoText.append('请先登录！\n')

    def chSettings(self):
        SettingsDialog(self.settings).exec_()
        self.refSettings()

    def about(self):
        AboutDialog().exec_()

    def help(self):
        pass

    def refSettings(self):
        try:
            with open('data/settings.json', 'rb') as f:
                self.settings = json.loads(f.read().decode())
        except:
            self.settings = {}

    def saveSettings(self):
        with open('data/settings.json', 'wb') as f:
            f.write(json.dumps(self.settings).encode())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '不开心，哼',
            "真的要走吗？", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)
 
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class Canvas(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.infoQ = queue.Queue()
        self.workQ = []
        self.taskQ = queue.Queue()
        self.initUI()
         
         
    def initUI(self):
        # 任务显示栏
        self.taskBox = QVBoxLayout()
        self.taskBar1 = TaskBar({})
        self.taskBar2 = TaskBar({})

        # 信息提示栏
        self.infoBox = QVBoxLayout()
        ## 信息提示框
        self.infoLbl = QLabel('提示信息')
        self.infoText = QTextEdit()

        ## 操作按钮
        self.operationBox = QHBoxLayout()
        self.decButton = QPushButton("-")
        self.startButton = QPushButton("|>")
        self.startButton.clicked.connect(self.start)
        self.incButton = QPushButton("+")
        self.sumVelLbl = QLabel('总速度：0kb/s')
        
        # 全局布局
        self.operationBox.addWidget(self.decButton)
        self.operationBox.addWidget(self.startButton)
        self.operationBox.addWidget(self.incButton)
        self.operationBox.addWidget(self.sumVelLbl)
        self.operationBox.addStretch(1)
        self.taskBox.addWidget(self.taskBar1)
        self.taskBox.addWidget(self.taskBar2)
        self.taskBox.addStretch(1)
        self.infoBox.addWidget(self.infoLbl)
        self.infoBox.addWidget(self.infoText)
        self.infoBox.addLayout(self.operationBox)
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.taskBox)
        self.mainLayout.addLayout(self.infoBox)
        self.setLayout(self.mainLayout)

        self.infoTimer = QTimer()
        self.infoTimer.setInterval(100)
        self.infoTimer.start()
        self.infoTimer.timeout.connect(self.refreshInfo)

        self.taskTimer = QTimer()
        self.taskTimer.setInterval(1000)
        self.taskTimer.start()
        self.taskTimer.timeout.connect(self.refreshTask)

        self.show()

    def refreshInfo(self):
        if not self.infoQ.empty():
            self.infoText.append(self.infoQ.get())
        if self.taskQ.empty():
            self.startButton.setText('|>')
        else:
            self.startButton.setText('||')
            
    def refreshTask(self):
        pass
        #self.taskBox.clear()
        #self.configs = {}
        #for courseware in self.workQ:
        #    config['name'] = courseware.name
        #    config['localsize'] = courseware.f.local_size/1024
        #    config['size'] = courseware.f.size/1024
        #    config['speed'] = (config['localsize'] - self.configs.get(courseware.name, {'localsize':0})['localsize'])/1024
        #    if config['size'] and config['size'] >= config['localsize']:
        #        config['progress'] = int(config['localsize']/config['size'])
        #    else:
        #        config['progress'] = 0
        #    config['flag'] = courseware.f.flag
        #    self.configs[courseware.name] = config
        #    self.taskBox.addWidget(TaskBar(config))

    def start(self):
        def download(args):
            for courseware in coursewares:
                courseware.download(*args)
            
        #def scan(_queue):
        #    time.sleep()
        #    _queue.put((1,))

        #th = threading.Thread(target=scan,args=(self.notify_queue,))
        #th.setDaemon(True)
        #th.start()
        try:
            courses = []
            self.startButton.setText('||')
            self.infoText.append('[Info]初始化课件中……')
            for courseConfig in self.settings.get('courseConfigs',[]):
                coursewares = getcoursewares(courseConfig.get('courseinfo'), \
                                             self.settings.get(platform.system()+'Root', os.path.expanduser("~")+os.sep+'Desktop'), \
                                             self.settings.get('mob_token'), \
                                             courseConfig.get('sharpness','sd'), \
                                             self.infoQ)
                if courseConfig.get('isLoad',False):
                    courses.append((coursewares, courseConfig.get('weekNum',[0]), courseConfig.get('loadType',[1,3,4])))
            self.infoText.append('[Info]初始化完成，开始下载')
            for course in courses:
                coursewares = course[0]
                self.infoText.append('[Info]当前下载课程：{}'.format(coursewares[0].coursename))
                general_view(courseConfig.get('courseinfo'), self.settings.get(platform.system()+'Root', os.path.expanduser("~")+os.sep+'Desktop'))
                playlist(coursewares[0].coursename, coursewares, self.settings.get(platform.system()+'Root', os.path.expanduser("~")+os.sep+'Desktop'),'RP')

                for courseware in coursewares:
                    self.taskQ.put((courseware, course[1], course[2]))
                thpl = ThreadPool(self.settings.get('processNum', 5), self.taskQ, self.workQ)

                #th = threading.Thread(target=download, args=(course[-2:],))
                #th.setDaemon(True)
                #th.start()
                
                #pool=ThreadPool(10)
                #for courseware in coursewares:
                #    pool.apply_async(courseware.download, args=(course[1], course[2]))
                #pool.close()
                #pool.join()
                
                #for courseware in coursewares:
                #    courseware.download(*course[-2:])
            self.startButton.setText('|>')
        except Exception as e:
            print(e)
            
class ThreadPool():
    def __init__(self, num, taskQ, workQ):
        self.num = num
        self.taskQ = taskQ
        self.workQ = workQ
        self.threads = []
        for n in range(num):
            th = threading.Thread(target=self.run)
            th.setDaemon(True)
            self.threads.append(th)
            th.start()

    def run(self):
        while True:
            if not self.taskQ.empty():
                task = self.taskQ.get()
                self.workQ.append(task[0])
                task[0].download(*task[1:])
                del self.workQ[self.workQ.index(task[0])]
            else:
                break

class TaskBar(QFrame):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initUI()
         
    def initUI(self):
        self.fileLbl = QLabel('当前下载：{} {}MB/{}MB {} kb/s'.format(self.config.get('name','xxx'),
                                                            self.config.get('localsize',0),
                                                            self.config.get('size', 0),
                                                            self.config.get('speed', 0)))
        self.pbar = QProgressBar()
        self.pbar.setGeometry(30, 40, 200, 25)
        self.pbar.setValue(self.config.get('progress',0))
        if self.config.get('flag', True):
            self.pauseButton = QPushButton("||")
        else:
            self.pauseButton = QPushButton("|>")
        self.cancelButton = QPushButton("X")

        self.controlBox = QHBoxLayout()
        self.controlBox.addWidget(self.pbar)
        self.controlBox.addWidget(self.pauseButton)
        self.controlBox.addWidget(self.cancelButton)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.fileLbl)
        self.mainLayout.addLayout(self.controlBox)
        self.setLayout(self.mainLayout)
        
        self.show()

class LoginDialog(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.initUI()

    def initUI(self):
        self.setWindowTitle("登录")      # 窗口标题
        self.setGeometry(400,400,300,200)   # 窗口位置与大小
 
        self.usernameLbl = QLabel('账号：')
        self.passwordLbl = QLabel('密码：')
        if self.settings.get('mob-token'):
            self.stateLbl = QLabel('当前用户：{}'.format(self.settings['username']))
        else:
            self.stateLbl = QLabel('状态：未登录')
 
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.isAutoLogin = QCheckBox('记住密码')

        self.loginBtn = QPushButton('登录')
        self.loginBtn.clicked.connect(self.login)
        self.cancelBtn = QPushButton('取消')
        self.cancelBtn.clicked.connect(self.close)
        self.hBtnsLayout = QHBoxLayout()
        self.hBtnsLayout.addWidget(self.loginBtn)
        self.hBtnsLayout.addWidget(self.cancelBtn)

        self.vlayout = QVBoxLayout()
        self.glayout = QGridLayout()
        self.glayout.addWidget(self.usernameLbl,0,0)
        self.glayout.addWidget(self.passwordLbl,1,0)
        self.glayout.addWidget(self.isAutoLogin,2,0)
        self.glayout.addWidget(self.username,0,1)
        self.glayout.addWidget(self.password,1,1)
        self.vlayout.addLayout(self.glayout)
        self.vlayout.addWidget(self.stateLbl)
        self.vlayout.addLayout(self.hBtnsLayout)
        self.setLayout(self.vlayout)

        if self.settings.get('isAutoLogin'):
            self.isAutoLogin.setChecked(True)
            self.username.setText(self.settings['username'])
            self.password.setText('*' * self.settings['passwordLen'])
        else:
            self.isAutoLogin.setChecked(False)
        self.show()

    def login(self):
        username = self.username.text()
        password = self.password.text()
        flag=hashlib.md5()
        flag.update(password.encode('utf-8'))
        passwd = flag.hexdigest()
        if username == 'sharing':
            username = 's_sharing@126.com'
            self.username.setText(username)
            passwd = 'e10adc3949ba59abbe56e057f20f883e'
            self.password.setText('*' * 6)
        if self.settings.get('isAutoLogin') and \
           username == self.settings['username'] and \
           password == '*' * self.settings['passwordLen']:
            passwd = self.settings['passwd']
        self.stateLbl.setText('登录中...')
        self.stateLbl.adjustSize()
        results = gettoken(username,passwd)
        if results[1] == 0:
            self.stateLbl.setText('登录成功')
            self.settings['mob_token'] = results[0]
            self.settings['isAutoLogin'] = self.isAutoLogin.isChecked()
            self.settings['username'] = username
            self.settings['passwordLen'] = len(password)
            self.settings['passwd'] = passwd
            with open('data/settings.json', 'wb') as f:
                f.write(json.dumps(self.settings).encode())
            self.close()
        elif results[1] == 100:
            self.stateLbl.setText('账号或密码错误，请重新登录')
        else:
            self.stateLbl.setText('发生未知错误，错误码{}'.format(results[1]))

class SettingsDialog(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("全局配置")      # 窗口标题
        self.setGeometry(400,400,300,200)   # 窗口位置与大小
 
        self.pathLbl = QLabel('路径:')
        self.processNumLbl = QLabel('进程数:')
 
        self.path = QLineEdit()
        self.processNum = QComboBox()
        for n in range(10):
            self.processNum.addItem(str(n+1))

        self.pathBtn = QPushButton("...")
        self.pathBtn.clicked.connect(self.selectPath)
        self.isAutoSetting = QCheckBox('自动配置')
        self.isAutoSetting.toggle()

        self.saveBtn = QPushButton('保存')
        self.saveBtn.clicked.connect(self.save)
        self.cancelBtn = QPushButton('取消')
        self.cancelBtn.clicked.connect(self.close)
        self.hBtnsLayout = QHBoxLayout()
        self.hBtnsLayout.addWidget(self.saveBtn)
        self.hBtnsLayout.addWidget(self.cancelBtn)

        self.glayout = QGridLayout()
        self.vlayout = QVBoxLayout()
        self.glayout.addWidget(self.pathLbl,0,0)
        self.glayout.addWidget(self.processNumLbl,1,0)
        self.glayout.addWidget(self.path,0,1,1,2)
        self.glayout.addWidget(self.processNum,1,1)
        self.glayout.addWidget(self.pathBtn,0,3)
        self.glayout.addWidget(self.isAutoSetting,1,2)
        self.vlayout.addLayout(self.glayout)
        self.vlayout.addLayout(self.hBtnsLayout)
        self.setLayout(self.vlayout)

        self.isAutoSetting.setChecked(self.settings.get('isAutoSetting',False))
        self.path.setText(self.settings.get(platform.system()+'Root',''))
        self.processNum.setCurrentIndex(self.settings.get('processNum', 1)- 1)
        
        self.show()

    def selectPath(self):
        root = self.path.text() if os.path.exists(self.path.text()) else os.path.expanduser("~")+os.sep+'Desktop'
        dirPath = QFileDialog.getExistingDirectory(self, "选择下载根目录", root)
        if dirPath:
            self.path.setText(dirPath)
 
    def save(self):
        self.settings[platform.system()+'Root'] = self.path.text()
        self.settings['processNum'] = self.processNum.currentIndex() + 1
        self.settings['isAutoSetting'] = self.isAutoSetting.isChecked()
        with open('data/settings.json', 'wb') as f:
            f.write(json.dumps(self.settings).encode())
        self.close()

class CourseDialog(QDialog):
    def __init__(self,settings):
        super().__init__()
        self.settings = settings
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("课程配置")      # 窗口标题
        self.setGeometry(400,400,1000,250)   # 窗口位置与大小

        self.tableWidget = QTableWidget(self)
        #self.tableWidget.setGeometry(340, 160, 224, 100)
        self.widths = (60, 200, 200, 200, 200)
        self.tableWidget.setColumnCount(len(self.widths))
        for colNum in range(len(self.widths)):
            self.tableWidget.setColumnWidth(colNum, self.widths[colNum])

        self.tableWidget.setHorizontalHeaderLabels(('是否下载', '课程号', '周次', '清晰度', '类型'))
        self.tableWidget.setSelectionMode(QTableWidget.NoSelection)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed) # 表头不可拖动
        self.courseConfigs = []

        for rowNum in range(len(self.settings['courseConfigs'])):
            self.tableWidget.insertRow(rowNum)
            courseConfigWdts = CourseConfigWdts(rowNum, self.settings, self.settings['courseConfigs'][rowNum])
            self.courseConfigs.append(courseConfigWdts)
            for colNum in range(len(courseConfigWdts.Wdts)):
                self.tableWidget.setCellWidget(rowNum, colNum, courseConfigWdts.Wdts[colNum])

        for rowNum in range(3):
            rowNum += len(self.settings['courseConfigs'])
            self.tableWidget.insertRow(rowNum)
            courseConfigWdts = CourseConfigWdts(rowNum, self.settings, {})
            self.courseConfigs.append(courseConfigWdts)
            for colNum in range(len(courseConfigWdts.Wdts)):
                self.tableWidget.setCellWidget(rowNum, colNum, courseConfigWdts.Wdts[colNum])
                #self.tableWidget.setItem(count, 0, QTableWidgetItem('item0'))
        
        self.addLineBtn = QPushButton('新增空白列')
        self.addLineBtn.clicked.connect(self.addLine)
        self.saveBtn = QPushButton('保存')
        self.saveBtn.clicked.connect(self.save)
        self.cancelBtn = QPushButton('取消')
        self.cancelBtn.clicked.connect(self.close)
        self.hBtnsLayout = QHBoxLayout()
        self.hBtnsLayout.addStretch(1)
        self.hBtnsLayout.addWidget(self.addLineBtn)
        self.hBtnsLayout.addWidget(self.saveBtn)
        self.hBtnsLayout.addWidget(self.cancelBtn)
        
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.tableWidget)
        self.vlayout.addStretch(1)
        self.vlayout.addLayout(self.hBtnsLayout)

        self.setLayout(self.vlayout)
        self.show()
 
    def save(self):
        self.settings['courseConfigs'] = []
        for courseConfig in self.courseConfigs:
            courseConfig = courseConfig.getConfig()
            if courseConfig.get('tid'):
                self.settings['courseConfigs'].append(dict(courseConfig))
        with open('data/settings.json', 'wb') as f:
            f.write(json.dumps(self.settings).encode())
        self.close()

    def addLine(self):
        rowNum = len(self.settings['courseConfigs'])
        self.tableWidget.insertRow(rowNum)
        courseConfigWdts = CourseConfigWdts(rowNum, self.settings, {})
        self.courseConfigs.append(courseConfigWdts)
        for colNum in range(len(courseConfigWdts.Wdts)):
            self.tableWidget.setCellWidget(rowNum, colNum, courseConfigWdts.Wdts[colNum])

class CourseConfigWdts():
    def __init__(self, id, settings, config={}):
        self.id = id
        self.settings = settings
        self.config = config
        
        self.isLoad = QCheckBox()
        self.tid = QLineEdit()
        self.tidBtn = QPushButton('...')
        self.tidBtn.clicked.connect(lambda : self.selectTid())
        self.weekNumStart = QComboBox()
        self.weekNumStart.addItem("1")
        self.weekNumSep = QLabel('~')
        self.weekNumEnd = QComboBox()
        self.weekNumEnd.addItem("1")
        self.isShd = QRadioButton('超清')
        self.isHd = QRadioButton('高清')
        self.isSd = QRadioButton('标清')
        self.isSd.toggle()
        self.loadType1 = QCheckBox('视频')
        self.loadType1.toggle()
        self.loadType3 = QCheckBox('文档')
        self.loadType3.toggle()
        self.loadType4 = QCheckBox('附件')
        self.loadType4.toggle()

        self.isloadWdt = self.newWdts([self.isLoad])
        self.tidWdt = self.newWdts([self.tid, self.tidBtn])
        self.weekNumWdt = self.newWdts([self.weekNumStart, self.weekNumSep, self.weekNumEnd])
        self.sharpnessWdt = self.newWdts([self.isShd, self.isHd, self.isSd])
        self.loadTypeWdt = self.newWdts([self.loadType1, self.loadType3, self.loadType4])

        self.lbls = ('是否下载', '课程号', '周次', '类型', '清晰度')
        self.Wdts = (self.isloadWdt, self.tidWdt, self.weekNumWdt, self.loadTypeWdt, self.sharpnessWdt)

        if self.config:
            try:
                self.refInfo(self.config['tid'])
            except Exception as e:
                print(e)
            self.isLoad.setChecked(self.config.get('isLoad',False))
            self.tid.setText(self.config.get('tid',''))
            self.weekNumStart.setCurrentIndex(self.config.get('weekNum', [0])[0])
            self.weekNumEnd.setCurrentIndex(self.config.get('weekNum', [0])[-1])
            self.loadType1.setChecked(1 in self.config.get('loadType', [1,3,4]))
            self.loadType3.setChecked(3 in self.config.get('loadType', [1,3,4]))
            self.loadType4.setChecked(4 in self.config.get('loadType', [1,3,4]))
            self.isSd.setChecked(self.config.get('sharpness', 'sd') == 'sd')
            self.isShd.setChecked(self.config['sharpness'] == 'shd')
            self.isHd.setChecked(self.config['sharpness'] == 'hd')
            
                

    def newWdts(self, wdts):
        widget = QWidget()
        hLayout = QHBoxLayout()
        for wdt in wdts:
            hLayout.addWidget(wdt)
        hLayout.setContentsMargins(5,2,5,2)
        widget.setLayout(hLayout)
        return widget

    def refInfo(self, tid):
        self.courseinfo = get_courseinfo(tid, self.settings.get('mob_token'))
        self.courseDto = self.courseinfo.get('results').get('courseDto')
        self.cid = self.courseDto.get('id')
        self.coursename = self.courseDto.get('name')
        self.chapters = self.courseinfo.get('results').get('termDto').get('chapters')
        self.config['courseinfo'] = self.courseinfo
        self.config['courseDto'] = self.courseDto
        self.config['cid'] = self.cid
        self.config['coursename'] = self.coursename
        self.config['chapters'] = self.chapters
        for weekNum in range(len(self.chapters)):
            num = str(weekNum + 1)
            if self.weekNumStart.findText(num) == -1:
                self.weekNumStart.addItem(num)
            if self.weekNumEnd.findText(num) == -1:
                self.weekNumEnd.addItem(num)

    def selectTid(self):
        selectTidDialog = SelectTidDialog()
        if selectTidDialog.exec_():
            tid = selectTidDialog.getTid()
            self.tid.setText(tid)
            self.refInfo(tid)

    def getConfig(self):
        if self.tid.text():
            self.config['id'] = self.id
            self.config['isLoad'] = self.isLoad.isChecked()
            self.config['tid'] = self.tid.text()
            self.config['weekNum'] = list(range(self.weekNumStart.currentIndex(), self.weekNumEnd.currentIndex()+1))
            p = [1,3,4]
            self.config['loadType'] = list(filter(lambda b:(self.loadType1.isChecked(),self.loadType3.isChecked(),self.loadType4.isChecked())[p.index(b)], p))
            self.config['sharpness'] = ['shd', 'hd', 'sd'][(self.isShd.isChecked(), self.isHd.isChecked(), self.isSd.isChecked()).index(True)]
        else:
            self.config = {}
        #print(self.config)
        return self.config

class SelectTidDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("课程号查询")      # 窗口标题
        self.setGeometry(400,400,400,250)   # 窗口位置与大小

        self.cid = QLineEdit()
        self.selectBtn = QPushButton('Search')
        self.selectBtn.clicked.connect(self.search)
        self.tidRbs = QFrame()
        self.vRbsLayout = QVBoxLayout()
        self.vRbsLayout.addStretch(1)
        self.tidRbs.setLayout(self.vRbsLayout)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
        self.vlayout = QVBoxLayout()
        self.selectBox = QHBoxLayout()
        self.selectBox.addWidget(self.cid)
        self.selectBox.addWidget(self.selectBtn)
        self.vlayout.addLayout(self.selectBox)
        self.vlayout.addWidget(self.tidRbs)
        self.vlayout.addStretch(1)

        self.hBtnsLayout = QHBoxLayout()
        self.hBtnsLayout.addStretch(1)
        self.hBtnsLayout.addWidget(self.buttons)
        self.vlayout.addLayout(self.hBtnsLayout)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.vlayout)
        self.show()

    def search(self):
        #self.tidRbs = QFrame()
        #self.vRbsLayout.clear()
        self.coursename, self.terminfos = getterminfos(self.cid.text())
        if self.coursename:
            self.vRbsLayout.addWidget(QLabel('课程名：{}'.format(self.coursename)))
            self.Rbs = []
            for termnum in range(len(self.terminfos)):
                terminfo = self.terminfos[termnum]
                rb = QRadioButton('第%d次开课：'%(termnum+1)+terminfo['text']+'，课程号：'+terminfo['id'])
                self.Rbs.append(rb)
                self.vRbsLayout.addWidget(rb)
        else:
            self.vRbsLayout.addWidget(QLabel('未匹配到任何课程，请重试'))
        #self.vRbsLayout.addStretch(1)
        #self.tidRbs.setLayout(self.vRbsLayout)
            
    def getTid(self):
        for index in range(len(self.Rbs)):
            if self.Rbs[index].isChecked():
                return self.terminfos[index]['id']

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("关于")      # 窗口标题
        self.setGeometry(400,400,300,200)   # 窗口位置与大小

        try:
            self.versionLbl = QLabel('版本号：{}'.format('.'.join(list(map(lambda x:str(x),version)))))
        except Exception as e:
            print(e)
        self.selectNewVer = QPushButton('检查更新')
        self.newVerInfoLbl = QLabel('当前版本已为最新版本！')
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.versionLbl)
        self.vlayout.addWidget(self.selectNewVer)
        self.vlayout.addWidget(self.newVerInfoLbl)
        #self.vlayout.addStretch(1)

        self.hBtnsLayout = QHBoxLayout()
        self.hBtnsLayout.addStretch(1)
        self.hBtnsLayout.addWidget(self.buttons)
        self.vlayout.addLayout(self.hBtnsLayout)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.vlayout)
        self.show()
         
if __name__ == '__main__':
     
    app = QApplication(sys.argv)
    ex = MOOC_Downloading()
    sys.exit(app.exec_()) 
