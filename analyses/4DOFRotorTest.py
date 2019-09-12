# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import time
import numpy as np
import os,sys

rootPath = os.getcwd()
sys.path.append( rootPath ) 

start_time = time.time()
##

# Build rotor 
from models.rotorComponentBuilder import *
from models.rotor4dof import FourDegreeOfFreedomRotor

Omega, Ra, length, rho = 7000, 0.0225, 0.43, 7850
rotModel = FourDegreeOfFreedomRotor(Omega, Ra, 0.0, length, rho )
rotModel.setRotorMassMatrix(M=2.0, J=0.1359)

# import unbalance components
Unbalance1 = UnbalanceBuilder(amp = 10e-6, phase = 0.0)
Unbalance1.setAxialCoordinate( length )
rotModel.addUnbalanceComponent( Unbalance1 )

# import disc components and assembly them to the created shaft
L_disc, Re_disc, Ri_disc, rho_disc  = 0.02, 0.04, 0.0225, 7850
disc1 = DiscBuilder( L_disc, Re_disc, Ri_disc, rho_disc )
disc1.setDiscAxialCoordinate( L_disc*0.5 )
disc2 = DiscBuilder( L_disc, Re_disc, Ri_disc, rho_disc )
disc2.setDiscAxialCoordinate( length - L_disc*0.5 )

rotModel.addDiscComponent(disc1)
rotModel.addDiscComponent(disc2)
# rotModel.computeBasicGeometricalFeatures()

# import bearing components
from models.bearingSimpleKC import SimpleKCBearing
brg1 =  SimpleKCBearing( Omega, Ra )
brg1.setAxialCoordinate( length*0.2 )
brg1.readBearingDynamicCoefficientFile( rootPath + r"\analyses\DynaCoef_Data.txt" )

brg2 =  SimpleKCBearing( Omega, Ra )
brg2.setAxialCoordinate( length*0.8 )
brg2.readBearingDynamicCoefficientFile( rootPath + r"\analyses\DynaCoef_Data.txt" )

rotModel.addBearingComponent(brg1)  
rotModel.addBearingComponent(brg2)  


# import transient simulation module 
from solvers.transient_simulation import TransientSimulation
simu = TransientSimulation( rotModel, dt = 0.5e-4 )
simu.setTransientParametors( 0.0, 1.0 )
simu.initializeIntegrator( tol=1e-3, Iter=5 )
simu.integrate()

print("--- %s seconds ---" % (time.time() - start_time)) 

# post traitement simple
import matplotlib.pyplot as plt
t_vect = simu.resu["time"]
pos_vect = simu.resu["position"]
converganceItera_vect = simu.resu["convergeItera"]
converganceError_vect = simu.resu['convergeError']

plt.figure()
plt.subplot(221)
plt.plot( t_vect, pos_vect[:,0:2])
plt.subplot(222)
plt.plot( pos_vect[:,1], pos_vect[:,0] )
plt.subplot(223)
plt.plot( t_vect, converganceError_vect)
plt.subplot(224)
plt.plot( t_vect, converganceItera_vect)
plt.show()
