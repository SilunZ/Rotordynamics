# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import numpy as np
from solvers.integrator import Integrator


class Newmark_Integrator( Integrator ):

    def __init__(self, dof, M, funforce, fundf, gamma=0.5, beta=0.25):
        
        Integrator.__init__(self, dof, funforce)
        self.setConvergenceCriteria(self)
        self.setRelaxCoef(rlx = 1.0)

        self.fundf = fundf
        self._gamma = gamma
        self._beta = beta
        self.invM = np.linalg.inv(M)
        self._J = np.zeros((self.N, self.N))
        self._R = np.zeros((self.N,))
        self._converganceErr = 0.0
        self._converganceItera = 0

    def setRelaxCoef(self, rlx):
        self.rlx = rlx
    
    def integrateOneTimeStep(self, t0, t1):

        n = self.n
        beta = self._beta
        gamma = self._gamma
        
        dt = t1 - t0
        self.Q = self.Q0
        self.DQ = self.DQ0
        self.DDQ = self.DDQ0

        self._converganceItera = 0
        while 1:

            #compute the acceleration
            force = self.funforce(t1, dt, self.Q, self.DQ)
            self.DDQ = np.dot(self.invM, force)

            #compute the vector residuel
            self.Q  =  self.Q0  + dt * self.DQ0 + 0.5 * dt**2 * ( (1.0 - 2. * beta) * self.DDQ0 + 2.0 * beta * self.DDQ )
            self.DQ =  self.DQ0 + dt * ( (1.0 - gamma) * self.DDQ0 + gamma * self.DDQ )

            self._R[0:n] = self.Q - self.Q0
            self._R[n::] = self.DQ - self.DQ0

            
            #compute the convergence err and the correction increment U.
            self._converganceErr = np.linalg.norm(self._R)
            self._converganceItera += 1
            
            if (self._converganceErr < self._tol) or (self._converganceItera > self._maxIter):
                break
        
            
            

        self.Q0 = self.Q
        self.DQ0 = self.DQ
        self.DDQ0 = self.DDQ
        
        return True
    
    def getIntegratedDisplacementAndVelocity(self):
        return self.Q, self.DQ
    
    def getErrorConvergence(self):
        return self._converganceErr

    def getIteraBeforeConvergence(self):
        return self._converganceItera


