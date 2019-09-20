
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
import numpy as np

class PostProcessing( QtWidgets.QGroupBox ):
    """
    description : pass
    """ 
    def __init__(self):
        
        super( PostProcessing, self).__init__()
        
        # set rotor layout
        layout = QtWidgets.QGridLayout()
        self.labels_list = ['Rotating Speed', 'Radius', 'Clearance']
        self._txtboxs = []
        for i, label in enumerate(self.labels_list):

            lab = QtWidgets.QLabel('%s' % (label))  ##
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

            try:
                self.data_list.append( np.float( numInTxt ) )
            except:
                QtWidgets.QMessageBox.question(self, 'Warning : ', " please check and fill up all the empty boxes" , QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                break

        # set rotor input dictionay to store the user defined data
        self.ORACodeInput = {'labels': self.labels_list, 'data': self.data_list}
        print ( self.ORACodeInput )