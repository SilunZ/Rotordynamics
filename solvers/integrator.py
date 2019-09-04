# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
import matplotlib.pyplot as plt



class Integrator():

    def __init__(self, dof, f, df):

        self.n = dof
        self.funforce = f
        self.fundf = df

        self.N = 2 * self.n
        self._Javailable = False

        self.Q0 = np.zeros((self.n,))
        self.DQ0 = np.zeros_like(self.Q0)
        self.DDQ0 = np.zeros_like(self.Q0)
        self.Q = np.zeros_like(self.Q0)
        self.DQ = np.zeros_like(self.Q0)
        self.DDQ = np.zeros_like(self.Q0)


    def _setConvergenceCriteria(self, tol=1e-3, Iter=100):
        
        self._tol = tol
        self._maxIter = Iter




