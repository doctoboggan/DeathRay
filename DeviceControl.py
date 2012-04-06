#!/usr/bin/python -d
 
import sys, os, glob, cPickle

from PyQt4 import QtCore, QtGui, Qt
from interfaces import DeviceControlInterface
from PlotWindow import PlotWindow
from utils import Thread
from utils import getAttachedDevices

import gpib_commands, fpga_scripts

from pdb import set_trace as bp #DEBUGING

 
class DeviceControl(QtGui.QMainWindow):
  '''Main application class that contains the GUI control and helper methods.
  '''

  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self)
    self.ui = DeviceControlInterface.Ui_MainWindow()
    self.ui.setupUi(self)

    self.ui.lineEditIP.setText('129.59.93.179') #fill in this IP for now

    #instance variables
    self.fpgaInfo = []
    self.fpgaScriptName = None
    self.fpgaOutputLocation = ''
    self.logFile = ''
    self.argDict = {}
    self.savedCommands = []
    self.savedPlotCommands = [None, None, None, None]
    self.usedCommands = []
    self.failedCommands = []
    self.commands = {'set':{}, 'get':{}}
    self.setOrGet = 'set'
    self.plotLabels = [self.ui.labelPlot1, self.ui.labelPlot2, 
                       self.ui.labelPlot3, self.ui.labelPlot4]
    self.plotSpinBoxes = [self.ui.doubleSpinBoxPlot1, self.ui.doubleSpinBoxPlot2, 
                          self.ui.doubleSpinBoxPlot3, self.ui.doubleSpinBoxPlot4]
    self.plotButtons = [self.ui.pushButtonPlot1, self.ui.pushButtonPlot2,
                        self.ui.pushButtonPlot3, self.ui.pushButtonPlot4]
    self.clearPlotButtons = [self.ui.pushButtonClearPlot1, self.ui.pushButtonClearPlot2,
                             self.ui.pushButtonClearPlot3, self.ui.pushButtonClearPlot4]

    #Initialize the UI
    self.initUI()

  def initUI(self):
    '''Initialize the user interface
    '''
    #Connect the signals and slots
      #list widgets selected
    self.connect(self.ui.listWidgetDevices, QtCore.SIGNAL('itemSelectionChanged()'), self.deviceSelected)
    self.connect(self.ui.listWidgetCommands, QtCore.SIGNAL('itemSelectionChanged()'), self.commandSelected)
    self.connect(self.ui.listWidgetSavedCommands, QtCore.SIGNAL('itemSelectionChanged()'),
        self.savedCommandSelected)
      #buttons
    self.connect(self.ui.pushButtonExecute, QtCore.SIGNAL('clicked()'), self.testClicked)
    self.connect(self.ui.pushButtonFindDevices, QtCore.SIGNAL('clicked()'), self.findDevicesClicked)
    self.connect(self.ui.pushButtonSave, QtCore.SIGNAL('clicked()'), self.saveClicked)
    self.connect(self.ui.pushButtonDelete, QtCore.SIGNAL('clicked()'), self.deleteClicked)
    self.connect(self.ui.pushButtonClear, QtCore.SIGNAL('clicked()'), self.clearClicked)
    self.connect(self.ui.pushButtonPlot1, QtCore.SIGNAL('clicked()'), lambda: self.plotClicked(0))
    self.connect(self.ui.pushButtonPlot2, QtCore.SIGNAL('clicked()'), lambda: self.plotClicked(1))
    self.connect(self.ui.pushButtonPlot3, QtCore.SIGNAL('clicked()'), lambda: self.plotClicked(2))
    self.connect(self.ui.pushButtonPlot4, QtCore.SIGNAL('clicked()'), lambda: self.plotClicked(3))
    self.connect(self.ui.pushButtonClearPlot1, QtCore.SIGNAL('clicked()'), lambda: self.clearPlotClicked(0))
    self.connect(self.ui.pushButtonClearPlot2, QtCore.SIGNAL('clicked()'), lambda: self.clearPlotClicked(1))
    self.connect(self.ui.pushButtonClearPlot3, QtCore.SIGNAL('clicked()'), lambda: self.clearPlotClicked(2))
    self.connect(self.ui.pushButtonClearPlot4, QtCore.SIGNAL('clicked()'), lambda: self.clearPlotClicked(3))
    self.connect(self.ui.pushButtonSaveExperiment, QtCore.SIGNAL('clicked()'), self.saveExperimentClicked)
    self.connect(self.ui.pushButtonLoadExperiment, QtCore.SIGNAL('clicked()'), self.loadExperimentClicked)
    self.connect(self.ui.pushButtonDone, QtCore.SIGNAL('clicked()'), self.doneClicked)
    self.connect(self.ui.pushButtonSelectFile, QtCore.SIGNAL('clicked()'), self.selectFileClicked)
    self.connect(self.ui.pushButtonSelectFolder, QtCore.SIGNAL('clicked()'), self.selectFolderClicked)
    self.connect(self.ui.pushButtonLogLocation, QtCore.SIGNAL('clicked()'), self.logClicked)
      #thread slots
    self.connect(self, QtCore.SIGNAL('foundDevices()'), self.devicesFound)
      #misc slots
    self.connect(self.ui.tabWidgetDevices, QtCore.SIGNAL('currentChanged(int)'), self.tabChanged)
    self.connect(self.ui.comboBoxFPGA, QtCore.SIGNAL('currentIndexChanged(int)'), self.fpgaComboChanged)
    self.connect(self.ui.checkBoxLogData, QtCore.SIGNAL('clicked()'), self.logDataClicked)
    
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
    
    #Set sizes, alignments, and initial checked states
    self.ui.verticalLayoutArguments.setAlignment(Qt.Qt.AlignTop)
    self.ui.splitter.setSizes([200,200,200])
    self.ui.splitter_vert.setVisible(False)
    self.ui.splitter_top.setVisible(False)
    self.ui.splitter_vert.setSizes([200,100])

    #populate the fpga_scripts combo box
    self.updateFPGAComboBox()



