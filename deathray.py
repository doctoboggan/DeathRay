#! /usr/bin/env python

from PyQt4 import QtGui
import sys
from PlotWindow import PlotWindow
from DeviceControl import DeviceControl

app = QtGui.QApplication(sys.argv)
appPlot = PlotWindow()
appPlot.show()
#sys.exit(app.exec_())

app2 = QtGui.QApplication(sys.argv)
myapp = DeviceControl()
myapp.resize(250, 150)  
myapp.move(300, 50)
myapp.show()
sys.exit(app2.exec_())

