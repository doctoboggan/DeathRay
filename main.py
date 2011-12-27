#!/usr/bin/python -d
 
import sys, random, pprint
from PyQt4 import QtCore, QtGui
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


  def openFiles(self):
    '''
    This displays the open file dialog, feeds the selected files to the processor, and
    then plots the results
    '''
    fname = QtGui.QFileDialog.getOpenFileNames(self, 'Open file(s)',
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

    numBins = len(self.ProcessedData.processedData[runIndex]['binCounts'])
    intervals = []
    inters = []
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
    self.ui.qwtPlot.setAxisScale(Qwt.QwtPlot.xBottom, 0.0, pos)
    self.ui.qwtPlot.replot()
    self.ui.qwtPlot.show()


  ####################
  #GUI Control Methods
  ####################

  def updateRunDisplay(self):
    '''
    This method updates the display widget to show a list of all the runs of the
    current experiment. This has experiment specific code that should be moved to
    FileProcessor.
    '''
    for run in self.ProcessedData.processedData:
      treeItem = QtGui.QTreeWidgetItem(self.ui.treeRun)
      treeItem.setText(0, run['filename'])

      if run['Decoder'] != '':
        childDecoder = QtGui.QTreeWidgetItem(treeItem)
        childDecoder.setText(0, 'Decoder: ' + run['Decoder'])
        treeItem.insertChild(0, childDecoder)
      
      if run['AutoMea'] != '':
        childAutoMea = QtGui.QTreeWidgetItem(treeItem)
        childAutoMea.setText(0, 'AutoMea: ' + run['AutoMea'])
        treeItem.insertChild(0, childAutoMea)
      
      if run['dataCount'] != 0:
        childDataCount = QtGui.QTreeWidgetItem(treeItem)
        childDataCount.setText(0, 'Data points: ' + str(run['dataCount']))
        treeItem.insertChild(0, childDataCount)

      if run['invalidString'] != []:
        childInvalidString = QtGui.QTreeWidgetItem(treeItem)
        childInvalidString.setText(0, 'Invalid lines: ' + str(run['invalidString']))
        treeItem.insertChild(0, childInvalidString)

      if run['doublePulse'] != []:
        childDoublePulse = QtGui.QTreeWidgetItem(treeItem)
        childDoublePulse.setText(0, 'Double pulse lines: ' + str(run['doublePulse']))
        treeItem.insertChild(0, childDoublePulse)
    #self.ui.treeRun.setItemSelected(self.ui.treeRun.itemFromIndex(0))

  def runClicked(self):
    index = self.ui.treeRun.indexFromItem(self.ui.treeRun.selectedItems()[0]).row()
    self.plotHistogram(index)
      


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeathRay()
  myapp.show()
  sys.exit(app.exec_())