############################
#### DRAWING METHODS
############################

  def updateDeviceList(self):
    '''Draw the found devices to the device list widget
    '''
    self.ui.listWidgetDevices.clear()
    for deviceName in self.deviceList:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetDevices)
      listItem.setText(deviceName)


  def updateCommands(self, deviceName):
    '''Draw the found commands to the commands list widget
    '''
    self.ui.listWidgetCommands.clear()
    for command in self.commands[self.setOrGet][str(deviceName).lower()]:
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetCommands)
      listItem.setText(command)

  
  def updateSavedCommands(self):
    '''Draw the saved commands to the saved commands list widget
    '''
    self.ui.pushButtonSaveExperiment.setEnabled(True)
    self.ui.listWidgetSavedCommands.clear()
    index = 0
    for command, args, kwargs in self.savedCommands:
      index += 1
      listItem = QtGui.QListWidgetItem(self.ui.listWidgetSavedCommands)
      text = str(str(index)+') '+args[2])+' -> '+str(command) + str(kwargs)
      listItem.setText(text)


  def showArgBoxes(self, numOfArgs):
    '''sets the correct amount of argument text boxes visible
    '''
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


  def updateFPGAComboBox(self):
    for scriptName in sorted(fpga_scripts.experiment):
      self.ui.comboBoxFPGA.addItem(scriptName)
      self.fpgaInfo.append(fpga_scripts.experiment[scriptName])




