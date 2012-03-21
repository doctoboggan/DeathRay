#!/usr/bin/python -d
 
import sys, os

from PyQt4 import QtCore, QtGui, Qt
from GUIfiles import DeviceControlInterface

import utils, gpib_commands


from pdb import set_trace as bp #DEBUGING


 
class DeviceControl(QtGui.QMainWindow):
  '''Main application class that contains the GUI control and helper methods.
  '''

  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self)
    self.ui = DeviceControlInterface.Ui_MainWindow()
    self.ui.setupUi(self)

    self.IP = '129.59.93.179'
    self.GPIB = 'gpib0,22'

    #self.deviceList, self.GPIBlist = utils.getAttachedDevices(self.defaultIP, 30).fix()
    self.deviceList = ['DSO6032A', 'E3631A', '34401A']
    self.GPIBlist = ['gpib0,07', 'gpib0,10', 'gpib0,22']

    self.getCommands()

    self.updateDeviceList()

    #instance variables

   #Initialize the UI
    self.initUI()


    self.findArguments()
    
  def initUI(self):
    #Connect the signals and slots
    self.connect(self.ui.listWidgetDevices, QtCore.SIGNAL('itemSelectionChanged()'), self.deviceSelected)
    self.connect(self.ui.pushButtonGet, QtCore.SIGNAL('clicked()'), self.getClicked)

    self.ui.lineEditIP.setText(self.IP)
    self.ui.lineEditGPIB.setText(self.GPIB)


  def updateDeviceList(self):
    for deviceName in self.deviceList:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetDevices)
      listItem.setText(deviceName)

  def deviceSelected(self):
    deviceName = self.ui.listWidgetDevices.currentItem().text()
    self.updateCommands(deviceName)

  def updateCommands(self, deviceName):
    self.ui.listWidgetCommands.clear()
    for command in self.commands[str(deviceName).lower()]:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetCommands)
      listItem.setText(command)

  def getClicked(self):
    command = self.ui.listWidgetCommands.currentItem().text()
    IP = str(self.ui.lineEditIP.text())
    device = str(self.ui.listWidgetDevices.currentItem().text())
    GPIB = self.GPIBlist[self.deviceList.index(device)]
    result = str(gpib_commands.command[str(command)](IP, GPIB, device.lower()).do())
    self.ui.lineEditResult.setText(result)

  def getCommands(self):
    self.commands = {}
    for module in gpib_commands.command.keys():
      deviceList = gpib_commands.command[module](self.IP, self.GPIB).rightDevice
      for device in deviceList:
        if device in self.commands:
          self.commands[device].append(module)
        else:
          self.commands[device] = [module]



  def findArguments(self):
    for module in os.listdir('gpib_commands'):
      ffile = open('gpib_commands/'+module)
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

