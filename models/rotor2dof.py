# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from rotorComponentBuilder import RotorBuilder

class TwoDegreeOfFreedomRotor( RotorBuilder ):

    def __init__(self, Omega, Ra, mass, Um):

        RotorBuilder.__init__(self, Omega, Ra)
        
        self._setMassMatrix( mass )
        self._setStiffnessMatrix()
        self._setDampping()
        self._setUnbalance( Um )

        # initial rotor position and velocity
        self.dof = 2                        # degree of freedom in x and y directions
        self.Q0 = np.zeros((self.dof,))
        self.DQ0 = np.zeros_like(self.Q0)
        self.DDQ0 = np.zeros_like(self.Q0)
        self.Q = np.zeros_like(self.Q0)
        self.DQ = np.zeros_like(self.Q0)
        self.DDQ = np.zeros_like(self.Q0)
    
    def setRotorPositionAndVelocity(self, Q, DQ, DDQ=None):

        self.Q0[:] = Q
        self.DQ0[:] = DQ
        if not DDQ is None:
            self.DDQ0[:] = DDQ

    def _setMassMatrix(self, value):
        self.M = np.zeros((2,2))
        self.M[0,0] = value
        self.M[1,1] = value
    
    def _setStiffnessMatrix(self):
        self.K = np.zeros((2,2))
        k1, k2 = 1e+7, 1e+7
        self.K[0,0] = k1 + k2
        self.K[0,1] = -k2
        self.K[1,0] = -k2
        self.K[1,1] =  k2
    
    def _setDampping(self):
        self.C = np.zeros((2,2))
        self.C[0,0] = 0.0
        self.C[0,1] = 0.0
        self.C[1,0] = 0.0
        self.C[1,1] = 0.0
    
    def _setUnbalance(self, value):
        self._Um = value

    ## exterior forces applied to rotor in function of time instance (inst)

    def _computeUnbalanceForce(self, inst):

        angle = np.angle(self._Um)
        w =  self.omega
        
        Fx = w**2 * abs(self._Um)* np.cos( w*inst + angle )
        Fy = w**2 * abs(self._Um)* np.sin( w*inst + angle )
        Fumba = [Fx, Fy]

        return Fumba 
    
    def _computeBearingForce(self, Q, dQ):

        Fbrg = - np.dot( self.K, Q  ) - np.dot( self.C, dQ  )

        return Fbrg
    
    def functionForce(self, inst, Q, dQ, DDQ):

        ### Force
        # rolling bearing force
        Fbrg = self._computeBearingForce(Q, dQ)

        # imbalance or harmonic force
        Fimba = self._computeUnbalanceForce( inst )

        # gravity force
        Fgrav = np.dot( self.M, [9.81, 0.0] )

        # total forces
        Ftotal = Fbrg +  Fimba + Fgrav

        return Ftotal
    
    def functionDerivativeForce(self, dt, Q, DQ, DDQ):
        return -self.K , -self.C