##############################
#### BUTTON CLICKED METHODS
##############################
 
  def findDevicesClicked(self):
    '''Spawns a new thread to search for attached devices
    '''
    self.IP = str(self.ui.lineEditIP.text())
    self.ui.statusbar.showMessage('Searching for devices, this may take about 30 seconds')
    self.ui.pushButtonFindDevices.setEnabled(False)
    self.ui.pushButtonFindDevices.setText('Searching...')
    thread = Thread.Thread(self.findDevices, self.IP)
    thread.start()
    self.thread = thread


  def testClicked(self):
    '''This method is called whenever the check command button is clicked. It makes the call to
    the correct command script and feeds it the arguments it needs
    '''
    command, args, kwargs = self.returnCurrentCommand()
    commandObject = gpib_commands.command[command](*args, **kwargs)
    self.usedCommands.append(commandObject)
    result = str(self.usedCommands[-1].do())
    self.ui.lineEditResult.setText(result)


  def saveClicked(self):
    self.ui.pushButtonSaveExperiment.setEnabled(True)
    command, args, kwargs = self.returnCurrentCommand()
    if (command, args, kwargs) not in self.savedCommands:
      self.savedCommands.append((command, args, kwargs))

    self.updateSavedCommands()

  def deleteClicked(self):
    item = self.ui.listWidgetSavedCommands.currentItem()
    index = int(self.ui.listWidgetSavedCommands.indexFromItem(item).row())
    del self.savedCommands[index]
    self.updateSavedCommands()


  def clearClicked(self):
    self.savedCommands = []
    self.ui.listWidgetSavedCommands.clear()


  def plotClicked(self, plotNumber):
    '''Saves the plot command and draws to the label
    '''
    command, args, kwargs = self.returnCurrentCommand()
    self.plotLabels[plotNumber].setText(args[2]+'->'+command)
    self.savedPlotCommands[plotNumber] = ([command, args, kwargs])


  def clearPlotClicked(self, plotNumber):
    '''
    '''
    self.plotLabels[plotNumber].setText('')
    self.savedPlotCommands[plotNumber] = None
  

  def saveExperimentClicked(self):
    '''Writes self.savedCommands and self.savedPlotCommands to a pickle file
    '''
    self.storeTimeIntervals()
    fname = QtGui.QFileDialog.getSaveFileName(self, 'Select location to save experiment',
        '/Users/jack/Documents')        
    f = open(fname, 'w')
    cPickle.dump((self.savedCommands, self.savedPlotCommands, self.fpgaOutputLocation,
      self.fpgaScriptName, self.logFile), f)
    f.close()


  def loadExperimentClicked(self):
    '''Loads in self.savedCommands and self.savedPlotCommands from a pickled file
    This method also draws the new information to the lists and labels
    '''
    fileName = QtGui.QFileDialog.getOpenFileNames(self, 'Select save file',
        '/Users/jack/Documents')
    f = open(str(fileName[0]), 'r')
    (self.savedCommands, self.savedPlotCommands, self.fpgaOutputLocation,
      self.fpgaScriptName, self.logFile) = cPickle.load(f)
    f.close()
    self.ui.splitter_vert.setVisible(True)
    self.updateSavedCommands()
    index = 0
    #fill in the plot information
    for plotInfo in self.savedPlotCommands:
      if plotInfo:
        command, args, kwargs, timeInterval = plotInfo
        self.plotLabels[index].setText(args[2]+'->'+command)
        self.plotSpinBoxes[index].setValue(timeInterval)
      index += 1
    #select the correct fpga experiment
    self.ui.comboBoxFPGA.setCurrentIndex(sorted(fpga_scripts.experiment.keys()).index(self.fpgaScriptName)+1)
    #fill in the selected output files/folders
    if type(self.fpgaOutputLocation) is list:
      self.ui.labelFPGALocation.setText('\n'.join(self.fpgaOutputLocation))
    else:
      self.ui.labelFPGALocation.setText(self.fpgaOutputLocation)
    #adjust the checkbox state and fill in the label
    self.ui.checkBoxLogData.setChecked(len(self.logFile) > 0)
    self.ui.labelLocationSelected.setText(self.logFile)

      
  def doneClicked(self):
    '''Stores the current time intervals and then runs all the commands in self.savedCommands
    If all commands return True, the currrent window is closed and PlotWindow is open and fed
    the savedPlotCommands. If a saved command fails it is noted in the status bar and the user
    is told to fix/delete it before continuing.
    '''
    self.storeTimeIntervals()
    self.executeSavedCommands()
    if self.failedCommands:
      message = 'Command number ['+', '.join(self.failedCommands)+'] has failed. Please fix or delete it.'
      self.ui.statusbar.showMessage(message)
      self.failedCommands = []
    else:
      self.close()
      self.plotWindowApp = PlotWindow((self.savedPlotCommands, self.fpgaOutputLocation,
        self.fpgaScriptName, self.logFile))
      self.plotWindowApp.show()


  def selectFileClicked(self):
    fname = QtGui.QFileDialog.getOpenFileNames(self, 'Select FPGA Output File(s)',
        '/Users/jack/Documents/Senior Year/Senior Design/')
    self.fpgaOutputLocation = [str(x) for x in list(fname)]
    self.ui.labelFPGALocation.setText('\n'.join(self.fpgaOutputLocation))


  def selectFolderClicked(self):
    dirname = QtGui.QFileDialog.getExistingDirectory(self, 'Select FPGA Output Folder',
        '~/Documents')
    self.fpgaOutputLocation = str(dirname)
    self.ui.labelFPGALocation.setText(self.fpgaOutputLocation)


  def logClicked(self):
    fname = QtGui.QFileDialog.getSaveFileName(self, 'Select location to log experiment',
        '~/Documents/experiment.log') 
    self.logFile = str(fname)
    self.ui.labelLocationSelected.setText(self.logFile)
  


