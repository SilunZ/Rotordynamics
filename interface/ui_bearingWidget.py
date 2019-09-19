
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot


class BearingWidget( QtWidgets.QWidget ):
    
    def __init__(self, parent):
        
        super( QtWidgets.QWidget, self).__init__(parent)
        
        # Create first tab
        layout = QtWidgets.QGridLayout(parent)
        # self.tab1.box.setColumnStretch(1, 10)

        # Creat labels
        label1 = QtWidgets.QLabel('Rotating Speed', self)
        label2 = QtWidgets.QLabel('Shaft Radius', self)
        label3 = QtWidgets.QLabel('Total rotor mass', self)

        layout.addWidget(label1,0,0)
        layout.addWidget(label2,1,0)
        layout.addWidget(label3,2,0)

        # Create textboxs
        self._textbox1 = QtWidgets.QLineEdit(self)
        self._textbox2 = QtWidgets.QLineEdit(self)
        self._textbox3 = QtWidgets.QLineEdit(self)
        
        layout.addWidget(self._textbox1,0,1)
        layout.addWidget(self._textbox2,1,1)
        layout.addWidget(self._textbox3,2,1)


    @pyqtSlot()
    def apply_click(self):

        textboxValue1 = self._textbox1.text()
        textboxValue2 = self._textbox2.text()
        textboxValue3 = self._textbox3.text()

        QtWidgets.QMessageBox.question(self, 'Message - pythonspot.com', "You typed: \n" + textboxValue1 + "\n" + textboxValue2 + "\n" + textboxValue3
                                                                       , QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

        # self.textbox.setText("")