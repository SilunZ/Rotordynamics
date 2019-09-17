# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/msdvyv/AppData/Local/Temp/tmp80027/mainform.ui'
#
# Created: Tue Nov 06 15:42:06 2018
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class Ui_MainForm(QMainWindow):

    def __init__(self):

        super().__init__()

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)
        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        self.title = 'ORACode'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.initUI()
        self.show()
    
    def initUI(self):
        
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('to be filled up')
        
        # mainMenu Buttons
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        # creat new model Button
        creatButton = QAction(QIcon('creat24.png'), 'New model', self)
        creatButton.setShortcut('Ctrl+N')
        creatButton.setStatusTip('creat new model')
        creatButton.triggered.connect(self.create)
        fileMenu.addAction(creatButton)

        # Save current model Button
        saveButton = QAction(QIcon('save24.png'), 'Save', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.setStatusTip('Save current model')
        saveButton.triggered.connect(self.saveState)
        fileMenu.addAction(saveButton)
        
        # Exit application Button
        exitButton = QAction(QIcon('exit.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        self.setWindowTitle("Styles")
        self.changeStyle('Windows')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()
    
    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)
    


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    ex = Ui_MainForm()
    ex.show()
    sys.exit(app.exec_()) 