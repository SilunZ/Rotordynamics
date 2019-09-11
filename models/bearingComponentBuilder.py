# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np


class BasicBearingBuilder():

    def __init__(self, Omega, Ra):
        self.setRotationSpeed( Omega )
        self.setRadius( Ra )
    
    def setRotationSpeed(self, Omega):
        self.Omega = Omega                  # tr/min
        self.omega = Omega * np.pi/30.0     # rad/s
        self.period = np.abs( 60.0 / Omega )
    
    def setRadius(self, Ra):
        self.Ra = Ra
    
