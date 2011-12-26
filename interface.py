# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created: Mon Dec 26 04:00:06 2011
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
        MainWindow.resize(837, 537)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.listRun = QtGui.QListWidget(self.splitter)
        self.listRun.setMaximumSize(QtCore.QSize(200, 16777215))
        self.listRun.setObjectName(_fromUtf8("listRun"))
        self.qwtPlot = Qwt5.QwtPlot(self.splitter)
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 837, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuDeathRay = QtGui.QMenu(self.menubar)
        self.menuDeathRay.setTitle(QtGui.QApplication.translate("MainWindow", "DeathRay", None, QtGui.QApplication.UnicodeUTF8))
        self.menuDeathRay.setObjectName(_fromUtf8("menuDeathRay"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionPreferences = QtGui.QAction(MainWindow)
        self.actionPreferences.setText(QtGui.QApplication.translate("MainWindow", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionNew_Experiment = QtGui.QAction(MainWindow)
        self.actionNew_Experiment.setEnabled(False)
        self.actionNew_Experiment.setText(QtGui.QApplication.translate("MainWindow", "New Experiment", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew_Experiment.setObjectName(_fromUtf8("actionNew_Experiment"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open file(s) for plotting...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave_Plot = QtGui.QAction(MainWindow)
        self.actionSave_Plot.setEnabled(False)
        self.actionSave_Plot.setText(QtGui.QApplication.translate("MainWindow", "Save Plot", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Plot.setObjectName(_fromUtf8("actionSave_Plot"))
        self.actionSave_Experiment_Setup = QtGui.QAction(MainWindow)
        self.actionSave_Experiment_Setup.setEnabled(False)
        self.actionSave_Experiment_Setup.setText(QtGui.QApplication.translate("MainWindow", "Save Experiment Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Experiment_Setup.setObjectName(_fromUtf8("actionSave_Experiment_Setup"))
        self.actionAbout_2 = QtGui.QAction(MainWindow)
        self.actionAbout_2.setText(QtGui.QApplication.translate("MainWindow", "About...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_2.setObjectName(_fromUtf8("actionAbout_2"))
        self.actionPreferences_2 = QtGui.QAction(MainWindow)
        self.actionPreferences_2.setText(QtGui.QApplication.translate("MainWindow", "Preferences...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences_2.setObjectName(_fromUtf8("actionPreferences_2"))
        self.actionQuit_2 = QtGui.QAction(MainWindow)
        self.actionQuit_2.setText(QtGui.QApplication.translate("MainWindow", "Quit DeathRay", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit_2.setObjectName(_fromUtf8("actionQuit_2"))
        self.actionAsd = QtGui.QAction(MainWindow)
        self.actionAsd.setText(QtGui.QApplication.translate("MainWindow", "asd", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAsd.setObjectName(_fromUtf8("actionAsd"))
        self.menuFile.addAction(self.actionNew_Experiment)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Plot)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Experiment_Setup)
        self.menuDeathRay.addAction(self.actionQuit_2)
        self.menubar.addAction(self.menuDeathRay.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        pass

from PyQt4 import Qwt5
