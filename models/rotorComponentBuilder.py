# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np


class BasicRotorBuilder():

    def __init__(self, Omega, Ra_ext, Ra_int = 0.0):
        self.setRotationSpeed( Omega )
        self.setRadius( Ra_ext, Ra_int)
    
    def setRotationSpeed(self, Omega):
        self.Omega = Omega                  # tr/min
        self.omega = Omega * np.pi/30.0     # rad/s
        self.period = np.abs( 60.0 / Omega )
    
    def setRadius(self, Ra_ext, Ra_int):
        self.Ra_ext = Ra_ext
        self.Ra_int = Ra_int


class DiscBuilder():

    def __init__(self, L_disc, Re_disc, Ri_disc, rho_disc):
        self.L = L_disc
        self.Re = Re_disc
        self.Ri = Ri_disc
        self.rho = rho_disc
        
        # computation operations below are performed in the disc local marker
        self.computeMass()
        self.computeMomentOfInertia()
        self.MatM = np.zeros((6,6))

    def computeMass(self):
        """ 
        calculate the disc mass as self.mass
        """
        self.mass = np.pi * ( self.Re**2 - self.Ri**2 ) * self.L * self.rho
    
    def computeMomentOfInertia(self):
        """
        Ixx, Iyy are the moments of inertia ; Izz is the polar moment of inertia
        """
        self.Ixx = 1.0/4.0 * np.pi * ( self.Re**4 - self.Ri**4 )
        self.Iyy = 1.0/4.0 * np.pi * ( self.Re**4 - self.Ri**4 )
        self.Izz = 1.0/2.0 * np.pi * ( self.Re**4 - self.Ri**4 )
    
    def setDiscAxialCoordinate(self, DZ):
        """
        axial position DZ in the global marker
        """
        self.DZ = DZ


class UnbalanceBuilder():

    def __init__(self, amp, phase=0.0):
        """
        """
        self._Um = amp*np.exp( phase*180.0/np.pi )
        self.force = np.zeros((4,))
    
    def setAxialCoordinate(self, DZ):
        """
        axial position DZ in the global marker
        """
        self.DZ = DZ 

    def computeUnbalanceForce(self, omega, inst):
        angle = np.angle(self._Um)
        w =  omega
        
        self.force[0] = w**2 * abs(self._Um)* np.cos( w*inst + angle )
        self.force[1] = w**2 * abs(self._Um)* np.sin( w*inst + angle )

    def getForce(self):
        return self.force

