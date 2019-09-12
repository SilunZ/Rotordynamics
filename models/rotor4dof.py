# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from models.rotorComponentBuilder import BasicRotorBuilder

class FourDegreeOfFreedomRotor( BasicRotorBuilder ):

    def __init__(self, Omega, Ra_ext, Ra_int, length, rho):

        BasicRotorBuilder.__init__(self, Omega, Ra_ext, Ra_int)
        self._setLength(length)
        self._setMaterial(rho)

        self.disc_list = []
        self.brg_list = []
        self.unb_list = []

        self.totalMass = 0.0
        self.GZ = 0.0

        # initial rotor position and velocity at center of mass
        self.dof = 4                        # degree of freedom in x and y directions (rotation and translation)
        self.Q = np.zeros((self.dof,))
        self.DQ = np.zeros_like(self.Q)
        self.DDQ = np.zeros_like(self.Q)
        self.M = np.zeros((self.dof,self.dof))
    
    def _setLength(self, length):
        self.length = length

    def _setMaterial(self, rho):
        self.density = rho

    def addDiscComponent(self, disc):
        self.disc_list.append( disc )

    def addBearingComponent(self, brg):
        self.brg_list.append( brg )
    
    def addUnbalanceComponent(self, unb):
        self.unb_list.append( unb )

## some basic computation for geometrical and inertie features

    def _computeRotorMass(self):
        
        self.shaftMass = np.pi * ( self.Ra_ext**2 - self.Ra_int**2) * self.length * self.density
        self.totalMass += self.shaftMass
        
        for disc in self.disc_list:
            self.totalMass += disc.mass
    
    def _computeCenterOfMass(self):
        """
        calculate the center of mass of the assembly rotor
        """

        self.GaZ = self.shaftMass*0.5*self.length
        self.GZ += self.GaZ

        for disc in self.disc_list:
            self.GZ += disc.mass*disc.DZ
        
        self.GZ /= self.totalMass

        print ("--- the rotor center of mass GZ is %s m" % self.GZ)
    
    def _computeMomentOfInertia(self):
        """
        Iaxx, Iayy are the shaft moments of inertia ; Izz is the shaft polar moment of inertia
        """
        self.Iaxx = 1.0/4.0 * np.pi * ( self.Ra_ext**4 - self.Ra_int**4 )
        self.Iayy = 1.0/4.0 * np.pi * ( self.Ra_ext**4 - self.Ra_int**4 )
        self.Iazz = 1.0/2.0 * np.pi * ( self.Ra_ext**4 - self.Ra_int**4 )
        
        # self.GaZ
        # for disc in self.disc_list:

    def _updateRotorMassMatrix(self):
        self.M[0,0] = self.totalMass
        self.M[1,1] = self.totalMass
        self.M[2,2] = self.Iazz*self.totalMass
        self.M[3,3] = self.Iazz*self.totalMass
    
    def setRotorMassMatrix(self, M, J):
        self.M[0,0] = M
        self.M[1,1] = M
        self.M[2,2] = J
        self.M[3,3] = J

    def computeBasicGeometricalFeatures(self):
        self._computeRotorMass()
        self._computeCenterOfMass()
        self._computeMomentOfInertia()
        self._updateRotorMassMatrix()

##  kinematic parametors 

    def setRotorPositionAndVelocity(self, Q, DQ, DDQ=None):
        self.Q = Q
        self.DQ = DQ
        if not DDQ is None:
            self.DDQ = DDQ

    def getRotorPositionAndVelocity(self):
        return self.Q, self.DQ
    
    def _getKinematicParametorsAtAxialCordinateDZ(self, DZ):

        distance = DZ - self.GZ
        Q = np.zeros((self.dof,))
        DQ = np.zeros((self.dof,))
        
        Q[0] = self.Q[0] + distance*self.Q[3]
        Q[1] = self.Q[1] - distance*self.Q[2]
        Q[2] = self.Q[2]
        Q[3] = self.Q[3]

        DQ[0] = self.DQ[0] + distance*self.DQ[3]
        DQ[1] = self.DQ[1] - distance*self.DQ[2]
        DQ[2] = self.DQ[2]
        DQ[3] = self.DQ[3]
        
        return Q, DQ
    
##  dyanmic forces function and its derivative

    def _updateTorqueAtCenterOfMassGz(self, F, DZ):

        distance = DZ - self.GZ
        F[2] = - distance*F[1]
        F[3] = distance*F[0]
        
        return F
    
    def functionForce(self, inst, dt, Q, DQ):
        """
        the total exterior forces for rotor have been calculated at the center of mass GZ
        """
        ### Force
        self.totalForce = np.zeros((self.dof, ))
        self.setRotorPositionAndVelocity(Q, DQ)
        
        # # gravity force
        # vect_gravity = [9.81, 0.0, 0.0, 0.0]
        # Fgrav = np.dot( self.M, vect_gravity  )
        # self.totalForce += Fgrav

        # linear bearing force
        for brg in self.brg_list :
            brgQ, brgDQ = self._getKinematicParametorsAtAxialCordinateDZ( brg.DZ )
            brg.computeLinearBearingForce( brgQ, brgDQ )
            brgF = self._updateTorqueAtCenterOfMassGz( brg.getForce() , brg.DZ )
            self.totalForce += brgF

        # unbalance or harmonic force
        for unb in self.unb_list :
            unb.computeUnbalanceForce(self.omega, inst)
            unbF = self._updateTorqueAtCenterOfMassGz( unb.getForce() , unb.DZ )
            self.totalForce += unbF

        return self.totalForce

    def functionDerivativeForce(self, dt, Q, DQ):
        pass




