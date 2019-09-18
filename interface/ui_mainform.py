# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/msdvyv/AppData/Local/Temp/tmp80027/mainform.ui'
#
# Created: Tue Nov 06 15:42:06 2018
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

# from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
#         QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
#         QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
#         QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
#         QMainWindow, QAction, QVBoxLayout, QWidget)
# from PyQt5.QtGui import QIcon


from PyQt5 import QtGui, QtWidgets, QtCore
from ui_tabs import TabsWidget

class Ui_MainForm(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()

        self.initUI()

        self.mytabs = TabsWidget(self)
        self.setCentralWidget( self.mytabs  )

        self.show()

    def initUI(self):
        
        self.setWindowTitle('ORACode')
        # self.setGeometry(10, 100, 800, 600)
        self.resize(800, 600)
        
        self.statusBar().showMessage('to be filled up')
        
        # creat mainMenu
        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('File')
        self._setFileMenu()

        
    def _setFileMenu(self):
       
        # Exit application Button
        exitButton = QtWidgets.QAction( QtGui.QIcon('exit.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)        
        self.fileMenu.addAction(exitButton)


        





    


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    ex = Ui_MainForm()
    sys.exit(app.exec_()) 