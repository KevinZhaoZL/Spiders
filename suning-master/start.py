import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QMessageBox, QGridLayout, QLabel, QPushButton, QFrame


class Ui_MainWindow(QWidget):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(564, 270)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton.setGeometry(QtCore.QRect(320, 60, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.textEdit = QtWidgets.QTextEdit(self.centralWidget)
        self.textEdit.setGeometry(QtCore.QRect(60, 60, 151, 31))
        self.textEdit.setObjectName("textEdit")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_2.setGeometry(QtCore.QRect(320, 150, 111, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(60, 30, 151, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(60, 110, 151, 41))
        self.label_2.setObjectName("label_2")
        self.comboBox = QtWidgets.QComboBox(self.centralWidget)
        self.comboBox.setGeometry(QtCore.QRect(60, 160, 87, 22))
        self.comboBox.setObjectName("comboBox")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 564, 26))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.comboBox.addItems(["%s" % x for x in range(1, 100)])
        self.pushButton.clicked.connect(self.start)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "苏宁爬虫"))
        self.pushButton.setText(_translate("MainWindow", "开启爬虫"))
        self.pushButton_2.setText(_translate("MainWindow", "暂停/恢复爬虫"))
        self.label.setText(_translate("MainWindow", "请输入需要爬取的商品"))
        self.label_2.setText(_translate("MainWindow", "请选择需要爬取的页数\n"
"(每页大约60件商品)"))

    def start(self):
        key=self.textEdit.toPlainText()
        page=self.comboBox.currentText()
        if key:
            os.system('redis-cli flushdb')
            os.system('redis-cli lpush mycrawler:start_urls http://www.suning.com')
            os.system('scrapy crawl sn -a key='+str(key)+' -a page='+str(page)+'')
            QMessageBox.critical(self,"提示","爬虫完毕！")
        else:
            QMessageBox.critical(self,"警告","请先输入您需要爬取的商品！")
            return
        #os.system('scrapy crawl jd -a key='+str(key)+' -a page='+str(page)+'')

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()
    os.system('redis-cli flushdb')
