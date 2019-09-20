
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
        self.SetButton.setDefault(False)
        # self.SetButton.clicked.connect( self.click_SetButtonAction() )

        self.RunButton = QtWidgets.QPushButton(" Run simulation")
        self.RunButton.setDefault(False)
        # self.SetButton.clicked.connect( self.click_RunButtonAction() )


        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.SetButton)
        layout.addWidget(self.RunButton)



        self.setLayout( layout )

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
        self.simu.setTransientParametors( 0.0, 1.0 )
        self.simu.initializeIntegrator( tol=1e-10, Iter=30 )

    
    
    @pyqtSlot()
    def click_RunButtonAction(self):
        pass
        # self.RunButton.clicked.connect( self.simu.integrate() )


    def click_SetButtonAction(self):
        pass
        # self._setSimulatingModelBuilder()

        
        

    def click_ApplybuttonAction(self):
        pass
