#!/usr/bin/python -d
 
import sys, random, pprint

from PyQt4 import QtCore, QtGui, Qt
from interface import Ui_MainWindow

import currentDC, voltageAC, voltageDC


 
class DeathRay(QtGui.QMainWindow):
  '''
  Main application class that contains the GUI control and helper methods.
  '''

  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.initUI()
    self.updateDeviceList()
    
  def initUI(self):
    #Connect the signals and slots
    self.connect(self.ui.listWidgetDevices, QtCore.SIGNAL('itemSelectionChanged()'), self.deviceSelected)
    self.connect(self.ui.pushButtonGet, QtCore.SIGNAL('clicked()'), self.getClicked)
    pass


  def updateDeviceList(self):
    for deviceName in ['hp34401a', 'hpe3631a']:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetDevices)
      listItem.setText(deviceName)

  def deviceSelected(self):
    deviceName = self.ui.listWidgetDevices.currentItem().text()
    self.updateCommands(deviceName)

  def updateCommands(self, deviceName):
    self.ui.listWidgetCommands.clear()
    if deviceName == 'hp34401a':
      for command in ['currentDC', 'voltageAC', 'voltageDC']:
        listItem = QtGui.QListWidgetItem(self.ui.listWidgetCommands)
        listItem.setText(command)
    if deviceName == 'hpe3631a':
      for command in ['currentDC', 'voltageDC']:
        listItem = QtGui.QListWidgetItem(self.ui.listWidgetCommands)
        listItem.setText(command)

  def getClicked(self):
    command = self.ui.listWidgetCommands.currentItem().text()
    IP = str(self.ui.lineEditIP.text())
    GPIB = str(self.ui.lineEditGPIB.text())
    device = str(self.ui.listWidgetDevices.currentItem().text())
    if command == 'currentDC':
      result = str(currentDC.currentDC(IP, GPIB, device).get())
    if command == 'voltageAC':
      result = str(voltageDC.voltageDC(IP, GPIB, device).get())
    if command == 'voltageDC':
      result = str(voltageDC.voltageDC(IP, GPIB, device).get())


    self.ui.lineEditResult.setText(result)

  

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeathRay()
  myapp.show()
  sys.exit(app.exec_())

