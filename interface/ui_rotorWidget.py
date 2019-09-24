

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, Qt
import os, sys
import numpy as np

class Rotor( QtWidgets.QMainWindow ):

    """
    description : pass
    """
    def __init__(self):
        
        super( Rotor, self).__init__()
        
        # set model choice box (QHBoxLayout)
        self.labels_list = ['Jeffcott model', 
                            '4-degree-of-freedow model', 
                            'Finite element model']

        self.modelChoiceComboBox = QtWidgets.QComboBox()
        for i, label in enumerate(self.labels_list):
            self.modelChoiceComboBox.addItem(label)
        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.modelChoiceComboBox)
        modelChoiceBox = QtWidgets.QGroupBox(" Rotor model : ")
        modelChoiceBox.setLayout(layout)

        # set rotor model parameter box (in function of the chosen model)
        self.modelChoiceComboBox.activated[str].connect(self._managementOfModel)

        # set rotor widgets main layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget( modelChoiceBox, 0, 0)
        
        centralWidget = QtWidgets.QDialog()
        centralWidget.setLayout(self.layout)
        self.setCentralWidget(centralWidget)
    
    def _managementOfModel(self):
        
        modelComboBoxIndex = self.modelChoiceComboBox.currentIndex()
        if modelComboBoxIndex == 0 : # chose Jeffcott model 
            self.RotorModelWidgets = JeffCottRotor()
        elif modelComboBoxIndex == 1 : # chose 4 degree of freedow model 
            pass
        elif modelComboBoxIndex == 2 : # chose the finite element model
            pass
        self.layout.addWidget( self.RotorModelWidgets, 1, 0, 5, 1)



class JeffCottRotor( QtWidgets.QGroupBox ):

    """
    description : pass
    """
    def __init__(self):
        
        super( JeffCottRotor, self).__init__()
        
        ## parametors box
        self.labels_list = ['Rotating Speed (RPM)', 'Shaft Radius (m)', 'Total rotor mass (Kg)', 'unbalance (kg.m)']
        self._txtboxs = []

        layout = QtWidgets.QGridLayout()
        for i, label in enumerate(self.labels_list):

            lab = QtWidgets.QLabel('%s' % (label))  ##
            layout.addWidget(lab, i , 0)

            self._txtboxs.append( QtWidgets.QLineEdit() ) 
            layout.addWidget(self._txtboxs[-1], i , 1)

        self._setDefaultValue()
        
        # layout.setColumnStretch(1, 1)
        # layout.setColumnMinimumWidth(0, 110)
        
        ## image box
        vizu = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("interface\images\jeffcottRotor.png")
        pixmap2 = pixmap.scaled(400, 200, QtCore.Qt.KeepAspectRatio)
        vizu.setPixmap(pixmap2)
        
        
        layout.addWidget(vizu, 0, 2, 0, 1)
        
        self.setLayout(layout)
    
    def _setDefaultValue(self):

        self._txtboxs[0].setText( "1000.0" ) 
        self._txtboxs[1].setText( "0.2" ) 
        self._txtboxs[2].setText( "5.0" ) 
        self._txtboxs[3].setText( "100e-6" ) 
    
    @pyqtSlot()
    def applyButtonAction(self):
        
        self.data_list = []
        for i, label in enumerate(self.labels_list):

            numInTxt = self._txtboxs[i].text()

            try:
                self.data_list.append( np.float( numInTxt ) )
            except:
                QtWidgets.QMessageBox.question(self, 'Warning : ', " please check and fill up all the empty boxes" , QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                break

        # set rotor input dictionay to store the user defined data
        self.ORACodeInput = {'labels': self.labels_list, 'data': self.data_list}
        print ( self.ORACodeInput )
    
## to be implemented

class FourDOFRotor( QtWidgets.QGroupBox ):

    """
    description : pass
    """
    def __init__(self):
        
        super( FourDOFRotor, self).__init__()
        
        ## parametors box

        self.labels_list = ['Rotating Speed (RPM)', 'Shaft Radius (m)', 'Total rotor mass (Kg)', 'unbalance (kg.m)']
        self._txtboxs = []

        layout = QtWidgets.QGridLayout()
        for i, label in enumerate(self.labels_list):

            lab = QtWidgets.QLabel('%s' % (label))  ##
            layout.addWidget(lab, i , 0)

            self._txtboxs.append( QtWidgets.QLineEdit() ) 
            layout.addWidget(self._txtboxs[-1], i , 1)

        self._setDefaultValue()
        
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(0, 110)

        self.setLayout(layout)
    
    def _setDefaultValue(self):

        self._txtboxs[0].setText( "1000.0" ) 
        self._txtboxs[1].setText( "0.2" ) 
        self._txtboxs[2].setText( "5.0" ) 
        self._txtboxs[3].setText( "100e-6" ) 
    