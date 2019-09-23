
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
import numpy as np


from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class PostProcessing( QtWidgets.QMainWindow ):
    """
    description : pass
    """ 
    def __init__(self, simulation):
        
        super( PostProcessing, self).__init__()
        
        self.simulation = simulation
        self.resuDataAvail = False

        # Types of results
        self.labels_list = ['Displacements', 'Velocity', 'Trajectory']

        # set results data box
        self.LoadResuButton = QtWidgets.QPushButton(" Load the simulation results")
        self.LoadResuButton.clicked.connect( self.loadSimulationResultData )

        # set plot choice combobox
        self.plotChoiceBox = QtWidgets.QComboBox()
        for i, label in enumerate(self.labels_list):
            self.plotChoiceBox.addItem(label)
        self.plotChoiceBox.activated[str].connect(self._manageComboBoxPlots)

        # set plot box
        self._static_canvas = FigureCanvas(Figure(figsize=(5, 3)))

        # set post processing layout
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.addWidget( self.LoadResuButton, 0, 0)
        self.mainLayout.addWidget( self.plotChoiceBox, 0, 1)
        self.mainLayout.addWidget( self._static_canvas, 1, 0, 1, 2)

        centralWidget = QtWidgets.QDialog()
        centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(centralWidget)
    
    def loadSimulationResultData(self):

        if self.simulation.resuDataAvail == True:
            self.resultsData = self.simulation.simu.resu
            print ("You are ready to go to plot the results.")
        else:
            print ("please run the simulation at first.")


    @pyqtSlot()
    def applyButtonAction(self):
        pass

    def _manageComboBoxPlots(self):
        
        plotsComboBoxIndex = self.plotChoiceBox.currentIndex()
        if plotsComboBoxIndex == 0 :
            self._static_canvas.figure.clear()

            self._static_ax = self._static_canvas.figure.subplots()
            
            x = self.resultsData["time"]
            y = self.resultsData["position"]
            self._static_ax.plot(x, y, "-")

            self._static_canvas.figure.canvas.draw()
            print ("Displacement!!!")
            
        elif plotsComboBoxIndex == 1 :
            self._static_canvas.figure.clear()

            self._static_ax = self._static_canvas.figure.subplots()
            
            x = self.resultsData["time"]
            y = self.resultsData["convergeItera"]
            self._static_ax.plot(x, y, "-")

            self._static_canvas.figure.canvas.draw()
            print ("Velocity!!!")

        elif plotsComboBoxIndex == 2 :
            self._static_canvas.figure.clear()
            
            self._static_ax = self._static_canvas.figure.subplots()
            x = self.resultsData["position"][:,0]
            y = self.resultsData["position"][:,1]
            self._static_ax.plot(x, y, ".")
            
            self._static_canvas.figure.canvas.draw()
            print ("Trajectory!!!")
