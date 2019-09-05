# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from newmark_integrator import Newmark_Integrator


class TransientSimulation():

    def __init__(self, rotModel, dt ):
        
        self._setTimestep(dt)
        self.rotor = rotModel

        # initialize numerical resualts dict
        self.resu = {'time':[],'position':[],'velocity':[], 'convergeError':[], 'convergeItera':[] }
        
    def _setTimestep(self, dt):
        self._dt = dt

    def setTransientParametors(self, tini, tend):
        self._tini = tini
        self._tend = tend
    
    def initializeIntegrator(self, tol, Iter):
        dof = self.rotor.dof
        M = self.rotor.M
        f = self.rotor.functionForce
        df = self.rotor.functionDerivativeForce
        self.OnestepInteg = Newmark_Integrator( dof, M, f, df )

        self.OnestepInteg.setInitialValues(self.rotor.Q , self.rotor.DQ)
        self.OnestepInteg.setConvergenceCriteria( tol, Iter )
        
    def integrate(self):
        # set necessary time parameters
        t0 = self._tini
        dt = self._dt

        # save initial information into results
        converganceErr = self.OnestepInteg.converganceErr
        converganceItera = self.OnestepInteg.converganceItera
        self._saveOneTimestepResu(t0, self.rotor.Q , self.rotor.DQ, converganceErr, converganceItera)

        while 1:
            
            # one time step avances.
            t1 = t0 + dt

            # one step integration
            self.OnestepInteg.integrateOneTimeStep(t0, t1)
            
            # update the information in the other relative objects.
            self.rotor.setRotorPositionAndVelocity( self.OnestepInteg.Q, self.OnestepInteg.DQ )

            # save the instance resualts
            converganceErr = self.OnestepInteg.converganceErr
            converganceItera = self.OnestepInteg.converganceItera
            self._saveOneTimestepResu(t1, self.rotor.Q , self.rotor.DQ, converganceErr, converganceItera)

            # end of one timestep integration
            if t1 >= self._tend :
                break
            t0 = np.copy(t1)

        # end of temporel integration
        self._saveAllResu()


    # save the simulation resualts
    def _saveOneTimestepResu(self, inst, q, dq, convergErr, convergItera):
        self.resu['time'].append(inst)
        self.resu['position'].append( np.copy(q) )
        self.resu['velocity'].append( np.copy(dq) )
        self.resu['convergeError'].append( convergErr )
        self.resu['convergeItera'].append( convergItera )
        

    def _saveAllResu(self):
        self.resu['time'] = np.asarray( self.resu['time'] )
        self.resu['position'] = np.asarray( self.resu['position'] )
        self.resu['velocity'] = np.asarray( self.resu['velocity'] )
        self.resu['convergeError'] = np.asarray( self.resu['convergeError'] )
        self.resu['convergeItera'] = np.asarray( self.resu['convergeItera'] )







