# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'welcomewindow.ui'
#
# Created: Fri Mar 16 13:26:12 2012
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
        MainWindow.resize(529, 534)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "                                                                       Welcome", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.textBrowser = QtGui.QTextBrowser(self.centralwidget)
        self.textBrowser.setHtml(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/newPrefix/test.png\" /></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Enter IP address:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.IPaddresslineEdit = QtGui.QLineEdit(self.centralwidget)
        self.IPaddresslineEdit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Enter IP address</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.IPaddresslineEdit.setInputMask(QtGui.QApplication.translate("MainWindow", "\"000.000.000.000\"; ", None, QtGui.QApplication.UnicodeUTF8))
        self.IPaddresslineEdit.setObjectName(_fromUtf8("IPaddresslineEdit"))
        self.horizontalLayout.addWidget(self.IPaddresslineEdit)
        self.verifyButton = QtGui.QPushButton(self.centralwidget)
        self.verifyButton.setText(QtGui.QApplication.translate("MainWindow", "verify", None, QtGui.QApplication.UnicodeUTF8))
        self.verifyButton.setObjectName(_fromUtf8("verifyButton"))
        self.horizontalLayout.addWidget(self.verifyButton)
        self.clearButton = QtGui.QPushButton(self.centralwidget)
        self.clearButton.setText(QtGui.QApplication.translate("MainWindow", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.clearButton.setObjectName(_fromUtf8("clearButton"))
        self.horizontalLayout.addWidget(self.clearButton)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.fpgaButton = QtGui.QPushButton(self.centralwidget)
        self.fpgaButton.setEnabled(False)
        self.fpgaButton.setText(QtGui.QApplication.translate("MainWindow", "FPGA", None, QtGui.QApplication.UnicodeUTF8))
        self.fpgaButton.setObjectName(_fromUtf8("fpgaButton"))
        self.horizontalLayout_2.addWidget(self.fpgaButton)
        self.gpibButton = QtGui.QPushButton(self.centralwidget)
        self.gpibButton.setEnabled(False)
        self.gpibButton.setText(QtGui.QApplication.translate("MainWindow", "Gpib", None, QtGui.QApplication.UnicodeUTF8))
        self.gpibButton.setObjectName(_fromUtf8("gpibButton"))
        self.horizontalLayout_2.addWidget(self.gpibButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.existButton = QtGui.QPushButton(self.centralwidget)
        self.existButton.setText(QtGui.QApplication.translate("MainWindow", "EXIST", None, QtGui.QApplication.UnicodeUTF8))
        self.existButton.setObjectName(_fromUtf8("existButton"))
        self.gridLayout.addWidget(self.existButton, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 529, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuCredit = QtGui.QMenu(self.menubar)
        self.menuCredit.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuCredit.setObjectName(_fromUtf8("menuCredit"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setTitle(QtGui.QApplication.translate("MainWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionClose = QtGui.QAction(MainWindow)
        self.actionClose.setText(QtGui.QApplication.translate("MainWindow", "close ", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "User manual", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionDeveloper_manual = QtGui.QAction(MainWindow)
        self.actionDeveloper_manual.setText(QtGui.QApplication.translate("MainWindow", "Developer manual", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDeveloper_manual.setObjectName(_fromUtf8("actionDeveloper_manual"))
        self.actionCheck_update = QtGui.QAction(MainWindow)
        self.actionCheck_update.setText(QtGui.QApplication.translate("MainWindow", "Check update", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCheck_update.setObjectName(_fromUtf8("actionCheck_update"))
        self.actionWebsite = QtGui.QAction(MainWindow)
        self.actionWebsite.setText(QtGui.QApplication.translate("MainWindow", "Website", None, QtGui.QApplication.UnicodeUTF8))
        self.actionWebsite.setObjectName(_fromUtf8("actionWebsite"))
        self.actionAbout_2 = QtGui.QAction(MainWindow)
        self.actionAbout_2.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_2.setObjectName(_fromUtf8("actionAbout_2"))
        self.actionCopy = QtGui.QAction(MainWindow)
        self.actionCopy.setText(QtGui.QApplication.translate("MainWindow", "Copy", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopy.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+C", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCopy.setObjectName(_fromUtf8("actionCopy"))
        self.actionPaste = QtGui.QAction(MainWindow)
        self.actionPaste.setText(QtGui.QApplication.translate("MainWindow", "Paste", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPaste.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+V", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPaste.setObjectName(_fromUtf8("actionPaste"))
        self.actionClear = QtGui.QAction(MainWindow)
        self.actionClear.setText(QtGui.QApplication.translate("MainWindow", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClear.setObjectName(_fromUtf8("actionClear"))
        self.menuFile.addAction(self.actionClose)
        self.menuCredit.addAction(self.actionAbout)
        self.menuCredit.addAction(self.actionDeveloper_manual)
        self.menuCredit.addSeparator()
        self.menuCredit.addAction(self.actionCheck_update)
        self.menuCredit.addAction(self.actionWebsite)
        self.menuCredit.addSeparator()
        self.menuCredit.addAction(self.actionAbout_2)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionClear)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuCredit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.clearButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.IPaddresslineEdit.clear)
        QtCore.QObject.connect(self.existButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.close)
        QtCore.QObject.connect(self.actionClear, QtCore.SIGNAL(_fromUtf8("activated()")), self.IPaddresslineEdit.clear)
        QtCore.QObject.connect(self.actionCopy, QtCore.SIGNAL(_fromUtf8("activated()")), self.IPaddresslineEdit.copy)
        QtCore.QObject.connect(self.actionPaste, QtCore.SIGNAL(_fromUtf8("activated()")), self.IPaddresslineEdit.paste)
        QtCore.QObject.connect(self.actionClose, QtCore.SIGNAL(_fromUtf8("activated()")), MainWindow.close)
        QtCore.QObject.connect(self.verifyButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.gpibButton.setEnabled)
        QtCore.QObject.connect(self.verifyButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.fpgaButton.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        pass

