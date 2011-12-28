#!/usr/bin/python -d
 
import sys, random, pprint
from PyQt4 import QtCore, QtGui, Qt
from interface import Ui_MainWindow
import PyQt4.Qwt5 as Qwt

from FileProcessor import FileProcessor
from Histogram import HistogramItem

 
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
    self.connect(self.ui.treeRun, QtCore.SIGNAL('itemSelectionChanged()'), self.runClicked)

    #Set initial sizes
    self.ui.splitter.setSizes([250, 600])

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
    self.ProcessedData = FileProcessor(self.filesList)
    pp=pprint.PrettyPrinter()
    pp.pprint(self.ProcessedData.processedData)
    self.updateRunDisplay()
    self.plotHistogram(0)

 
  def plotHistogram(self, runIndex):
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


    numBins = len(self.ProcessedData.processedData[runIndex]['binCounts'])
    intervals = []
    binNumber = Qwt.QwtArrayDouble(numBins)

    pos = 0.0
    for i in range(numBins):
      width = 30
      binNumber[i] = self.ProcessedData.processedData[runIndex]['binCounts'][i]
      if pos > 0:
        intervals.append(Qwt.QwtDoubleInterval(pos-15, pos+width-15));
      else:
        intervals.append(Qwt.QwtDoubleInterval(pos, pos+width-15));
      pos += width

    self.histogram.setData(Qwt.QwtIntervalData(intervals, binNumber))
    self.histogram.attach(self.ui.qwtPlot)

    self.ui.qwtPlot.setAxisScale(Qwt.QwtPlot.yLeft, 0.0, max(binNumber))
    self.ui.qwtPlot.setAxisScale(Qwt.QwtPlot.xBottom, 0.0, pos, 30)
    self.ui.qwtPlot.setAxisTitle(Qwt.QwtPlot.xBottom, self.ProcessedData.xAxis)
    self.ui.qwtPlot.setAxisTitle(Qwt.QwtPlot.yLeft, self.ProcessedData.yAxis)
    self.ui.qwtPlot.setTitle(self.ProcessedData.plotTitle)
    self.ui.qwtPlot.replot()
    self.ui.qwtPlot.show()


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

    print self.ProcessedData.displayData
    for run in self.ProcessedData.displayData:
      treeItem = QtGui.QTreeWidgetItem(self.ui.treeRun)
      treeItem.setText(0, run[0])

      for subItemIndex in range(len(run)-1):
        child = QtGui.QTreeWidgetItem(treeItem)
        child.setText(0, run[subItemIndex+1])
        treeItem.insertChild(0, child)
        child.setDisabled(True)
      
    #Set 'All Runs' as the selected item
    allRunsItem = self.ui.treeRun.findItems('All Runs',QtCore.Qt.MatchExactly)[0]
    self.ui.treeRun.setItemSelected(allRunsItem, True)

  def runClicked(self):
    index = self.ui.treeRun.indexFromItem(self.ui.treeRun.selectedItems()[0]).row()
    self.plotHistogram(index)
      


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeathRay()
  myapp.show()
  sys.exit(app.exec_())

