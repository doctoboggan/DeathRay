#!/usr/bin/python -d
 
import sys
from PyQt4 import QtCore, QtGui
from interface import Ui_MainWindow
 
class DeathRay(QtGui.QMainWindow):

  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.initUI()
    
  def initUI(self):
    self.connect(self.ui.actionOpen, QtCore.SIGNAL('triggered()'), self.openDialog)

  def openDialog(self):
    fname = QtGui.QFileDialog.getOpenFileNames(self, 'Open file', '/Users/jack')
    self.filesList = [str(x) for x in list(fname)]
    self.loadFiles()

  def loadFiles(self):
    for filename in self.filesList

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = DeathRay()
  myapp.show()
  sys.exit(app.exec_())

