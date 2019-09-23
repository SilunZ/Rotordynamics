
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
import numpy as np
import os, sys


class Resolution( QtWidgets.QGroupBox ):
    """
    description : pass
    """ 
    def __init__(self):
        
        super( Resolution, self).__init__()

        self.SetButton = QtWidgets.QPushButton(" Set up the simulating model")
        self.SetButton.clicked.connect( self.click_SetButtonAction )

        self.RunButton = QtWidgets.QPushButton(" Run simulation ")
        self.RunButton.clicked.connect( self.click_RunButtonAction )
        
        layout = QtWidgets.QHBoxLayout() 
        layout.addWidget(self.SetButton)
        layout.addWidget(self.RunButton)
        self.setLayout( layout )

        ##
        self.modelAvailble =  False
        self.resuDataAvail = False
        
        

    def getInput(self, rot, brg, analy):
        
        self._rotorInput = rot
        self._bearingInput = brg
        self._analysisInput = analy

        self.simulatingModelBuilder()
    

    def _setSimulatingModelBuilder(self):

        rootPath = os.getcwd()
        sys.path.append( rootPath )

        # import rotor component
        from models.rotor2dof import TwoDegreeOfFreedomRotor

        # Omega = self._rotorInput[]
        rotModel = TwoDegreeOfFreedomRotor( Omega=1000, Ra_ext=0.2, mass=5.0, Um=1e-4 )

        # import bearing component
        from models.bearingSimpleKC import SimpleKCBearing
        brgModel =  SimpleKCBearing( rotModel.Omega, rotModel.Ra_ext )
        brgModel.readBearingDynamicCoefficientFile( rootPath + r"\analyses\DynaCoef_Data.txt" )

        # add bearing into rotor model
        rotModel.addBearingComponent(brgModel)

        # import transient simulation module 
        from solvers.transient_simulation import TransientSimulation
        self.simu = TransientSimulation( rotModel, dt = 1e-4 )
        self.simu.setTransientParametors( 0.0, 0.2 )
        self.simu.initializeIntegrator( tol=1e-7, Iter=30 )
        
    
    @pyqtSlot()
    def click_RunButtonAction(self):

        if  self.modelAvailble == True:
            self.simu.integrate()
            self.resuDataAvail = True
            print ('---> The calculation has been completed.')
        else: 
            QtWidgets.QMessageBox.question(self, 'Warning : ', " please set up first the rotor model" , QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def click_SetButtonAction(self):
        self._setSimulatingModelBuilder()
        self.modelAvailble = True
        print ('---> The rotor model has been setted.')

    def click_ApplybuttonAction(self):
        pass
