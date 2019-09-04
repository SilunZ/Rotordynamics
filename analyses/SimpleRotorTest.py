# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import os,sys
sys.path.append(os.path.realpath('..'))

import numpy as np


# import rotor component
from models.rotor2dof import TwoDegreeOfFreedomRotor
rotModel = TwoDegreeOfFreedomRotor( 10000, 0.2, 1.0, 1e-4 )

# import bearing component
#skip

# import transient simulation module 
from solvers.transient_simulation import TransientSimulation
simu = TransientSimulation( rotModel )
simu.setTransientParametors(0.0, 0.1)

simu.integrate()


# post traitement

import matplotlib.pyplot as plt
t_vect = simu.resu["time"]
pos_vect = simu.resu["position"]

print pos_vect

plt.figure()
plt.plot( t_vect, pos_vect[:,0])
plt.plot( t_vect, pos_vect[:,1])
plt.show()

