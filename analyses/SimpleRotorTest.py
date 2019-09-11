# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
import os,sys
rootPath = os.getcwd()
sys.path.append( rootPath ) 

# import rotor component
from models.rotor2dof import TwoDegreeOfFreedomRotor
rotModel = TwoDegreeOfFreedomRotor( Omega=1000, Ra_ext=0.2, mass=5.0, Um=1e-4 )

# import bearing component
from models.bearingSimpleKC import SimpleKCBearing
brgModel =  SimpleKCBearing( rotModel.Omega, rotModel.Ra_ext )
brgModel.readBearingDynamicCoefficientFile( rootPath + r"\analyses\DynaCoef_Data.txt" )

# add bearing into rotor model
rotModel.addBearingComponent(brgModel)

# import transient simulation module 
from solvers.transient_simulation import TransientSimulation
simu = TransientSimulation( rotModel, dt = 1e-4 )
simu.setTransientParametors( 0.0, 1.0 )
simu.initializeIntegrator( tol=1e-3, Iter=10 )
simu.integrate()

# post traitement simple
import matplotlib.pyplot as plt
t_vect = simu.resu["time"]
pos_vect = simu.resu["position"]
converganceItera_vect = simu.resu["convergeItera"]
converganceError_vect = simu.resu['convergeError']

plt.figure()
plt.plot( t_vect, pos_vect)
plt.show()

