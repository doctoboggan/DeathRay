# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutwindow.ui'
#
# Created: Fri Mar 16 03:35:34 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AboutWindow(object):
    def setupUi(self, AboutWindow):
        AboutWindow.setObjectName(_fromUtf8("AboutWindow"))
        AboutWindow.resize(400, 300)
        AboutWindow.setWindowTitle(QtGui.QApplication.translate("AboutWindow", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.namelabel = QtGui.QLabel(AboutWindow)
        self.namelabel.setGeometry(QtCore.QRect(120, 30, 171, 91))
        font = QtGui.QFont()
        font.setPointSize(27)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.namelabel.setFont(font)
        self.namelabel.setText(QtGui.QApplication.translate("AboutWindow", "<html><head/><body><p>DeathRay</p><p>____________</p><p><br/></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.namelabel.setTextFormat(QtCore.Qt.AutoText)
        self.namelabel.setScaledContents(True)
        self.namelabel.setWordWrap(True)
        self.namelabel.setObjectName(_fromUtf8("namelabel"))
        self.Infolabel = QtGui.QLabel(AboutWindow)
        self.Infolabel.setGeometry(QtCore.QRect(80, 150, 251, 81))
        self.Infolabel.setText(QtGui.QApplication.translate("AboutWindow", "It is dsksgkejdsg", None, QtGui.QApplication.UnicodeUTF8))
        self.Infolabel.setObjectName(_fromUtf8("Infolabel"))

        self.retranslateUi(AboutWindow)
        QtCore.QMetaObject.connectSlotsByName(AboutWindow)

    def retranslateUi(self, AboutWindow):
        pass


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    AboutWindow = QtGui.QWidget()
    ui = Ui_AboutWindow()
    ui.setupUi(AboutWindow)
    AboutWindow.show()
    sys.exit(app.exec_())

