# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"


import numpy as np


value = 1.0
M = np.zeros((2,2))
M[0,0] = value
M[1,1] = value

k = 1e+6
K = np.zeros((2,2))
K[0,0] = k
K[0,1] = 0.0
K[1,0] = 0.0
K[1,1] = k

c = 1000.0
C = np.zeros((2,2))
C[0,0] = c
C[0,1] = 0.0
C[1,0] = 0.0
C[1,1] = c

# name_fichier = "test.txt"
# resuFichier = open( name_fichier, 'w')
# resuFichier.write( "#{0}\t   {1}\t  {2}\t  {3}\t  {4}\t  {5}\t  {6}\t  {7}\t  {8}\n" \
#            .format("Omega", "Kxx", "Kxy", "Kyx", "Kyy", "Cxx", "Cxy", "Cyx", "Cyy",) )


# resuFichier.write("{0:.1f}\t {1:.1f}\t {2:.1f}\t {3:.1f}\t {4:.1f}\t {5:.1f}\t {6:.1f}\t {7:.1f}\t {8:.1f}\n"\
#            .format( 1000.00, K[0,0],   K[0,1],   K[1,0],   K[1,1],   C[0,0],   C[0,1],  C[1,0],   C[1,1] ) )
# resuFichier.write("{0:.1f}\t {1:.1f}\t {2:.1f}\t {3:.1f}\t {4:.1f}\t {5:.1f}\t {6:.1f}\t {7:.1f}\t {8:.1f}\n"\
#            .format( 1000.00, K[0,0],   K[0,1],   K[1,0],   K[1,1],   C[0,0],   C[0,1],  C[1,0],   C[1,1] ) )
# resuFichier.write("{0:.1f}\t {1:.1f}\t {2:.1f}\t {3:.1f}\t {4:.1f}\t {5:.1f}\t {6:.1f}\t {7:.1f}\t {8:.1f}\n"\
#            .format( 1000.00, K[0,0],   K[0,1],   K[1,0],   K[1,1],   C[0,0],   C[0,1],  C[1,0],   C[1,1] ) )



# resuFichier.close()

fichier = np.genfromtxt("test.txt")
print np.genfromtxt("test.txt", comments="#")
