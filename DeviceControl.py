#!/usr/bin/python -d
 
import sys, os

from PyQt4 import QtCore, QtGui, Qt
from interface import Ui_MainWindow

import modules

 
class DeathRay(QtGui.QMainWindow):
  '''
  Main application class that contains the GUI control and helper methods.
  '''

  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.updateDeviceList()

    #instance variables
    self.defaultIP = '129.59.93.179'
    self.defaultGPIB = 'gpib0,22'

   #Initialize the UI
    self.initUI()


    self.findArguments()
    
  def initUI(self):
    #Connect the signals and slots
    self.connect(self.ui.listWidgetDevices, QtCore.SIGNAL('itemSelectionChanged()'), self.deviceSelected)
    self.connect(self.ui.pushButtonGet, QtCore.SIGNAL('clicked()'), self.getClicked)

    self.ui.lineEditIP.setText(self.defaultIP)
    self.ui.lineEditGPIB.setText(self.defaultGPIB)


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
    result = str(modules.command[str(command)](IP, GPIB, device).get())
    1/0
    self.ui.lineEditResult.setText(result)


  def findArguments(self):
    for module in os.listdir('modules'):
      ffile = open('modules/'+module)
      lines = ffile.readlines()
      for line in lines:
        if 'def __init__' in line:
          print module
          print line[line.find('(')+7:line.find(')')]

  

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeathRay()
  myapp.show()
  sys.exit(app.exec_())

