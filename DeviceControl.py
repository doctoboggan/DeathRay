#!/usr/bin/python -d
 
import sys, os

from PyQt4 import QtCore, QtGui, Qt
from DeviceControlInterface import Ui_MainWindow

import DRmodules, DRscripts


from pdb import set_trace as bp #DEBUGING


 
class DeviceControl(QtGui.QMainWindow):
  '''Main application class that contains the GUI control and helper methods.
  '''

  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.defaultIP = '129.59.93.179'
    self.defaultGPIB = 'gpib0,22'

    self.deviceList, self.GPIBlist = DRscripts.getdevice(self.defaultIP, 23).fix()
    print DRscripts.getcommand(self.defaultIP, self.defaultGPIB, '34401A').do()

    self.updateDeviceList()

    #instance variables

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
    for deviceName in self.deviceList:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetDevices)
      listItem.setText(deviceName)

  def deviceSelected(self):
    deviceName = self.ui.listWidgetDevices.currentItem().text()
    self.updateCommands(deviceName)

  def updateCommands(self, deviceName):
    self.ui.listWidgetCommands.clear()
    if deviceName == 'hp34401a':
      for command in ['getcurrentDC', 'getvoltageAC', 'getvoltageDC']:
        listItem = QtGui.QListWidgetItem(self.ui.listWidgetCommands)
        listItem.setText(command)
    if deviceName == 'hpe3631a':
      for command in ['getcurrentDC', 'getvoltageDC']:
        listItem = QtGui.QListWidgetItem(self.ui.listWidgetCommands)
        listItem.setText(command)

  def getClicked(self):
    command = self.ui.listWidgetCommands.currentItem().text()
    IP = str(self.ui.lineEditIP.text())
    GPIB = str(self.ui.lineEditGPIB.text())
    device = str(self.ui.listWidgetDevices.currentItem().text())
    result = str(DRmodules.command[str(command)](IP, GPIB, device).get())
    1/0
    self.ui.lineEditResult.setText(result)


  def findArguments(self):
    for module in os.listdir('DRmodules'):
      ffile = open('DRmodules/'+module)
      lines = ffile.readlines()
      for line in lines:
        if 'def __init__' in line:
          print module
          print line[line.find('(')+7:line.find(')')]

  

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeviceControl()
  myapp.show()
  sys.exit(app.exec_())

