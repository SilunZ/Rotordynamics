# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np


class RotorBuilder():

    def __init__(self, Omega, Ra):
        self.setRotationSpeed( Omega )
        self.setRadius( Ra )
    
    def setRotationSpeed(self, Omega):
        self.Omega = Omega                  # tr/min
        self.omega = Omega * np.pi/30.0     # rad/s
        self.period = np.abs( 60.0 / Omega )
    
    def setRadius(self, Ra):
        self.Ra = Ra


class DiscBuilder():

    def __init__(self, L_disc, Re_disc, Ri_disc, rho_disc):
        self.L = L_disc
        self.Re = Re_disc
        self.Ri = Ri_disc
        self.rho = rho_disc
        
        # computation operations below are performed in the disc local marker
        self.computeMass()
        self.computeMomentOfInertia()

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