########################
#### MISC SLOTS
########################

  def deviceSelected(self):
    '''This method is called whenever a device is selected. It simply calls update commands
    '''
    self.showArgBoxes(0)
    deviceName = self.ui.listWidgetDevices.currentItem().text()
    self.updateCommands(deviceName)


  def commandSelected(self):
    '''This method updates the argument view to display the relevent textboxes and labels
    '''
    self.ui.pushButtonExecute.setEnabled(True)
    self.ui.pushButtonSave.setEnabled(True)
    commandName = str(self.ui.listWidgetCommands.currentItem().text())
    args = self.argDict[commandName].keys()
    values = self.argDict[commandName].values()
    numOfArgs = len(args)
    self.numOfArgs = numOfArgs #save it so other methods know how many args are displayed.
    
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


  def savedCommandSelected(self):
    self.ui.pushButtonDelete.setEnabled(True)


  def tabChanged(self, index):
    if index is 0:
      self.setOrGet = 'set'
      self.ui.listWidgetCommands.clear()
    if index is 1:
      self.setOrGet = 'get'
      self.ui.listWidgetCommands.clear()
    self.deviceSelected()


  def fpgaComboChanged(self, index):
    self.ui.pushButtonSaveExperiment.setEnabled(True)
    for plotIndex in range(len(self.plotButtons)):
      self.plotButtons[plotIndex].setEnabled(True)
      self.clearPlotButtons[plotIndex].setEnabled(True)
      if self.plotLabels[plotIndex].text() == 'FPGA Plot':
        self.plotLabels[plotIndex].setText('')
      self.plotSpinBoxes[plotIndex].setEnabled(True)

    if index is 0:
      self.fpgaScriptName = None
    else:
      self.fpgaScriptName = sorted(fpga_scripts.experiment.keys())[index-1]
      for plotIndex in fpga_scripts.experiment[self.fpgaScriptName][1]:
        self.plotButtons[plotIndex-1].setEnabled(False)
        self.plotLabels[plotIndex-1].setText('FPGA Plot')
        self.plotSpinBoxes[plotIndex-1].setEnabled(False)
        self.clearPlotButtons[plotIndex-1].setEnabled(False)


  def logDataClicked(self):
    self.ui.pushButtonSaveExperiment.setEnabled(True)
    if self.ui.checkBoxLogData.isChecked():
      self.ui.pushButtonLogLocation.setEnabled(True)
    else:
      self.ui.pushButtonLogLocation.setEnabled(False)
      self.ui.labelLocationSelected.setText('')
      self.logFile = ''


  def devicesFound(self):
    '''Slot that is called when the thread indicates it has found the attached devices
    '''
    self.ui.statusbar.showMessage('')
    self.ui.pushButtonFindDevices.setEnabled(True)
    self.ui.pushButtonFindDevices.setText('Find Devices')
    self.findArguments()
    self.updateDeviceList()
    self.ui.splitter_vert.setVisible(True)
    self.ui.splitter_top.setVisible(True)



##########################
#### HELPER METHODS
##########################

  def findArguments(self):
    '''This method searches through the commands folder and finds all the def __init__ lines
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


  def returnCurrentCommand(self):
    '''This method returns a tuple consisting of (command-name, args, kwargs) all of which are needed
    to instantiate a command object. To create a new command object with the return value of this
    method, do the following:

    command, args, kwargs = self.returnCurrentCommand()
    commandObject = gpib_commands.command[command](*args, **kwargs)

    To execute the command, call the .do() method on the commandObject, eg:
    commandObject.do()
    '''

    #biuld a dict of kwargs that consists of the extra arguments for any given command
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
    IP = self.IP
    device = str(self.ui.listWidgetDevices.currentItem().text())
    GPIB = self.GPIBlist[self.deviceList.index(device)]

    #update the commands arg dict so next time the most recently applied value is filled in
    self.argDict[command].update(kwargs)

    return command, [IP, GPIB, device], kwargs


  def executeSavedCommands(self):
    '''Called when the user clicks Start Experiment. It attempts to execute all saved commands
    '''
    for command, args, kwargs in self.savedCommands:
      commandObject = gpib_commands.command[command](*args, **kwargs)
      self.usedCommands.append(commandObject)
      result = self.usedCommands[-1].do()
      if not result[0]:
        self.failedCommands.append(str(self.savedCommands.index((command, args, kwargs))+1))


  def storeTimeIntervals(self):
    '''This method grabs the currently entered time intervals for each plot and saves them.
    '''
    for index in range(len(self.savedPlotCommands)):
      if self.savedPlotCommands[index]:
        timeInterval = self.plotSpinBoxes[index].value()
        if len(self.savedPlotCommands[index]) is 3:
          self.savedPlotCommands[index].append(timeInterval)
        else:
          self.savedPlotCommands[index][3] = timeInterval


  def findDevices(self, IP):
    '''Find the attached devices. This method is spawned in a thread
    '''
    self.deviceList, self.GPIBlist = getAttachedDevices.getAttachedDevices(IP, 30).do()
    #self.deviceList = ['DSO6032A', 'E3631A', '34401A']
    #self.GPIBlist = ['gpib0,07', 'gpib0,10', 'gpib0,22']
    self.emit(QtCore.SIGNAL('foundDevices()'))

  

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeviceControl()
  myapp.resize(250, 150)  
  myapp.move(300, 50)
  myapp.setWindowTitle("DeathRay - Device Control")
  myapp.show()
  sys.exit(app.exec_())

