# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from newmark_integrator import Newmark_Integrator
import sys


class TransientSimulation():

    def __init__(self, rotModel ):
        
        self._setTimestep()
        self.rotor = rotModel

        
        
    def _setTimestep(self):
        self._dt = 1e-3
    
    def setTransientParametors(self, tini, tend):
        self._tini = tini
        self._tend = tend
    
    def integrate(self):
        # set necessary time parameters
        t0 = self._tini
        dt = self._dt


        # set one time step integrator 
        dof = self.rotor.dof
        f = self.rotor.functionForce
        df = self.rotor.functionDerivativeForce
        M = self.rotor.M
        integ = Newmark_Integrator( dof, M, f, df )
        

        while 1:

            t1 = t0 + dt

            integ.integrateOneTimeStep(t0, t1)
            self.rotor.setRotorPositionAndVelocity(integ.Q, integ.DQ)

            if t1 >= self._tend :
                break
            t0 = np.copy(t1)







