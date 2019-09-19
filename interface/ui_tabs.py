

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot

class TabsWidget( QtWidgets.QWidget ):
    
    def __init__(self, parent):
        
        super( QtWidgets.QWidget, self).__init__(parent)
        

##
    def _setRotorTabs(self):

        # Create first tab
        self.tab1.box = QtWidgets.QGridLayout(self.tab1)
        # self.tab1.box.setColumnStretch(1, 10)

        # topLeftGroupBox = QtWidgets.QGroupBox()

        # radioButton1 = QtWidgets.QRadioButton("Radio button 1")
        # radioButton2 = QtWidgets.QRadioButton("Radio button 2")
        # radioButton3 = QtWidgets.QRadioButton("Radio button 3")

        # ButtonBoxLayout = QtWidgets.QHBoxLayout()
        # ButtonBoxLayout.addWidget(radioButton1)
        # ButtonBoxLayout.addWidget(radioButton2)
        # ButtonBoxLayout.addWidget(radioButton3)
        # ButtonBoxLayout.addStretch(1)
        # topLeftGroupBox.setLayout(ButtonBoxLayout)

        # self.tab1.box.addWidget(radioButton1)


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

        # Create the buttons in bottom of the tab1 layout

        # ButtonLayout = QtWidgets.QHBoxLayout()

        # self.button1 = QtWidgets.QPushButton('apply', self)
        # self.button2 = QtWidgets.QPushButton('reset', self)

        # ButtonLayout.addWidget(self.button1)
        # ButtonLayout.addWidget(self.button2)

        # self.tab1.box.addWidget(self.button1,20,3)
        # self.tab1.box.addWidget(self.button2,21,3)

        # connect button to function on_click
        # self.button1.clicked.connect(self.apply_click)

    @pyqtSlot()
    def apply_click(self):
        textboxValue1 = self._textbox1.text()
        textboxValue2 = self._textbox2.text()
        textboxValue3 = self._textbox3.text()

        QtWidgets.QMessageBox.question(self, 'Message - pythonspot.com', "You typed: \n" + textboxValue1 + "\n" + textboxValue2 + "\n" + textboxValue3
                                                                       , QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

        self.textbox.setText("")

##
