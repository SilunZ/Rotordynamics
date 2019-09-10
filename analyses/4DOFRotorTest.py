# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
import os,sys
rootPath = os.getcwd()
sys.path.append( rootPath ) 

# import rotor component
from models.rotor4dof import FourDegreeOfFreedomRotor
Omega, Ra, length, rho = 1000, 0.2, 1.0, 7850
rotModel = FourDegreeOfFreedomRotor(Omega, Ra, length, rho )

# import disc components and assembly them to the created shaft
from models.rotorComponentBuilder import DiscBuilder
L_disc, Re_disc, Ri_disc, rho_disc  = 0.1, 0.4, 0.2, 7850
disc1 = DiscBuilder( L_disc, Re_disc, Ri_disc, rho_disc )
disc1.setDiscAxialCoordinate( L_disc*0.5 )
disc2 = DiscBuilder( L_disc, Re_disc, Ri_disc, rho_disc )
disc2.setDiscAxialCoordinate( length - L_disc*0.5 )

rotModel.addDiscComponent(disc1)
rotModel.addDiscComponent(disc2)
print (rotModel.discs)

sys.exit()


# import bearing component
from models.bearingSimpleKC import SimpleKCBearing
brgModel =  SimpleKCBearing( rotModel.Omega, rotModel.Ra )
brgModel.readBearingDynamicCoefficientFile( rootPath + r"\analyses\DynaCoef_Data.txt" )

# add bearing into rotor model
rotModel.addBearingComponent(brgModel)

# import transient simulation module 
from solvers.transient_simulation import TransientSimulation
simu = TransientSimulation( rotModel, dt = 1e-4 )
simu.setTransientParametors( 0.0, 1.0 )
simu.initializeIntegrator( tol=1e-6, Iter=10 )
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

