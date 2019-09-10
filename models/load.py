# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np

class Load():
    """
    Generic class representing a load
    """
    def __init__(self, node_name, dof):
        self.node_name = node_name # ex. Z0N1
        self.compo = np.zeros((dof,))  # ex. DX, DY, DZ, DRX, DRY, DRZ
        
        self.indof = [] #inlet dofs
        self.outdof = [] #outlet dofs

        self._displacementDependent = False
        self._velocityDependent = False
        self._accelerationDependent = False

    def isDisplacementDependent(self):
        return self._displacementDependent

    def isVelocityDependent(self):
        return self._velocityDependent

    def isAccelerationDependent(self):
        return self._accelerationDependent


class HarmonicLoad(Load):
##
    def __init__(self, node_name, dof, amp, phase):

        Load.__init__(self, node_name, dof)
        self.amp = amp
        self.phase = phase

    def getForce(self, phi, dphi, ddphi, time):
        """
        return harmonic (umbalance) forces
        phi = omega * t
        dphi = omega
        """
        # mult = dphi**2 * NP.cos(phi + self.phase) + ddphi * NP.sin(phi + self.phase)
        mult = dphi**2 * np.cos(dphi*time + self.phase) + ddphi * np.sin(dphi*time + self.phase)

        self.lastF = [self.amp * mult, ]
        
        return self.lastF


