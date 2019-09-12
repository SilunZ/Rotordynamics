# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"


import numpy as np


import matplotlib.pyplot as plt
t_vect = simu.resu["time"]
pos_vect = simu.resu["position"]
converganceItera_vect = simu.resu["convergeItera"]
converganceError_vect = simu.resu['convergeError']

plt.figure()
plt.subplot(221)
plt.plot( t_vect, pos_vect[:,0:2])
plt.subplot(222)
plt.plot( pos_vect[:,1], pos_vect[:,0] )
plt.subplot(223)
plt.plot( t_vect, converganceError_vect)
plt.subplot(224)
plt.plot( t_vect, converganceItera_vect)
plt.show()
