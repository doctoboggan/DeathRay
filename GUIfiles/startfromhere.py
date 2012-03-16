#!/user/bin/env python

# I face some issues with picutres...

from PyQt4 import QtCore, QtGui
from GUIfiles import aboutwindow, welcomewindow  #add new windows here

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = welcomewindow  .Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

