# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from models.rotorComponentBuilder import RotorBuilder

class FourDegreeOfFreedomRotor( RotorBuilder ):

    def __init__(self, Omega, Ra, length, rho):

        RotorBuilder.__init__(self, Omega, Ra)
        self._setLength(length)
        self._setMaterial(rho)

        self.discs = []
        self.brgs = []
        self.loads = []

        # initial rotor position and velocity at center of mass
        self.dof = 4                        # degree of freedom in x and y directions (rotation and translation)
        self.Q = np.zeros((self.dof,))
        self.DQ = np.zeros_like(self.Q)
        self.DDQ = np.zeros_like(self.Q)
    
    def _setLength(self, length):
        self.length = length

    def _setMaterial(self, rho):
        self.density = rho

    def addDiscComponent(self, disc):
        self.discs.append( disc )

    def addBearingComponent(self, brg):
        self.brgs.append( brg )

    def addLoadComponenet(self, load):
        self.loads.append( load )
    
    def computeRotorMass(self):
        self.mass = 

    ##
    def setRotorPositionAndVelocityAtCentreOfMass(self, Q, DQ, DDQ=None):
        self.Q = Q
        self.DQ = DQ
        if not DDQ is None:
            self.DDQ = DDQ


    ##

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
    
    def functionForce(self, inst, dt, Q, DQ, DDQ):

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
    
    def functionDerivativeForce(self, dt, Q, DQ, DDQ):
        return -self._brg.K , -self._brg.C

    # output rotor class information
    def getRotorPositionAndVelocity(self):
        return self.Q, self.DQ









