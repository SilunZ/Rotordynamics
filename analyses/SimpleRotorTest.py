# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import os,sys
import numpy as np

# import rotor component
from models.rotor2dof import TwoDegreeOfFreedomRotor
rotModel = TwoDegreeOfFreedomRotor( 2000, 0.02, 1.0, 1e-4 )

# import bearing component
#skip

# import transient simulation module 
from solvers.transient_simulation import TransientSimulation
simu = TransientSimulation( rotModel )
simu.setTransientParametors(0,1)

simu.integrate()