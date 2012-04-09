# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DeviceControlInterface.ui'
#
# Created: Mon Apr  2 20:46:36 2012
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
        MainWindow.setEnabled(True)
        MainWindow.resize(729, 775)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.tabWidgetMain = QtGui.QTabWidget(self.centralwidget)
        self.tabWidgetMain.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidgetMain.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidgetMain.setElideMode(QtCore.Qt.ElideRight)
        self.tabWidgetMain.setObjectName(_fromUtf8("tabWidgetMain"))
        self.tab_7 = QtGui.QWidget()
        self.tab_7.setObjectName(_fromUtf8("tab_7"))
        self.verticalLayout_16 = QtGui.QVBoxLayout(self.tab_7)
        self.verticalLayout_16.setObjectName(_fromUtf8("verticalLayout_16"))
        self.verticalLayout_13 = QtGui.QVBoxLayout()
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.label_15 = QtGui.QLabel(self.tab_7)
        self.label_15.setText(QtGui.QApplication.translate("MainWindow", "Select the desired FPGA script from the drop down, or None if you don\'t need one.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.verticalLayout_13.addWidget(self.label_15)
        self.label_16 = QtGui.QLabel(self.tab_7)
        self.label_16.setText(QtGui.QApplication.translate("MainWindow", "If you do select one, you must also select the file or folder the FPGA will be outputting to.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.verticalLayout_13.addWidget(self.label_16)
        self.verticalLayout_16.addLayout(self.verticalLayout_13)
        self.line_2 = QtGui.QFrame(self.tab_7)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout_16.addWidget(self.line_2)
        self.horizontalLayout_17 = QtGui.QHBoxLayout()
        self.horizontalLayout_17.setObjectName(_fromUtf8("horizontalLayout_17"))
        self.label_19 = QtGui.QLabel(self.tab_7)
        self.label_19.setMaximumSize(QtCore.QSize(81, 16777215))
        self.label_19.setText(QtGui.QApplication.translate("MainWindow", "Select Script:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.horizontalLayout_17.addWidget(self.label_19)
        self.comboBoxFPGA = QtGui.QComboBox(self.tab_7)
        self.comboBoxFPGA.setObjectName(_fromUtf8("comboBoxFPGA"))
        self.comboBoxFPGA.addItem(_fromUtf8(""))
        self.comboBoxFPGA.setItemText(0, QtGui.QApplication.translate("MainWindow", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontalLayout_17.addWidget(self.comboBoxFPGA)
        self.verticalLayout_16.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_15 = QtGui.QHBoxLayout()
        self.horizontalLayout_15.setObjectName(_fromUtf8("horizontalLayout_15"))
        self.pushButtonSelectFile = QtGui.QPushButton(self.tab_7)
        self.pushButtonSelectFile.setText(QtGui.QApplication.translate("MainWindow", "Select Output File(s)", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSelectFile.setObjectName(_fromUtf8("pushButtonSelectFile"))
        self.horizontalLayout_15.addWidget(self.pushButtonSelectFile)
        self.pushButtonSelectFolder = QtGui.QPushButton(self.tab_7)
        self.pushButtonSelectFolder.setText(QtGui.QApplication.translate("MainWindow", "Select Output Folder", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSelectFolder.setObjectName(_fromUtf8("pushButtonSelectFolder"))
        self.horizontalLayout_15.addWidget(self.pushButtonSelectFolder)
        self.verticalLayout_16.addLayout(self.horizontalLayout_15)
        self.scrollArea = QtGui.QScrollArea(self.tab_7)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 657, 458))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.labelFPGALocation = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.labelFPGALocation.setText(QtGui.QApplication.translate("MainWindow", "No File/Folder Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFPGALocation.setObjectName(_fromUtf8("labelFPGALocation"))
        self.verticalLayout_14.addWidget(self.labelFPGALocation)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_16.addWidget(self.scrollArea)
        self.tabWidgetMain.addTab(self.tab_7, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.tab_3)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.tab_3)
        self.label.setText(QtGui.QApplication.translate("MainWindow", "GPIB Gateway IP:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.lineEditIP = QtGui.QLineEdit(self.tab_3)
        self.lineEditIP.setText(_fromUtf8(""))
        self.lineEditIP.setObjectName(_fromUtf8("lineEditIP"))
        self.horizontalLayout_3.addWidget(self.lineEditIP)
        self.pushButtonFindDevices = QtGui.QPushButton(self.tab_3)
        self.pushButtonFindDevices.setText(QtGui.QApplication.translate("MainWindow", "Find Devices", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonFindDevices.setObjectName(_fromUtf8("pushButtonFindDevices"))
        self.horizontalLayout_3.addWidget(self.pushButtonFindDevices)
        self.verticalLayout_11.addLayout(self.horizontalLayout_3)
        self.splitter_vert = QtGui.QSplitter(self.tab_3)
        self.splitter_vert.setOrientation(QtCore.Qt.Vertical)
        self.splitter_vert.setObjectName(_fromUtf8("splitter_vert"))
        self.splitter_top = QtGui.QSplitter(self.splitter_vert)
        self.splitter_top.setOrientation(QtCore.Qt.Vertical)
        self.splitter_top.setObjectName(_fromUtf8("splitter_top"))
        self.line = QtGui.QFrame(self.splitter_top)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.layoutWidget_2 = QtGui.QWidget(self.splitter_top)
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.splitter = QtGui.QSplitter(self.layoutWidget_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget_3 = QtGui.QWidget(self.splitter)
        self.layoutWidget_3.setObjectName(_fromUtf8("layoutWidget_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget_3)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(self.layoutWidget_3)
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Devices:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.listWidgetDevices = QtGui.QListWidget(self.layoutWidget_3)
        self.listWidgetDevices.setObjectName(_fromUtf8("listWidgetDevices"))
        self.verticalLayout_2.addWidget(self.listWidgetDevices)
        self.layoutWidget_4 = QtGui.QWidget(self.splitter)
        self.layoutWidget_4.setObjectName(_fromUtf8("layoutWidget_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget_4)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.layoutWidget_4)
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Commands:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.listWidgetCommands = QtGui.QListWidget(self.layoutWidget_4)
        self.listWidgetCommands.setObjectName(_fromUtf8("listWidgetCommands"))
        self.verticalLayout_3.addWidget(self.listWidgetCommands)
        self.layoutWidget_5 = QtGui.QWidget(self.splitter)
        self.layoutWidget_5.setObjectName(_fromUtf8("layoutWidget_5"))
        self.verticalLayoutArguments = QtGui.QVBoxLayout(self.layoutWidget_5)
        self.verticalLayoutArguments.setMargin(0)
        self.verticalLayoutArguments.setObjectName(_fromUtf8("verticalLayoutArguments"))
        self.label_4 = QtGui.QLabel(self.layoutWidget_5)
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "Inputs:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayoutArguments.addWidget(self.label_4)
        self.groupBox = QtGui.QGroupBox(self.layoutWidget_5)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.labelArg1 = QtGui.QLabel(self.groupBox)
        self.labelArg1.setText(QtGui.QApplication.translate("MainWindow", "arg1:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelArg1.setObjectName(_fromUtf8("labelArg1"))
        self.horizontalLayout.addWidget(self.labelArg1)
        self.lineEditArg1 = QtGui.QLineEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditArg1.sizePolicy().hasHeightForWidth())
        self.lineEditArg1.setSizePolicy(sizePolicy)
        self.lineEditArg1.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEditArg1.setObjectName(_fromUtf8("lineEditArg1"))
        self.horizontalLayout.addWidget(self.lineEditArg1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.labelArg2 = QtGui.QLabel(self.groupBox)
        self.labelArg2.setText(QtGui.QApplication.translate("MainWindow", "arg2:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelArg2.setObjectName(_fromUtf8("labelArg2"))
        self.horizontalLayout_4.addWidget(self.labelArg2)
        self.lineEditArg2 = QtGui.QLineEdit(self.groupBox)
        self.lineEditArg2.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEditArg2.setObjectName(_fromUtf8("lineEditArg2"))
        self.horizontalLayout_4.addWidget(self.lineEditArg2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.labelArg3 = QtGui.QLabel(self.groupBox)
        self.labelArg3.setText(QtGui.QApplication.translate("MainWindow", "arg3:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelArg3.setObjectName(_fromUtf8("labelArg3"))
        self.horizontalLayout_5.addWidget(self.labelArg3)
        self.lineEditArg3 = QtGui.QLineEdit(self.groupBox)
        self.lineEditArg3.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEditArg3.setObjectName(_fromUtf8("lineEditArg3"))
        self.horizontalLayout_5.addWidget(self.lineEditArg3)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.labelArg4 = QtGui.QLabel(self.groupBox)
        self.labelArg4.setText(QtGui.QApplication.translate("MainWindow", "arg4:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelArg4.setObjectName(_fromUtf8("labelArg4"))
        self.horizontalLayout_6.addWidget(self.labelArg4)
        self.lineEditArg4 = QtGui.QLineEdit(self.groupBox)
        self.lineEditArg4.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEditArg4.setObjectName(_fromUtf8("lineEditArg4"))
        self.horizontalLayout_6.addWidget(self.lineEditArg4)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.labelArg5 = QtGui.QLabel(self.groupBox)
        self.labelArg5.setText(QtGui.QApplication.translate("MainWindow", "arg5:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelArg5.setObjectName(_fromUtf8("labelArg5"))
        self.horizontalLayout_7.addWidget(self.labelArg5)
        self.lineEditArg5 = QtGui.QLineEdit(self.groupBox)
        self.lineEditArg5.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEditArg5.setObjectName(_fromUtf8("lineEditArg5"))
        self.horizontalLayout_7.addWidget(self.lineEditArg5)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayoutArguments.addWidget(self.groupBox)
        self.verticalLayout_5.addWidget(self.splitter)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.pushButtonExecute = QtGui.QPushButton(self.layoutWidget_2)
        self.pushButtonExecute.setEnabled(False)
        self.pushButtonExecute.setText(QtGui.QApplication.translate("MainWindow", "Check Command", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonExecute.setObjectName(_fromUtf8("pushButtonExecute"))
        self.horizontalLayout_2.addWidget(self.pushButtonExecute)
        self.lineEditResult = QtGui.QLineEdit(self.layoutWidget_2)
        self.lineEditResult.setObjectName(_fromUtf8("lineEditResult"))
        self.horizontalLayout_2.addWidget(self.lineEditResult)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.tabWidgetDevices = QtGui.QTabWidget(self.splitter_vert)
        self.tabWidgetDevices.setObjectName(_fromUtf8("tabWidgetDevices"))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.horizontalLayout_12 = QtGui.QHBoxLayout(self.tab_5)
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.horizontalLayoutSavedCommands = QtGui.QHBoxLayout()
        self.horizontalLayoutSavedCommands.setObjectName(_fromUtf8("horizontalLayoutSavedCommands"))
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_5 = QtGui.QLabel(self.tab_5)
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "Saved Commands:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_7.addWidget(self.label_5)
        self.listWidgetSavedCommands = QtGui.QListWidget(self.tab_5)
        self.listWidgetSavedCommands.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidgetSavedCommands.sizePolicy().hasHeightForWidth())
        self.listWidgetSavedCommands.setSizePolicy(sizePolicy)
        self.listWidgetSavedCommands.setObjectName(_fromUtf8("listWidgetSavedCommands"))
        self.verticalLayout_7.addWidget(self.listWidgetSavedCommands)
        self.horizontalLayoutSavedCommands.addLayout(self.verticalLayout_7)
        self.verticalLayoutCommandButtons = QtGui.QVBoxLayout()
        self.verticalLayoutCommandButtons.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.verticalLayoutCommandButtons.setObjectName(_fromUtf8("verticalLayoutCommandButtons"))
        self.label_6 = QtGui.QLabel(self.tab_5)
        self.label_6.setMaximumSize(QtCore.QSize(159, 16777215))
        self.label_6.setText(_fromUtf8(""))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayoutCommandButtons.addWidget(self.label_6)
        self.pushButtonSave = QtGui.QPushButton(self.tab_5)
        self.pushButtonSave.setEnabled(False)
        self.pushButtonSave.setMaximumSize(QtCore.QSize(140, 16777215))
        self.pushButtonSave.setText(QtGui.QApplication.translate("MainWindow", "Save Command", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSave.setObjectName(_fromUtf8("pushButtonSave"))
        self.verticalLayoutCommandButtons.addWidget(self.pushButtonSave)
        self.pushButtonDelete = QtGui.QPushButton(self.tab_5)
        self.pushButtonDelete.setEnabled(False)
        self.pushButtonDelete.setMaximumSize(QtCore.QSize(140, 16777215))
        self.pushButtonDelete.setText(QtGui.QApplication.translate("MainWindow", "Delete Command", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonDelete.setObjectName(_fromUtf8("pushButtonDelete"))
        self.verticalLayoutCommandButtons.addWidget(self.pushButtonDelete)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayoutCommandButtons.addItem(spacerItem)
        self.pushButtonClear = QtGui.QPushButton(self.tab_5)
        self.pushButtonClear.setMaximumSize(QtCore.QSize(140, 16777215))
        self.pushButtonClear.setText(QtGui.QApplication.translate("MainWindow", "Clear All", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClear.setObjectName(_fromUtf8("pushButtonClear"))
        self.verticalLayoutCommandButtons.addWidget(self.pushButtonClear)
        self.horizontalLayoutSavedCommands.addLayout(self.verticalLayoutCommandButtons)
        self.horizontalLayout_12.addLayout(self.horizontalLayoutSavedCommands)
        self.tabWidgetDevices.addTab(self.tab_5, _fromUtf8(""))
        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName(_fromUtf8("tab_6"))
        self.horizontalLayout_13 = QtGui.QHBoxLayout(self.tab_6)
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.gridLayoutPlots = QtGui.QGridLayout()
        self.gridLayoutPlots.setObjectName(_fromUtf8("gridLayoutPlots"))
        self.groupBoxPlot1 = QtGui.QGroupBox(self.tab_6)
        self.groupBoxPlot1.setEnabled(True)
        self.groupBoxPlot1.setMinimumSize(QtCore.QSize(300, 136))
        self.groupBoxPlot1.setMaximumSize(QtCore.QSize(207, 142))
        self.groupBoxPlot1.setTitle(QtGui.QApplication.translate("MainWindow", "Plot 1", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBoxPlot1.setObjectName(_fromUtf8("groupBoxPlot1"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupBoxPlot1)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.horizontalLayout_18 = QtGui.QHBoxLayout()
        self.horizontalLayout_18.setObjectName(_fromUtf8("horizontalLayout_18"))
        self.pushButtonPlot1 = QtGui.QPushButton(self.groupBoxPlot1)
        self.pushButtonPlot1.setText(QtGui.QApplication.translate("MainWindow", "Plot Here", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonPlot1.setObjectName(_fromUtf8("pushButtonPlot1"))
        self.horizontalLayout_18.addWidget(self.pushButtonPlot1)
        self.pushButtonClearPlot1 = QtGui.QPushButton(self.groupBoxPlot1)
        self.pushButtonClearPlot1.setText(QtGui.QApplication.translate("MainWindow", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClearPlot1.setObjectName(_fromUtf8("pushButtonClearPlot1"))
        self.horizontalLayout_18.addWidget(self.pushButtonClearPlot1)
        self.verticalLayout_6.addLayout(self.horizontalLayout_18)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_7 = QtGui.QLabel(self.groupBoxPlot1)
        self.label_7.setText(QtGui.QApplication.translate("MainWindow", "Every", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_8.addWidget(self.label_7)
        self.doubleSpinBoxPlot1 = QtGui.QDoubleSpinBox(self.groupBoxPlot1)
        self.doubleSpinBoxPlot1.setSingleStep(0.5)
        self.doubleSpinBoxPlot1.setProperty("value", 5.0)
        self.doubleSpinBoxPlot1.setObjectName(_fromUtf8("doubleSpinBoxPlot1"))
        self.horizontalLayout_8.addWidget(self.doubleSpinBoxPlot1)
        self.label_8 = QtGui.QLabel(self.groupBoxPlot1)
        self.label_8.setText(QtGui.QApplication.translate("MainWindow", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_8.addWidget(self.label_8)
        self.verticalLayout_6.addLayout(self.horizontalLayout_8)
        self.labelPlot1 = QtGui.QLabel(self.groupBoxPlot1)
        self.labelPlot1.setFrameShape(QtGui.QFrame.Box)
        self.labelPlot1.setFrameShadow(QtGui.QFrame.Sunken)
        self.labelPlot1.setText(_fromUtf8(""))
        self.labelPlot1.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPlot1.setObjectName(_fromUtf8("labelPlot1"))
        self.verticalLayout_6.addWidget(self.labelPlot1)
        self.gridLayoutPlots.addWidget(self.groupBoxPlot1, 0, 1, 1, 1)
        self.groupBoxPlot2 = QtGui.QGroupBox(self.tab_6)
        self.groupBoxPlot2.setEnabled(True)
        self.groupBoxPlot2.setMinimumSize(QtCore.QSize(300, 136))
        self.groupBoxPlot2.setMaximumSize(QtCore.QSize(207, 142))
        self.groupBoxPlot2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBoxPlot2.setTitle(QtGui.QApplication.translate("MainWindow", "Plot 2", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBoxPlot2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBoxPlot2.setFlat(False)
        self.groupBoxPlot2.setObjectName(_fromUtf8("groupBoxPlot2"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.groupBoxPlot2)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.horizontalLayout_19 = QtGui.QHBoxLayout()
        self.horizontalLayout_19.setObjectName(_fromUtf8("horizontalLayout_19"))
        self.pushButtonPlot2 = QtGui.QPushButton(self.groupBoxPlot2)
        self.pushButtonPlot2.setText(QtGui.QApplication.translate("MainWindow", "Plot Here", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonPlot2.setObjectName(_fromUtf8("pushButtonPlot2"))
        self.horizontalLayout_19.addWidget(self.pushButtonPlot2)
        self.pushButtonClearPlot2 = QtGui.QPushButton(self.groupBoxPlot2)
        self.pushButtonClearPlot2.setText(QtGui.QApplication.translate("MainWindow", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClearPlot2.setObjectName(_fromUtf8("pushButtonClearPlot2"))
        self.horizontalLayout_19.addWidget(self.pushButtonClearPlot2)
        self.verticalLayout_8.addLayout(self.horizontalLayout_19)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_9 = QtGui.QLabel(self.groupBoxPlot2)
        self.label_9.setText(QtGui.QApplication.translate("MainWindow", "Every", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_9.addWidget(self.label_9)
        self.doubleSpinBoxPlot2 = QtGui.QDoubleSpinBox(self.groupBoxPlot2)
        self.doubleSpinBoxPlot2.setSingleStep(0.5)
        self.doubleSpinBoxPlot2.setProperty("value", 5.0)
        self.doubleSpinBoxPlot2.setObjectName(_fromUtf8("doubleSpinBoxPlot2"))
        self.horizontalLayout_9.addWidget(self.doubleSpinBoxPlot2)
        self.label_10 = QtGui.QLabel(self.groupBoxPlot2)
        self.label_10.setText(QtGui.QApplication.translate("MainWindow", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_9.addWidget(self.label_10)
        self.verticalLayout_8.addLayout(self.horizontalLayout_9)
        self.labelPlot2 = QtGui.QLabel(self.groupBoxPlot2)
        self.labelPlot2.setFrameShape(QtGui.QFrame.Box)
        self.labelPlot2.setFrameShadow(QtGui.QFrame.Sunken)
        self.labelPlot2.setText(_fromUtf8(""))
        self.labelPlot2.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPlot2.setObjectName(_fromUtf8("labelPlot2"))
        self.verticalLayout_8.addWidget(self.labelPlot2)
        self.gridLayoutPlots.addWidget(self.groupBoxPlot2, 0, 2, 1, 1)
        self.groupBoxPlot4 = QtGui.QGroupBox(self.tab_6)
        self.groupBoxPlot4.setEnabled(True)
        self.groupBoxPlot4.setMinimumSize(QtCore.QSize(300, 135))
        self.groupBoxPlot4.setMaximumSize(QtCore.QSize(207, 141))
        self.groupBoxPlot4.setTitle(QtGui.QApplication.translate("MainWindow", "Plot 4", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBoxPlot4.setObjectName(_fromUtf8("groupBoxPlot4"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.groupBoxPlot4)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.horizontalLayout_21 = QtGui.QHBoxLayout()
        self.horizontalLayout_21.setObjectName(_fromUtf8("horizontalLayout_21"))
        self.pushButtonPlot4 = QtGui.QPushButton(self.groupBoxPlot4)
        self.pushButtonPlot4.setText(QtGui.QApplication.translate("MainWindow", "Plot Here", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonPlot4.setObjectName(_fromUtf8("pushButtonPlot4"))
        self.horizontalLayout_21.addWidget(self.pushButtonPlot4)
        self.pushButtonClearPlot4 = QtGui.QPushButton(self.groupBoxPlot4)
        self.pushButtonClearPlot4.setText(QtGui.QApplication.translate("MainWindow", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClearPlot4.setObjectName(_fromUtf8("pushButtonClearPlot4"))
        self.horizontalLayout_21.addWidget(self.pushButtonClearPlot4)
        self.verticalLayout_10.addLayout(self.horizontalLayout_21)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.label_13 = QtGui.QLabel(self.groupBoxPlot4)
        self.label_13.setText(QtGui.QApplication.translate("MainWindow", "Every", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_11.addWidget(self.label_13)
        self.doubleSpinBoxPlot4 = QtGui.QDoubleSpinBox(self.groupBoxPlot4)
        self.doubleSpinBoxPlot4.setSingleStep(0.5)
        self.doubleSpinBoxPlot4.setProperty("value", 5.0)
        self.doubleSpinBoxPlot4.setObjectName(_fromUtf8("doubleSpinBoxPlot4"))
        self.horizontalLayout_11.addWidget(self.doubleSpinBoxPlot4)
        self.label_14 = QtGui.QLabel(self.groupBoxPlot4)
        self.label_14.setText(QtGui.QApplication.translate("MainWindow", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.horizontalLayout_11.addWidget(self.label_14)
        self.verticalLayout_10.addLayout(self.horizontalLayout_11)
        self.labelPlot4 = QtGui.QLabel(self.groupBoxPlot4)
        self.labelPlot4.setFrameShape(QtGui.QFrame.Box)
        self.labelPlot4.setFrameShadow(QtGui.QFrame.Sunken)
        self.labelPlot4.setText(_fromUtf8(""))
        self.labelPlot4.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPlot4.setObjectName(_fromUtf8("labelPlot4"))
        self.verticalLayout_10.addWidget(self.labelPlot4)
        self.gridLayoutPlots.addWidget(self.groupBoxPlot4, 1, 2, 1, 1)
        self.groupBoxPlot3 = QtGui.QGroupBox(self.tab_6)
        self.groupBoxPlot3.setEnabled(True)
        self.groupBoxPlot3.setMinimumSize(QtCore.QSize(300, 135))
        self.groupBoxPlot3.setMaximumSize(QtCore.QSize(207, 141))
        self.groupBoxPlot3.setTitle(QtGui.QApplication.translate("MainWindow", "Plot 3", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBoxPlot3.setObjectName(_fromUtf8("groupBoxPlot3"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.groupBoxPlot3)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.horizontalLayout_20 = QtGui.QHBoxLayout()
        self.horizontalLayout_20.setObjectName(_fromUtf8("horizontalLayout_20"))
        self.pushButtonPlot3 = QtGui.QPushButton(self.groupBoxPlot3)
        self.pushButtonPlot3.setText(QtGui.QApplication.translate("MainWindow", "Plot Here", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonPlot3.setObjectName(_fromUtf8("pushButtonPlot3"))
        self.horizontalLayout_20.addWidget(self.pushButtonPlot3)
        self.pushButtonClearPlot3 = QtGui.QPushButton(self.groupBoxPlot3)
        self.pushButtonClearPlot3.setText(QtGui.QApplication.translate("MainWindow", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClearPlot3.setObjectName(_fromUtf8("pushButtonClearPlot3"))
        self.horizontalLayout_20.addWidget(self.pushButtonClearPlot3)
        self.verticalLayout_9.addLayout(self.horizontalLayout_20)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.label_11 = QtGui.QLabel(self.groupBoxPlot3)
        self.label_11.setText(QtGui.QApplication.translate("MainWindow", "Every", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_10.addWidget(self.label_11)
        self.doubleSpinBoxPlot3 = QtGui.QDoubleSpinBox(self.groupBoxPlot3)
        self.doubleSpinBoxPlot3.setSingleStep(0.5)
        self.doubleSpinBoxPlot3.setProperty("value", 5.0)
        self.doubleSpinBoxPlot3.setObjectName(_fromUtf8("doubleSpinBoxPlot3"))
        self.horizontalLayout_10.addWidget(self.doubleSpinBoxPlot3)
        self.label_12 = QtGui.QLabel(self.groupBoxPlot3)
        self.label_12.setText(QtGui.QApplication.translate("MainWindow", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_10.addWidget(self.label_12)
        self.verticalLayout_9.addLayout(self.horizontalLayout_10)
        self.labelPlot3 = QtGui.QLabel(self.groupBoxPlot3)
        self.labelPlot3.setFrameShape(QtGui.QFrame.Box)
        self.labelPlot3.setFrameShadow(QtGui.QFrame.Sunken)
        self.labelPlot3.setText(_fromUtf8(""))
        self.labelPlot3.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPlot3.setObjectName(_fromUtf8("labelPlot3"))
        self.verticalLayout_9.addWidget(self.labelPlot3)
        self.gridLayoutPlots.addWidget(self.groupBoxPlot3, 1, 1, 1, 1)
        self.horizontalLayout_13.addLayout(self.gridLayoutPlots)
        self.tabWidgetDevices.addTab(self.tab_6, _fromUtf8(""))
        self.verticalLayout_11.addWidget(self.splitter_vert)
        self.tabWidgetMain.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.tab_4)
        self.verticalLayout_15.setObjectName(_fromUtf8("verticalLayout_15"))
        self.checkBoxLogData = QtGui.QCheckBox(self.tab_4)
        self.checkBoxLogData.setText(QtGui.QApplication.translate("MainWindow", "Save Log File?", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxLogData.setTristate(False)
        self.checkBoxLogData.setObjectName(_fromUtf8("checkBoxLogData"))
        self.verticalLayout_15.addWidget(self.checkBoxLogData)
        self.horizontalLayout_16 = QtGui.QHBoxLayout()
        self.horizontalLayout_16.setObjectName(_fromUtf8("horizontalLayout_16"))
        self.pushButtonLogLocation = QtGui.QPushButton(self.tab_4)
        self.pushButtonLogLocation.setEnabled(False)
        self.pushButtonLogLocation.setText(QtGui.QApplication.translate("MainWindow", "Select Location", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonLogLocation.setObjectName(_fromUtf8("pushButtonLogLocation"))
        self.horizontalLayout_16.addWidget(self.pushButtonLogLocation)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem1)
        self.verticalLayout_15.addLayout(self.horizontalLayout_16)
        self.labelLocationSelected = QtGui.QLabel(self.tab_4)
        self.labelLocationSelected.setText(QtGui.QApplication.translate("MainWindow", "No File Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLocationSelected.setObjectName(_fromUtf8("labelLocationSelected"))
        self.verticalLayout_15.addWidget(self.labelLocationSelected)
        spacerItem2 = QtGui.QSpacerItem(20, 513, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_15.addItem(spacerItem2)
        self.tabWidgetMain.addTab(self.tab_4, _fromUtf8(""))
        self.verticalLayout_12.addWidget(self.tabWidgetMain)
        self.horizontalLayout_14 = QtGui.QHBoxLayout()
        self.horizontalLayout_14.setObjectName(_fromUtf8("horizontalLayout_14"))
        self.pushButtonSaveExperiment = QtGui.QPushButton(self.centralwidget)
        self.pushButtonSaveExperiment.setEnabled(False)
        self.pushButtonSaveExperiment.setText(QtGui.QApplication.translate("MainWindow", "Save Experiment Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSaveExperiment.setObjectName(_fromUtf8("pushButtonSaveExperiment"))
        self.horizontalLayout_14.addWidget(self.pushButtonSaveExperiment)
        self.pushButtonLoadExperiment = QtGui.QPushButton(self.centralwidget)
        self.pushButtonLoadExperiment.setText(QtGui.QApplication.translate("MainWindow", "Load Experiment Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonLoadExperiment.setObjectName(_fromUtf8("pushButtonLoadExperiment"))
        self.horizontalLayout_14.addWidget(self.pushButtonLoadExperiment)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem3)
        self.pushButtonDone = QtGui.QPushButton(self.centralwidget)
        self.pushButtonDone.setEnabled(True)
        self.pushButtonDone.setText(QtGui.QApplication.translate("MainWindow", "Start Experiment", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonDone.setObjectName(_fromUtf8("pushButtonDone"))
        self.horizontalLayout_14.addWidget(self.pushButtonDone)
        self.verticalLayout_12.addLayout(self.horizontalLayout_14)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 729, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidgetMain.setCurrentIndex(0)
        self.tabWidgetDevices.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(self.tab_7), QtGui.QApplication.translate("MainWindow", "FPGA", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidgetDevices.setTabText(self.tabWidgetDevices.indexOf(self.tab_5), QtGui.QApplication.translate("MainWindow", "Set Up Devices", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidgetDevices.setTabText(self.tabWidgetDevices.indexOf(self.tab_6), QtGui.QApplication.translate("MainWindow", "Plot Data", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(self.tab_3), QtGui.QApplication.translate("MainWindow", "Devices", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(self.tab_4), QtGui.QApplication.translate("MainWindow", "Log Data", None, QtGui.QApplication.UnicodeUTF8))
