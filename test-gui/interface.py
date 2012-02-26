# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created: Thu Feb 23 02:04:49 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(514, 227)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.listWidgetDevices = QtGui.QListWidget(self.centralwidget)
        self.listWidgetDevices.setObjectName(_fromUtf8("listWidgetDevices"))
        self.horizontalLayout.addWidget(self.listWidgetDevices)
        self.listWidgetCommands = QtGui.QListWidget(self.centralwidget)
        self.listWidgetCommands.setObjectName(_fromUtf8("listWidgetCommands"))
        self.horizontalLayout.addWidget(self.listWidgetCommands)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setText(QtGui.QApplication.translate("MainWindow", "IP Address:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.lineEditIP = QtGui.QLineEdit(self.centralwidget)
        self.lineEditIP.setObjectName(_fromUtf8("lineEditIP"))
        self.horizontalLayout_3.addWidget(self.lineEditIP)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "GPIB ID:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.lineEditGPIB = QtGui.QLineEdit(self.centralwidget)
        self.lineEditGPIB.setObjectName(_fromUtf8("lineEditGPIB"))
        self.horizontalLayout_4.addWidget(self.lineEditGPIB)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.pushButtonGet = QtGui.QPushButton(self.centralwidget)
        self.pushButtonGet.setText(QtGui.QApplication.translate("MainWindow", "Get Data", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonGet.setObjectName(_fromUtf8("pushButtonGet"))
        self.horizontalLayout_2.addWidget(self.pushButtonGet)
        self.lineEditResult = QtGui.QLineEdit(self.centralwidget)
        self.lineEditResult.setObjectName(_fromUtf8("lineEditResult"))
        self.horizontalLayout_2.addWidget(self.lineEditResult)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 514, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        pass

