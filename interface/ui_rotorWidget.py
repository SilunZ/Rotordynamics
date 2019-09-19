

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
import numpy as np

class Rotor( QtWidgets.QGroupBox ):
    """
    description : pass
    """
    def __init__(self):
        
        super( Rotor, self).__init__()
        
        # set rotor layout
        layout = QtWidgets.QGridLayout()
        self.labels_list = ['Rotating Speed', 'Shaft Radius', 'Total rotor mass']
        self._txtboxs = []
        for i, label in enumerate(self.labels_list):

            lab = QtWidgets.QLabel('%s' % (label))
            layout.addWidget(lab, i , 0)

            self._txtboxs.append( QtWidgets.QLineEdit() ) 
            layout.addWidget(self._txtboxs[-1], i , 1)

        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(0, 110)
        self.setLayout(layout)
    
    @pyqtSlot()
    def applyButtonAction(self):
        
        self.data_list = []
        for i, label in enumerate(self.labels_list):
            numInTxt = self._txtboxs[i].text()
            self.data_list.append( np.float( numInTxt ) )

        # set rotor input dictionay to store the user defined data
        self.ORACodeInput = {'labels': self.labels_list, 'data': self.data_list}