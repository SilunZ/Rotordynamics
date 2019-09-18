

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot

class TabsWidget( QtWidgets.QWidget):
    
    def __init__(self, parent):
        
        super( QtWidgets.QWidget, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()
        self.tab5 = QtWidgets.QWidget()
        self.setGeometry(10, 10, 100, 100)
        
        # Add tabs
        self.tabs.addTab(self.tab1," Rotor ")
        self.tabs.addTab(self.tab2," Bearing ")
        self.tabs.addTab(self.tab3," Calculation setting ")
        self.tabs.addTab(self.tab4," Solve ")
        self.tabs.addTab(self.tab5," Results ")

        self._setRotorTabs()

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

##
    def _setRotorTabs(self):

        # Create first tab
        self.tab1.box = QtWidgets.QGridLayout(self.tab1)
        self.tab1.box.setColumnStretch(1, 10)

        # Creat labels
        label1 = QtWidgets.QLabel('Rotating Speed', self)
        label2 = QtWidgets.QLabel('Shaft Radius', self)
        label3 = QtWidgets.QLabel('Total rotor mass', self)

        self.tab1.box.addWidget(label1,0,0)
        self.tab1.box.addWidget(label2,1,0)
        self.tab1.box.addWidget(label3,2,0)

        # Create textboxs
        self._textbox1 = QtWidgets.QLineEdit(self)
        self._textbox2 = QtWidgets.QLineEdit(self)
        self._textbox3 = QtWidgets.QLineEdit(self)
        
        self.tab1.box.addWidget(self._textbox1,0,1)
        self.tab1.box.addWidget(self._textbox2,1,1)
        self.tab1.box.addWidget(self._textbox3,2,1)

        # Create a button in the window
        self.button1 = QtWidgets.QPushButton('apply', self)
        self.button2 = QtWidgets.QPushButton('reset', self)

        self.tab1.box.addWidget(self.button1,20,0)
        self.tab1.box.addWidget(self.button2,21,0)

        # connect button to function on_click
        self.button1.clicked.connect(self.apply_click)

    @pyqtSlot()
    def apply_click(self):
        textboxValue1 = self._textbox1.text()
        textboxValue2 = self._textbox2.text()
        textboxValue3 = self._textbox3.text()

        QtWidgets.QMessageBox.question(self, 'Message - pythonspot.com', "You typed: \n" + textboxValue1 + "\n" + textboxValue2 + "\n" + textboxValue3
                                                                       , QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

        self.textbox.setText("")

##
