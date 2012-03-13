#!/usr/bin/python -d
 
import sys, random, pprint

from PyQt4 import QtCore, QtGui, Qt
from interface import Ui_MainWindow
import PyQt4.Qwt5 as Qwt
import numpy as np

from FileProcessor2 import FileProcessor
from Histogram import HistogramItem
from ImagePlot import ImagePlot, square


from pdb import set_trace as bp #DEBUGING

 
class DeathRay(QtGui.QMainWindow):
  '''
  Main application class that contains the GUI control and helper methods.
  '''

  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self)
    self.ui = Ui_MainWindow()
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
    
    self.ui.qwtPlot_2.setHidden(True)
    self.ui.qwtPlot_3.setHidden(True)
    self.ui.qwtPlot_4.setHidden(True)

    #jump to this method while developing
    self.openFiles()

  def openFiles(self):
    '''
    This displays the open file dialog, feeds the selected files to the processor, and
    then plots the results
    '''
    fname = QtGui.QFileDialog.getOpenFileNames(self, 'Select FPGA Output File(s)',
        '/Users/jack/Documents/Senior Year/Senior Design/data/raw')
    self.filesList = [str(x) for x in list(fname)]
    self.Experiment = FileProcessor(self.filesList)
    #pp=pprint.PrettyPrinter()
    #pp.pprint(self.Experiment.processedData)
    self.updateRunDisplay()

    #Plot some stuffs
    self.plotLine(self.ui.qwtPlot_1, 0)
 
  def plotHistogram(self, plot, runIndex):
    '''
    This method displays a histogram using data from .processedData
    '''

    #if there is currently a histogram attached, remove it
    try:
      self.histogram.detach()
    except AttributeError:
      pass

    self.histogram = HistogramItem()
    self.histogram.setColor(Qt.Qt.darkGreen)


    try:
      maxBinValue = max(self.Experiment.processedData[runIndex]['pulsewidthList'])
    except ValueError:
      maxBinValue = 0
    #Add 1 so maxBinValue is included in the array
    binValue = np.arange(0,maxBinValue+1, 30)
    binCounts = np.zeros(len(binValue))
    for pulsewidth in self.Experiment.processedData[runIndex]['pulsewidthList']:
      binCounts[int(pulsewidth/30)] += 1


    numBins = len(binCounts)
    intervals = []
    binNumber = Qwt.QwtArrayDouble(numBins)

    pos = 0.0
    for i in range(numBins):
      width = 30
      binNumber[i] = binCounts[i]
      if pos > 0:
        intervals.append(Qwt.QwtDoubleInterval(pos-15, pos+width-15));
      else:
        intervals.append(Qwt.QwtDoubleInterval(pos, pos+width-15));
      pos += width

    self.histogram.setData(Qwt.QwtIntervalData(intervals, binNumber))
    self.histogram.attach(self.ui.qwtPlot_1)

    plot.setAxisScale(Qwt.QwtPlot.yLeft, 0.0, max(binNumber))
    plot.setAxisScale(Qwt.QwtPlot.xBottom, 0.0, pos, 30)
    plot.setAxisTitle(Qwt.QwtPlot.xBottom, self.Experiment.xAxis)
    plot.setAxisTitle(Qwt.QwtPlot.yLeft, self.Experiment.yAxis)
    plot.setTitle(self.Experiment.plotTitle)
    plot.replot()
    plot.show()

  def plotLine(self, plot, runIndex):

    plot.clear()
    y = self.Experiment.processedData[runIndex]['y-vector']
    x = self.Experiment.processedData[runIndex]['x-vector']
    curveType = self.Experiment.processedData[runIndex]['plotType']

    grid = Qwt.QwtPlotGrid()
    grid.setPen(Qt.QPen(Qt.Qt.gray, 0, Qt.Qt.DotLine))
    grid.attach(plot)

    curve = Qwt.QwtPlotCurve()
    curve.setPen(Qt.QPen(Qt.Qt.red))
    curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
    curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                      Qt.QBrush(),
                                      Qt.QPen(Qt.Qt.black),
                                      Qt.QSize(5, 5)))
    if curveType == 'spline':
      curve.setCurveAttribute(Qwt.QwtPlotCurve.Fitted)

    if curveType == 'step':
      curve.setStyle(Qwt.QwtPlotCurve.Steps)

    if curveType == 'sticks':
      curve.setStyle(Qwt.QwtPlotCurve.Sticks)

    if curveType == 'scatter':
      curve.setStyle(Qwt.QwtPlotCurve.NoCurve)
      curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Cross,
                                      Qt.QBrush(),
                                      Qt.QPen(Qt.Qt.red),
                                      Qt.QSize(5, 5)))
    curve.setData(x,y)
    curve.attach(plot)

    self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        plot.canvas())
    self.zoomer.setRubberBandPen(Qt.QPen(Qt.Qt.green))

    plot.setAxisTitle(Qwt.QwtPlot.xBottom, self.Experiment.processedData[runIndex]['x-axis'])
    plot.setAxisTitle(Qwt.QwtPlot.yLeft, self.Experiment.processedData[runIndex]['y-axis'])

    plot.replot()


  def plotHeatMap(self, plot, runIndex):
    plotImage = ImagePlot('Heatmap')
    plotImage.attach(plot)
    plotImage.setData(square(512, -2*np.pi, 2*np.pi), (-2*np.pi, 2*np.pi), (-2*np.pi, 2*np.pi))
    
    self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        plot.canvas())
    self.zoomer.setRubberBandPen(Qt.QPen(Qt.Qt.green))




  ####################
  #GUI Control Methods
  ####################

  def updateRunDisplay(self):
    '''
    This method updates the display widget to show a list of all the runs of the
    current experiment.
    
    The data in FileProcessor.displayData is used for the treeWidget
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
      
    #Set 'All Runs' as the selected item
    #allRunsItem = self.ui.treeRun.findItems(self.Experiment.displayData[0],QtCore.Qt.MatchExactly)[0]
    #self.ui.treeRun.setItemSelected(allRunsItem, True)

  def updateDataTable(self, index):
    '''
    This method updates the table widget with the data stored in FileProcessor.tableData
    '''
    currentTableData = self.Experiment.tableData[index]
    self.ui.tableWidgetData.clear()
    self.ui.tableWidgetData.setRowCount(max(len(x) for x in currentTableData))
    self.ui.tableWidgetData.setColumnCount(len(currentTableData[0]))
    self.ui.tableWidgetData.setHorizontalHeaderLabels(currentTableData[0])
    for c in range(len(currentTableData)-1):
      for r in range(len(currentTableData[c+1])):
        print c, ',', r
        tableItem = QtGui.QTableWidgetItem(str(currentTableData[c+1][r]))
        tableItem.setTextAlignment(2)
        self.ui.tableWidgetData.setItem(r, c, tableItem)
      self.ui.tableWidgetData.resizeColumnToContents(c)
    #self.ui.tableWidgetData.setSortingEnabled(True)


  def runClicked(self):
    index = self.ui.treeRun.indexFromItem(self.ui.treeRun.selectedItems()[0]).row()
    self.plotLine(self.ui.qwtPlot_1, index)
    self.updateDataTable(index)

  def setPlotNumber(self, number):
    self.ui.qwtPlot_1.setVisible(number > 0)
    self.ui.qwtPlot_2.setVisible(number > 1)
    self.ui.qwtPlot_3.setVisible(number > 2)
    self.ui.qwtPlot_4.setVisible(number > 3)


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeathRay()
  myapp.show()
  sys.exit(app.exec_())

