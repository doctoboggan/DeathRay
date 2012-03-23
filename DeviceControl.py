#!/usr/bin/python -d
 
import sys, os, glob

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

    self.ui.lineEditIP.setText('129.59.93.179') #fill in this IP for now

    #Initialize the UI
    self.initUI()
    
    #instance variables
    self.argDict = {}
    self.commands = {'set':{}, 'get':{}}
    self.setOrGet = 'set'

    self.radioToggled()


  def initUI(self):
    #Connect the signals and slots
    self.connect(self.ui.listWidgetDevices, QtCore.SIGNAL('itemSelectionChanged()'), self.deviceSelected)
    self.connect(self.ui.listWidgetCommands, QtCore.SIGNAL('itemSelectionChanged()'), self.commandSelected)
    self.connect(self.ui.pushButtonExecute, QtCore.SIGNAL('clicked()'), self.getClicked)
    self.connect(self.ui.pushButtonFindDevices, QtCore.SIGNAL('clicked()'), self.findDevicesClicked)
    self.connect(self.ui.radioButtonSet, QtCore.SIGNAL('clicked()'), self.radioToggled)
    self.connect(self.ui.radioButtonGet, QtCore.SIGNAL('clicked()'), self.radioToggled)
    
    #set the argument boxes invisible at first
    self.ui.labelArg1.setVisible(False)
    self.ui.lineEditArg1.setVisible(False)
    self.ui.labelArg2.setVisible(False)
    self.ui.lineEditArg2.setVisible(False)
    self.ui.labelArg3.setVisible(False)
    self.ui.lineEditArg3.setVisible(False)
    self.ui.labelArg4.setVisible(False)
    self.ui.lineEditArg4.setVisible(False)
    self.ui.labelArg5.setVisible(False)
    self.ui.lineEditArg5.setVisible(False)
    
    self.ui.verticalLayoutArguments.setAlignment(Qt.Qt.AlignTop)
    self.ui.splitter.setSizes([200,200,200])
    self.ui.radioButtonSet.setChecked(True)


  def updateDeviceList(self):
    self.ui.listWidgetDevices.clear()
    for deviceName in self.deviceList:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetDevices)
      listItem.setText(deviceName)


  def updateCommands(self, deviceName):
    self.ui.listWidgetCommands.clear()
    for command in self.commands[self.setOrGet][str(deviceName).lower()]:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetCommands)
      listItem.setText(command)


  def deviceSelected(self):
    self.showArgBoxes(0)
    deviceName = self.ui.listWidgetDevices.currentItem().text()
    self.updateCommands(deviceName)


  def commandSelected(self):
    '''This method updates the argument view to display the relevent textboxes and labels
    '''
    self.ui.pushButtonExecute.setEnabled(True)
    commandName = str(self.ui.listWidgetCommands.currentItem().text())
    args = self.argDict[commandName].keys()
    values = self.argDict[commandName].values()
    numOfArgs = len(args)
    self.numOfArgs = numOfArgs #save it so other methods know many args are displayed.
    
    self.showArgBoxes(numOfArgs)

    if numOfArgs > 0:
      self.ui.labelArg1.setText(args[0]+':')
      self.ui.lineEditArg1.setText(values[0])
    if numOfArgs > 1:
      self.ui.labelArg2.setText(args[1]+':')
      self.ui.lineEditArg2.setText(values[1])
    if numOfArgs > 2:
      self.ui.labelArg3.setText(args[2]+':')
      self.ui.lineEditArg3.setText(values[2])
    if numOfArgs > 3:
      self.ui.labelArg4.setText(args[3]+':')
      self.ui.lineEditArg4.setText(values[3])
    if numOfArgs > 4:
      self.ui.labelArg5.setText(args[4]+':')
      self.ui.lineEditArg5.setText(values[4])


  def showArgBoxes(self, numOfArgs):
    #set the correct amount of text boxes visible
    self.ui.labelArg1.setVisible(numOfArgs>0)
    self.ui.lineEditArg1.setVisible(numOfArgs>0)
    self.ui.labelArg2.setVisible(numOfArgs>1)
    self.ui.lineEditArg2.setVisible(numOfArgs>1)
    self.ui.labelArg3.setVisible(numOfArgs>2)
    self.ui.lineEditArg3.setVisible(numOfArgs>2)
    self.ui.labelArg4.setVisible(numOfArgs>3)
    self.ui.lineEditArg4.setVisible(numOfArgs>3)
    self.ui.labelArg5.setVisible(numOfArgs>4)
    self.ui.lineEditArg5.setVisible(numOfArgs>4)


  def radioToggled(self):
    if self.ui.radioButtonSet.isChecked():
      self.setOrGet = 'set'
    else:
      self.setOrGet = 'get'


  def findDevicesClicked(self):
    self.IP = str(self.ui.lineEditIP.text())
    #self.deviceList, self.GPIBlist = utils.getAttachedDevices(self.IP, 30).fix()
    self.deviceList = ['DSO6032A', 'E3631A', '34401A']
    self.GPIBlist = ['gpib0,07', 'gpib0,10', 'gpib0,22']

    self.findArguments()
    self.updateDeviceList()


  def getClicked(self):
    '''
    this method is called whenever the get button is clicked. It makes the call to
    the correct command script and feeds it the arguments it needs
    '''
    kwargs={}
    if self.numOfArgs > 0:
      arg = str(self.ui.labelArg1.text()[:-1])
      value = str(self.ui.lineEditArg1.text())
      kwargs[arg] = value
    if self.numOfArgs > 1:
      arg = str(self.ui.labelArg2.text()[:-1])
      value = str(self.ui.lineEditArg2.text())
      kwargs[arg] = value
    if self.numOfArgs > 2:
      arg = str(self.ui.labelArg3.text()[:-1])
      value = str(self.ui.lineEditArg3.text())
      kwargs[arg] = value
    if self.numOfArgs > 3:
      arg = str(self.ui.labelArg4.text()[:-1])
      value = str(self.ui.lineEditArg4.text())
      kwargs[arg] = value
    if self.numOfArgs > 4:
      arg = str(self.ui.labelArg5.text()[:-1])
      value = str(self.ui.lineEditArg5.text())
      kwargs[arg] = value

    command = str(self.ui.listWidgetCommands.currentItem().text())
    device = str(self.ui.listWidgetDevices.currentItem().text())
    GPIB = self.GPIBlist[self.deviceList.index(device)]
    result = str(gpib_commands.command[command](self.IP, GPIB, device.lower(), **kwargs).do())
    self.ui.lineEditResult.setText(result)

    #update the commands arg dict to next time the most recently applied value is filled in
    self.argDict[command].update(kwargs)


  def findArguments(self):
    '''
    This method searches through the commands folder and finds all the def __init__ lines
    so it can extract the arguments for each command. It also checks the rightDevice
    variable to see which device each command should work with. 
    '''
    self.commands = {'set':{}, 'get':{}}
    for command in glob.glob('gpib_commands/*.py'):
      ffile = open(command)
      lines = ffile.readlines()
      commandName = os.path.split(command)[1].split('.')[0]
      for line in lines:
        #find the __init__ method to see what extra arguments all the commands need
        if 'def __init__(self,' == line.strip()[:18]:
          #argDict is a dict of dicts keyed on command with value of an arg:default-value dict
          self.argDict[commandName] = {}
          for arg in line[line.find('(')+7:line.find(')')].split(',')[3:-1]:
            a,v = arg.split('=')
            a,v = a.strip(), v.strip()[1:-1]
            self.argDict[commandName][a] = v

        #find the right device line and use it to build two command dicts (set and get commands)
        #key is device name and value is list of commands that work with that device
        if 'self.rightDevice = [' == line.strip()[:20]:
          deviceList = eval(line[line.find('['):]) #this is the rightDevice list
          for device in deviceList:
            if 'set' in commandName[:3]: #if the command starts with set put it in self.commands['set']
              if device in self.commands['set']:
                self.commands['set'][device].append(commandName)
              else:
                self.commands['set'][device] = [commandName]
            elif 'get' in commandName[:3]: #if the command starts with get put it in self.commands['get']
              if device in self.commands['get']:
                self.commands['get'][device].append(commandName)
              else:
                self.commands['get'][device] = [commandName]
  

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeviceControl()
  myapp.show()
  sys.exit(app.exec_())

