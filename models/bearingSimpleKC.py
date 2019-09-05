# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
import os,sys

from models.bearingComponentBuilder import BearingBuilder


class SimpleKCBearing(BearingBuilder):

    def __init__(self, Omega, Ra):
        BearingBuilder.__init__( self, Omega, Ra )
        self.K = np.zeros((2,2))
        self.C = np.zeros((2,2))
    
    def readBearingDynamicCoefficientFile(self, filename):

        coefDyna_List = np.genfromtxt( filename )[0,:]

        self.K[0,0] = coefDyna_List[1]
        self.K[0,1] = coefDyna_List[2]
        self.K[1,0] = coefDyna_List[3]
        self.K[1,1] = coefDyna_List[4]

        self.C[0,0] = coefDyna_List[5]
        self.C[0,1] = coefDyna_List[6]
        self.C[1,0] = coefDyna_List[7]
        self.C[1,1] = coefDyna_List[8]



