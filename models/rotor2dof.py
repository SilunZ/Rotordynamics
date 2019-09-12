# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from models.rotorComponentBuilder import BasicRotorBuilder

class Load():
    def __init__(self):
        pass

class TwoDegreeOfFreedomRotor( BasicRotorBuilder ):

    def __init__(self, Omega, Ra_ext, mass, Um):

        BasicRotorBuilder.__init__(self, Omega, Ra_ext)
        
        self._setRotorMassMatrix( mass )
        self._setUnbalance( Um )

        # initial rotor position and velocity
        self.dof = 2                        # degree of freedom in x and y directions
        self.Q = np.zeros((self.dof,))
        self.DQ = np.zeros_like(self.Q)
        self.DDQ = np.zeros_like(self.Q)
    
    def setRotorPositionAndVelocity(self, Q, DQ, DDQ=None):

        self.Q = Q
        self.DQ = DQ
        if not DDQ is None:
            self.DDQ = DDQ

    def addBearingComponent(self, brg):

        self._brg = brg


    def _setRotorMassMatrix(self, value):
        self.M = np.zeros((2,2))
        self.M[0,0] = value
        self.M[1,1] = value
    
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
    
    def _computeBearingForce(self):

        Fbrg = -( np.dot( self._brg.K, self.Q  ) + np.dot( self._brg.C, self.DQ  ) )

        return Fbrg
    
    # total force to be used
    
    def functionForce(self, inst, dt, Q, DQ):

        ### Force
        # rolling bearing force
        Fbrg = self._computeBearingForce()

        # imbalance or harmonic force
        Fimba = self._computeUnbalanceForce( inst )

        # gravity force
        Fgrav = np.dot( self.M, [9.81, 0.0] )

        # total forces
        Ftotal = Fbrg +  Fimba + Fgrav

        return Ftotal
    
    def functionDerivativeForce(self, dt, Q, DQ):
        return -self._brg.K , -self._brg.C

    # output rotor class information
    def getRotorPositionAndVelocity(self):
        return self.Q, self.DQ









