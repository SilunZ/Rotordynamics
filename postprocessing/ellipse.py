# -*- coding: utf-8 -*-

__author__="MA HASSINI (mohamed-amine.hassini@edf.fr)"

import numpy as np


class Ellipse:


    def __init__(self,mx,my):
        self.__mx=mx
        self.__my=my
        self.__nPoints=180
        self.__ga,self.__pa=self.__getAxes()
        pass

    def getAxes(self):
        return self.__ga,self.__pa


    def setNPoints(self,num):
        self.__nPoints=num
        return True

    def getNPoints(self):
        return self.__nPoints


    def getCurve(self,npoints=180,tour=360.0):
        xr=np.real(self.__mx)
        xi=np.imag(self.__mx)
        yr=np.real(self.__my)
        yi=np.imag(self.__my)

        t=tour/180*np.pi
        angle=np.linspace(0,t,npoints)
        x=np.cos(angle)*np.real(self.__mx)-np.sin(angle)*np.imag(self.__mx)
        y=np.cos(angle)*np.real(self.__my)-np.sin(angle)*np.imag(self.__my)
        return x,y

    def getSkewness(self):
        angx=np.angle(self.__mx)
        angy=np.angle(self.__my)
        diffang=(angx-angy)%(2.0*np.pi)
        resu=np.linalg.norm(self.__pa)/np.linalg.norm(self.__ga)
        if diffang>0 and diffang<np.pi:
            resu=-resu
        return resu

    def getPrecession(self):
        res=self.getSkewness()
        if res<0:return "BW"
        return "FW"
        pass

    def isBackward(self):
        res=self.getSkewness()
        if res<0:return True
        return False

    def isForward(self):
        return not self.isBackward();


    def __getAxes(self):

        A=np.zeros((2,2))
        A[0,0]=np.real(self.__mx)
        A[0,1]=np.imag(self.__mx)
        A[1,0]=np.real(self.__my)
        A[1,1]=np.imag(self.__my)

        U,S,V=np.linalg.svd(A)

        ga=np.zeros((2,1))
        pa=np.zeros((2,1))

        ga[0,0]=S[0]
        pa[1,0]=S[1]

        #start transformation
        ga=np.dot(U,ga)
        pa=np.dot(U,pa)


        return ga,pa

