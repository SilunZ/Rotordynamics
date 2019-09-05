# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
import os,sys

from bearingComponentBuilder import BearingBuilder


class SimpleKCBearing(BearingBuilder):

    def __init__(self, Omega, Ra):
        BearingBuilder.__init__( self, Omega, Ra )
    
    def setBearingStiffness(self):
        pass 

    def setBearingDamping(self):
        pass 
    
    def readBearingDynamicCoefficientFile(self):


        # sys.path.append(os.path.realpath('..'))

        fichier = np.genfromtxt("test.txt")
        print np.genfromtxt("test.txt", comments="#")
        pass
