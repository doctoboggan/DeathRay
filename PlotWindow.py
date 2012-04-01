#!/usr/bin/python -d
 
import sys

from PyQt4 import QtCore, QtGui, Qt
from GUIfiles import interface
import PyQt4.Qwt5 as Qwt
import numpy as np

import fpga_scripts


from pdb import set_trace as bp #DEBUGING

 
class PlotWindow(QtGui.QMainWindow):
  '''Main application class that contains the GUI control and helper methods.
  '''

  def __init__(self, devicePlotCommands=None, parent=None):
    QtGui.QWidget.__init__(self)
    self.devicePlotCommands = devicePlotCommands
    print 'input: ', devicePlotCommands
    self.ui = interface.Ui_MainWindow()
    self.ui.setupUi(self)
    self.initUI()
    
  def initUI(self):
    #Connect the signals and slots
    self.connect(self.ui.actionOpen, QtCore.SIGNAL('triggered()'), self.openFiles)
    self.connect(self.ui.actionOne_Plot, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(1))
    self.connect(self.ui.actionTwo_Plots, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(2)) 
    self.connect(self.ui.actionThree_Plots, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(3)) 
    self.connect(self.ui.actionFour_Plots, QtCore.SIGNAL('triggered()'), lambda: self.setPlotNumber(4))
    self.connect(self.ui.treeRun, QtCore.SIGNAL('itemSelectionChanged()'), self.runClicked)

    #Set initial sizes
    self.ui.splitter.setSizes([150, 500, 150])
    
    #start off with no plots visible
    self.setPlotNumber(0)


    #jump to this method while developing
    self.openFiles()

  def openFiles(self):
    '''This displays the open file dialog, feeds the selected files to the processor, and
    then plots the results
    '''
    fname = QtGui.QFileDialog.getOpenFileNames(self, 'Select FPGA Output File(s)',
        '/Users/jack/Documents/Senior Year/Senior Design/data/raw')
    self.filesList = [str(x) for x in list(fname)]
    self.Experiment = fpga_scripts.experiment['register_error'].FileProcessor(self.filesList)
    self.updateRunDisplay()

    #Plot the first element in self.processedData
    self.updatePlots(0)


 
  def plotLine(self, plot, processedData, index):
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
    self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        plot.canvas())
    self.zoomer.setRubberBandPen(Qt.QPen(Qt.Qt.green))

    plot.setAxisTitle(Qwt.QwtPlot.xBottom, processedData[index]['x-axis'])
    plot.setAxisTitle(Qwt.QwtPlot.yLeft, processedData[index]['y-axis'])

    plot.replot()


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


  def updatePlots(self, index):
    if hasattr(self.Experiment, 'processedData'):
      self.plotLine(self.ui.qwtPlot_1, self.Experiment.processedData, index)
      self.setPlotNumber(1)
    if hasattr(self.Experiment, 'processedData2'):
      self.plotLine(self.ui.qwtPlot_1, self.Experiment.processedData2, index)
      self.setPlotNumber(2)
    if hasattr(self.Experiment, 'processedData3'):
      self.plotLine(self.ui.qwtPlot_1, self.Experiment.processedData3, index)
      self.setPlotNumber(3)
    if hasattr(self.Experiment, 'processedData4'):
      self.plotLine(self.ui.qwtPlot_1, self.Experiment.processedData4, index)
      self.setPlotNumber(4)


  def updateDataTable(self, index):
    '''This method updates the table widget with the data stored in Experiment.tableData
    '''
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


  def runClicked(self):
    '''This method is called whenever an item is clicked on the tree widget
    '''
    index = self.ui.treeRun.indexFromItem(self.ui.treeRun.selectedItems()[0]).row()
    self.updatePlots(index)
    self.updateDataTable(index)

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


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = PlotWindow()
  myapp.show()
  sys.exit(app.exec_())

