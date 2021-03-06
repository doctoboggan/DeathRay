#!/usr/bin/python -d
 
import sys, os, glob, time

from PyQt4 import QtCore, QtGui, Qt
from interfaces import interface
import PyQt4.Qwt5 as Qwt
import numpy as np

import fpga_scripts, gpib_commands
from utils import Thread

 
class PlotWindow(QtGui.QMainWindow):
  '''This class represents the plot window. It contains all the methods used to plot and
  display all the data
  '''

  def __init__(self, inputData=None, parent=None):
    QtGui.QWidget.__init__(self)
    (self.deviceControlWindow, self.savedPlotCommands, self.fpgaOutput, 
        self.fpgaScriptName, self.logFilePath) = inputData
    self.ui = interface.Ui_MainWindow()
    self.ui.setupUi(self)
    
    #set the correct number of plots visible
    self.plotsUsed=0
    if self.savedPlotCommands[0]:
      self.plotsUsed=1
    if self.savedPlotCommands[1]:
      self.plotsUsed=2
    if self.savedPlotCommands[2]:
      self.plotsUsed=3
    if self.savedPlotCommands[3]:
      self.plotsUsed=4
    self.setPlotNumber(self.plotsUsed) 

    #If a script is selected, initialize the experiment and resize windows
    if self.fpgaScriptName:
      self.Experiment = fpga_scripts.experiment[self.fpgaScriptName][0].FileProcessor()
      self.ui.splitter.setSizes([150, 500, 150])
      #start the file watcher
      self.fileWatcher = QtCore.QFileSystemWatcher(self)
      self.startFileWatcher()
      self.connect(self.fileWatcher, QtCore.SIGNAL('fileChanged(QString)'), self.fileChanged)
      self.connect(self.fileWatcher, QtCore.SIGNAL('directoryChanged(QString)'), self.directoryChanged)
    else:
      self.ui.splitter.setSizes([0, 500, 0])

    #if a logfile is specified, open it for writing
    if self.logFilePath:
      self.logFile = open(self.logFilePath, 'w')
      self.logFile.write('Unix Time, Measurement, Command, Device, GPIB-ID\n')

    #instance variables
    self.plottingThreads = []
    self.keepPlotting = True
    self.deviceValues = [[],[],[],[]]
    self.deviceTimes = [[],[],[],[]]
    self.plots = [self.ui.qwtPlot_1, self.ui.qwtPlot_2, self.ui.qwtPlot_3, self.ui.qwtPlot_4]
    self.dataLogged = False
    self.savedLogLines = []
    self.displayLabels = [None, None, None, None]
    self.scrollAreas = [None, None, None, None]
    self.dataTables = [None, None, None, None]

    #spawn the threads that communicate with devices.
    self.spawnThreads()

    self.initUI()

    #run this immediately to see if the directory already has some files in it
    if self.fpgaScriptName:
      self.fileChanged()

  def initUI(self):
    #Connect the signals and slots
    self.connect(self.ui.actionOne_Plot, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(1))
    self.connect(self.ui.actionTwo_Plots, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(2)) 
    self.connect(self.ui.actionThree_Plots, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(3)) 
    self.connect(self.ui.actionFour_Plots, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(4))
    self.connect(self.ui.treeRun, QtCore.SIGNAL('itemSelectionChanged()'), self.runClicked)
    self.connect(self.ui.pushButtonBack, QtCore.SIGNAL('clicked()'), self.backClicked)
    self.connect(self.ui.pushButtonLog, QtCore.SIGNAL('clicked()'), self.logClicked)
    self.connect(self.ui.pushButtonStopStart, QtCore.SIGNAL('clicked()'), self.stopStartClicked)
    self.connect(self, QtCore.SIGNAL('newData0(QString)'), lambda x: self.newDataDetected(x, 0))
    self.connect(self, QtCore.SIGNAL('newData1(QString)'), lambda x: self.newDataDetected(x, 1))
    self.connect(self, QtCore.SIGNAL('newData2(QString)'), lambda x: self.newDataDetected(x, 2))
    self.connect(self, QtCore.SIGNAL('newData3(QString)'), lambda x: self.newDataDetected(x, 3))


  #############
  #Button Methods
  #############

  def runClicked(self):
    '''This method is called whenever an item is clicked on the tree widget
    '''
    self.updatePlots()
    self.updateDataTable()


  def backClicked(self):
    '''Closes PlotWindows and reopens DeviceControl. Only enabled when an experiment has been stopped.
    Also warns users if data is not logged.
    '''
    self.deviceControlWindow.show()


  def logClicked(self):
    fname = QtGui.QFileDialog.getSaveFileName(self, 'Select location to log experiment',
        '~/Documents/experiment.log') 
    logFile = open(str(fname), 'w')
    logFile.write('Unix Time, Measurement, Command, Device, GPIB-ID\n')
    logFile.writelines(self.savedLogLines)
    logFile.close()
    self.dataLogged = True



  def stopStartClicked(self):
    stopOrStart = str(self.ui.pushButtonStopStart.text())
    if 'Stop' in stopOrStart:
      self.ui.pushButtonStopStart.setText('Start Experiment')
      if not self.logFilePath:
        self.ui.pushButtonLog.setEnabled(True)
      self.keepPlotting = False
      self.ui.statusbar.showMessage('')
      if self.logFilePath:
        self.logFile.close()
    if 'Start' in stopOrStart:
      if self.logFilePath:
        self.logFile = open(self.logFilePath, 'a')
      self.ui.pushButtonStopStart.setText('Stop Experiment')
      self.ui.pushButtonLog.setEnabled(False)
      self.keepPlotting = True
      self.spawnThreads()
      self.dataLogged = False



  #############
  #Slot Methods
  #############

  def fileChanged(self):
    '''Called when the fileWatcher detects a change in any file it is watching
    It is responsible for calling self.Experiment's .load() method with the required files
    '''
    try:#if there is a currently selected item, try to save it
      currentItem = self.ui.treeRun.selectedItems()[0]
      currentItemText = currentItem.text(0)
    except:
      pass
    if type(self.fpgaOutput) is list: #user selected one or more files directly
      self.Experiment.load(self.fpgaOutput)
      self.updateRunDisplay()
      self.updatePlots()
      self.updateDataTable()
    else: #user selected a folder to watch
      if len(glob.glob(os.path.join(self.fpgaOutput, '*'))) > 0: #if there are files in the folder
        filesList = glob.glob(os.path.join(self.fpgaOutput, '*'))
        self.Experiment.load(filesList)
        self.updateRunDisplay()
        self.updatePlots()
        self.updateDataTable()
    try:#try to reselect the currently selected item from above
      foundItem = self.ui.treeRun.findItems(currentItemText,QtCore.Qt.MatchExactly)[0]
      self.ui.treeRun.setCurrentItem(foundItem)
    except:
      pass
    

  def directoryChanged(self):
    '''Whenever the file watcher notices a change in the parent dir this is called
    It is responsible for adding any new files to the path of the filewatcher
    '''
    if type(self.fpgaOutput) is str:
      filesList = glob.glob(os.path.join(self.fpgaOutput, '*'))
      self.fileWatcher.addPaths(filesList)
      self.Experiment.load(filesList)
    else:
      filesList = glob.glob(os.path.join(os.path.dirname(self.fpgaOutput[0]), '*'))
      self.fileWatcher.addPaths(filesList)
      self.Experiment.load(filesList)




  def newDataDetected(self, data, index):
    '''When new data is ready in any of the threads, this method is called
    '''
    #get time since the epoch. use time.gmtime() to get this in a human readable format
    currentTime = time.time()
    try:#if the data converts to a float, we append it to our vector for plotting
      floatValue = float(data)
      self.deviceTimes[index].append(currentTime)
      self.deviceValues[index].append(floatValue)
      xVector = np.array(self.deviceTimes[index][-50:])
      yVector = np.array(self.deviceValues[index][-50:])
      plotData = [{
          'x-vector': xVector - self.deviceTimes[index][0],
          'y-vector': yVector,
          'plotType': 'lines',
          'x-axis': 'Time (s)',
          'y-axis': self.savedPlotCommands[index][0]+' - '+self.savedPlotCommands[index][1][2]
          }]
      self.plotLine(self.plots[index], plotData, 0, autoScale=False)
      self.ui.statusbar.showMessage('')
    except ValueError:#The returned value couldn't be converted to a float
      if not self.deviceTimes[index]:
        self.deviceValues[index].append(str(data))
        if not self.dataTables[index]: #a table has not been created here yet

          #Make the tables to hold the non-floatable data
          self.dataTables[index] = QtGui.QTableWidget(1,4)
          self.dataTables[index].setHorizontalHeaderLabels(['Unix Time','Device','Command','Data'])
          if index is 0:
            self.ui.qwtPlot_1.setVisible(False)
            self.ui.splitter_top.insertWidget(0, self.dataTables[index])
          if index is 1:
            self.ui.qwtPlot_2.setVisible(False)
            self.ui.splitter_top.insertWidget(1, self.dataTables[index])
          if index is 2:
            self.ui.qwtPlot_3.setVisible(False)
            self.ui.splitter_bottom.insertWidget(0, self.dataTables[index])
          if index is 3:
            self.ui.qwtPlot_4.setVisible(False)
            self.ui.splitter_bottom.insertWidget(1, self.dataTables[index])
        #Make both the tables items (time and data)
        tableItemTime = QtGui.QTableWidgetItem(str(currentTime))
        tableItemCommand = QtGui.QTableWidgetItem(self.savedPlotCommands[index][0])
        tableItemDevice = QtGui.QTableWidgetItem(self.savedPlotCommands[index][1][2])
        tableItemData = QtGui.QTableWidgetItem(str(data))
        rows = len(self.deviceValues[index])
        self.dataTables[index].setRowCount(rows)
        self.dataTables[index].setItem(rows-1, 0, tableItemTime)
        self.dataTables[index].setItem(rows-1, 1, tableItemDevice)
        self.dataTables[index].setItem(rows-1, 2, tableItemCommand)
        self.dataTables[index].setItem(rows-1, 3, tableItemData)
        self.dataTables[index].resizeColumnToContents(0)
        self.dataTables[index].resizeColumnToContents(1)
    else:
      self.ui.statusbar.showMessage('Failed to convert return falue to float: '+str(data)+' '+str(index))

    print 'detected: ', data, index

    #if a logfile is selected, we write a logline, otherwise, save it so we may write it later
    command, args, kwargs, timeInterval = self.savedPlotCommands[index]
    line = ', '.join([str(currentTime), str(data).strip(), str(command), str(args[2]), str(args[1])])
    if self.logFilePath:
      self.logFile.write(line+'\n')
      self.logFile.flush()
    else:
      self.savedLogLines.append(line+'\n')
 
  

  ####################
  #GUI Control Methods
  ####################

  def updateRunDisplay(self):
    '''This method updates the display widget to show a list of all the runs of the
    current experiment.
    
    The data in Experiment.displayData is used for the treeWidget
    '''
    self.ui.treeRun.clear()
    for run in self.Experiment.displayData:
      treeItem = QtGui.QTreeWidgetItem(self.ui.treeRun)
      treeItem.setText(0, run[0])
      for subItemIndex in range(len(run)-1):
        child = QtGui.QTreeWidgetItem(treeItem)
        child.setText(0, run[subItemIndex+1])
        treeItem.insertChild(0, child)
        child.setDisabled(True)
    #Set the first element as the selected item
    firstItem = self.ui.treeRun.findItems(self.Experiment.displayData[0][0],QtCore.Qt.MatchExactly)[0]
    self.ui.treeRun.setItemSelected(firstItem, True)


  def updatePlots(self):
    '''Draws the data stored in processedData using the plotLine method
    '''
    index = self.ui.treeRun.indexFromItem(self.ui.treeRun.selectedItems()[0]).row()
    if hasattr(self.Experiment, 'processedData'):
      self.plotLine(self.ui.qwtPlot_1, self.Experiment.processedData, index)
      plotsUsed = 1
    if hasattr(self.Experiment, 'processedData2'):
      self.plotLine(self.ui.qwtPlot_2, self.Experiment.processedData2, index)
      plotsUsed = 1
    if hasattr(self.Experiment, 'processedData3'):
      self.plotLine(self.ui.qwtPlot_3, self.Experiment.processedData3, index)
      plotsUsed = 1
    if hasattr(self.Experiment, 'processedData4'):
      self.plotLine(self.ui.qwtPlot_4, self.Experiment.processedData4, index)
      plotsUsed = 1
    self.setPlotNumber(max(plotsUsed, self.plotsUsed))


  def updateDataTable(self):
    '''This method updates the table widget with the data stored in Experiment.tableData
    '''
    index = self.ui.treeRun.indexFromItem(self.ui.treeRun.selectedItems()[0]).row()
    currentTableData = self.Experiment.tableData[index]
    self.ui.tableWidgetData.clear()
    self.ui.tableWidgetData.setRowCount(max(len(x) for x in currentTableData))
    self.ui.tableWidgetData.setColumnCount(len(currentTableData[0]))
    self.ui.tableWidgetData.setHorizontalHeaderLabels(currentTableData[0])
    for c in range(len(currentTableData)-1):
      for r in range(len(currentTableData[c+1])):
        tableItem = QtGui.QTableWidgetItem(str(currentTableData[c+1][r]))
        tableItem.setTextAlignment(2)
        self.ui.tableWidgetData.setItem(r, c, tableItem)
      self.ui.tableWidgetData.resizeColumnToContents(c)
    #Sorting is buggy, enable with caution.
    #self.ui.tableWidgetData.setSortingEnabled(True)


  def setPlotNumber(self, number):
    '''This function sets the number of plots visible
    '''

    self.ui.qwtPlot_1.setVisible(False)
    self.ui.qwtPlot_2.setVisible(False)
    self.ui.qwtPlot_3.setVisible(False)
    self.ui.qwtPlot_4.setVisible(False)

    self.ui.qwtPlot_1.setVisible(number > 0)
    self.ui.qwtPlot_2.setVisible(number > 1)
    self.ui.qwtPlot_3.setVisible(number > 2)
    self.ui.qwtPlot_4.setVisible(number > 3)



  ###############
  #Helper Methods
  ###############

  def startFileWatcher(self):
    '''Starts the QFileWatcher on either the file or files selected.
    '''
    if type(self.fpgaOutput) is list: #This means the user selected one or more files
      self.fileWatcher.addPaths(self.fpgaOutput)
      self.fileWatcher.addPath(os.path.dirname(self.fpgaOutput[0]))
      self.Experiment.load(self.fpgaOutput)
      self.updateRunDisplay()
      #Plot the first element in self.processedData
      self.updatePlots()
      self.updateDataTable()
    elif type(self.fpgaOutput) is str: #this means the user selected a directory
      self.fileWatcher.addPath(self.fpgaOutput)#add the dir
      filesList = glob.glob(os.path.join(self.fpgaOutput, '*'))
      self.fileWatcher.addPaths(filesList)


  def spawnThreads(self, indexes=[0,1,2,3]):
    '''Spawns a new thread for each plotting command selected by the user.
    '''
    for index in indexes:
      if self.savedPlotCommands[index]:
        #sleep between spawning threads or else the device may be overloaded with requests
        time.sleep(.5)
        print 'spawning thread ', index
        thread = Thread.Thread(self.deviceHandler, self.savedPlotCommands[index], index) 
        thread.start()
        #store a reference so the thread isn't garbage collected.
        self.plottingThreads.append(thread)


  def deviceHandler(self, plotCommand, plotNumber):
    '''This method is spawned inside a thread. It polls the device according to the
    time interval
    '''
    command, args, kwargs, timeInterval = plotCommand
    while self.keepPlotting:
      try:
        commandObject = gpib_commands.command[command](*args, **kwargs)
        while self.keepPlotting:
          result = commandObject.do()
          self.emit(QtCore.SIGNAL('newData'+str(plotNumber)+'(QString)'), str(result))
          time.sleep(timeInterval)
      except:
        print 'thread ', str(plotNumber), ' crashed'
        time.sleep(1)


  def plotLine(self, plot, processedData, index, autoScale=True):
    '''This method is used to plot and replot all the data.
    It has the ability to allow the caller to select which plot to draw to.
    The index is used to index into processedData. It is supplied by the runClicked method

    Qwt is quite powerful and able to provide many types of plots.
    To add some more, modify this method. Qwt documentation and examples can be found online
    '''
    plot.clear() #Clear the previous plot
    #grab the data and plotType from the file processor script
    y = processedData[index]['y-vector']
    x = processedData[index]['x-vector']
    curveType = processedData[index]['plotType']

    #Add a grid
    grid = Qwt.QwtPlotGrid()
    grid.setPen(Qt.QPen(Qt.Qt.gray, 0.1, Qt.Qt.DotLine))
    grid.attach(plot)

    #instantiate a curve and set some properties
    curve = Qwt.QwtPlotCurve()
    curve.setPen(Qt.QPen(Qt.Qt.red))
    curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)

    if curveType == 'spline':
      curve.setCurveAttribute(Qwt.QwtPlotCurve.Fitted)
      curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                  Qt.QBrush(),
                                  Qt.QPen(Qt.Qt.black),
                                  Qt.QSize(5, 5)))

    if curveType == 'step':
      curve.setStyle(Qwt.QwtPlotCurve.Steps)

    if curveType == 'lines':
      curve.setStyle(Qwt.QwtPlotCurve.Lines)      
      curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                  Qt.QBrush(),
                                  Qt.QPen(Qt.Qt.black),
                                  Qt.QSize(5, 5)))

    if curveType == 'sticks':
      curve.setPen(Qt.QPen(Qt.Qt.darkGreen, 6))    
      curve.setStyle(Qwt.QwtPlotCurve.Sticks)
      curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                  Qt.QBrush(),
                                  Qt.QPen(Qt.Qt.black),
                                  Qt.QSize(5, 5)))

    if curveType == 'scatter':
      curve.setStyle(Qwt.QwtPlotCurve.NoCurve)
      curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Cross,
                                      Qt.QBrush(),
                                      Qt.QPen(Qt.Qt.red),
                                      Qt.QSize(5, 5)))
    
    #Set the data and attach the plot
    curve.setData(np.array(x),np.array(y))
    curve.attach(plot)

    #allow the user to select and zoom in on sections (right-click to recenter)
    #buggy - enable with caution
    #self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
    #                                    Qwt.QwtPlot.yLeft,
    #                                    Qwt.QwtPicker.DragSelection,
    #                                    Qwt.QwtPicker.AlwaysOff,
    #                                    plot.canvas())
    #self.zoomer.setRubberBandPen(Qt.QPen(Qt.Qt.green))

    plot.setAxisTitle(Qwt.QwtPlot.xBottom, processedData[index]['x-axis'])
    plot.setAxisTitle(Qwt.QwtPlot.yLeft, processedData[index]['y-axis'])
    if not autoScale:
      top = max(y)+0.1*max(y)
      bottom = min(y) + 0.1*min(y)
      plot.setAxisScale(Qwt.QwtPlot.yLeft, min(0, top, bottom), max(0, top, bottom))
    else:
      plot.setAxisAutoScale(Qwt.QwtPlot.yLeft)

    plot.replot()


#This is here so the file can be run on its own. The file should not be run on its own
if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = PlotWindow()
  myapp.show()
  sys.exit(app.exec_())

