# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

# import os,sys
# sys.path.append(os.path.realpath('..'))

import numpy as np


# import rotor component
from models.rotor2dof import TwoDegreeOfFreedomRotor
rotModel = TwoDegreeOfFreedomRotor( Omega=1000, Ra=0.2, mass=5.0, Um=1e-4 )

# import bearing component
#skip


# import transient simulation module 
from solvers.transient_simulation import TransientSimulation
simu = TransientSimulation( rotModel, dt = 1e-4 )
simu.setTransientParametors( 0.0, 1.0 )
simu.initializeIntegrator( tol=1e-6, Iter=10 )

simu.integrate()


# post traitement

import matplotlib.pyplot as plt
t_vect = simu.resu["time"]
pos_vect = simu.resu["position"]
converganceItera_vect = simu.resu["convergeItera"]
converganceError_vect = simu.resu['convergeError']

# print pos_vect

plt.figure()
plt.plot( t_vect, pos_vect)
plt.show()

