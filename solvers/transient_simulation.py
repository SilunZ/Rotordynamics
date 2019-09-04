# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from newmark_integrator import Newmark_Integrator
import sys


class TransientSimulation():

    def __init__(self, rotModel ):
        
        self._setTimestep()
        self.rotor = rotModel

        # initialize numerical resualts dict
        self.resu = {'time':[],'position':[],'velocity':[]}
        
    def _setTimestep(self):
        self._dt = 1e-4

    def setTransientParametors(self, tini, tend):
        self._tini = tini
        self._tend = tend
    
    def integrate(self):
        # set necessary time parameters
        t0 = self._tini
        dt = self._dt

        self._saveOneTimestepResu(t0, self.rotor.Q , self.rotor.DQ)

        # set one time step integrator 
        dof = self.rotor.dof
        M = self.rotor.M
        f = self.rotor.functionForce
        df = self.rotor.functionDerivativeForce
        integ = Newmark_Integrator( dof, M, f, df )
        integ.setInitialValues(self.rotor.Q , self.rotor.DQ)


        while 1:

            t1 = t0 + dt

            #
            integ.integrateOneTimeStep(t0, t1)
            self.rotor.setRotorPositionAndVelocity(integ.Q, integ.DQ)

            # 
            self._saveOneTimestepResu(t1, self.rotor.Q , self.rotor.DQ)
            print t1
            print integ.Q
            print self.rotor.Q
            print

            if t1 >= self._tend :
                break
            t0 = np.copy(t1)
        
        self._saveAllResu()

    # save the simulation resualts
    def _saveOneTimestepResu(self, inst, q, dq):
        self.resu['time'].append(inst)
        self.resu['position'].append( np.copy(q) )
        self.resu['velocity'].append( np.copy(dq) )

    def _saveAllResu(self):
        self.resu['time'] = np.asarray( self.resu['time'] )
        self.resu['position'] = np.asarray( self.resu['position'] )
        self.resu['velocity'] = np.asarray( self.resu['velocity'] )







