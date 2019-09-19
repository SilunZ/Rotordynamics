# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets, QtCore
from interface.ui_rotorWidget import Rotor
from interface.ui_bearingWidget import BearingWidget

from functools import partial


class Ui_MainForm(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('ORACode')
        self.resize(800, 600)
       
        # creat mainMenu
        self._setMenu()

        # creat main layout
        self.mainLayout = QtWidgets.QVBoxLayout()

        # creat tabs
        self._setTabs()


        # creat Lower banner
        self._setLowerBanner()

        # central widget of QMainWindow
        centralWidget = QtWidgets.QDialog()
        centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(centralWidget)

        self.show()
    
    def _setMenu(self):

        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('File')
       
        # Exit application Button
        exitButton = QtWidgets.QAction( QtGui.QIcon('exit.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)        
        self.fileMenu.addAction(exitButton)

    def _setLowerBanner(self):
        
        # creat lower banner buttons
        self.nextButton = QtWidgets.QPushButton("Next")
        self.backButton = QtWidgets.QPushButton("Back")
        self.resetButton = QtWidgets.QPushButton("Reset")
        self.applyButton = QtWidgets.QPushButton("Apply")

        self.nextButton.clicked.connect(partial(self._manageTabs, 1))
        self.backButton.clicked.connect(partial(self._manageTabs, -1))
        self.applyButton.clicked.connect( self._manageApplyButtonAction )

        # Lower banner
        bannerLayout = QtWidgets.QHBoxLayout()
        bannerLayout.addStretch(1)
        bannerLayout.addWidget(self.backButton)
        bannerLayout.addWidget(self.nextButton)
        bannerLayout.addWidget(self.applyButton)
        bannerLayout.addWidget(self.resetButton)

        # set bannerLayout to the main layout
        self.mainLayout.addLayout(bannerLayout)
    
    def _setTabs(self):
        
        tabsLayout = QtWidgets.QVBoxLayout()

        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget()

        #### tab 1 : " rotor setting"
        tab1Layout = QtWidgets.QGridLayout()

        # set model choice box
        modelChoiceBox = QtWidgets.QGroupBox(" Rotor model : ")
        layout = QtWidgets.QHBoxLayout()
        radioButton1 = QtWidgets.QRadioButton("Jeffcott model ")
        radioButton2 = QtWidgets.QRadioButton("4-degree-of-freedow model")
        radioButton3 = QtWidgets.QRadioButton("Finite element model")
        layout.addWidget(radioButton1)
        layout.addWidget(radioButton2)
        layout.addWidget(radioButton3)
        layout.addStretch(1)
        modelChoiceBox.setLayout(layout)

        self.rotSetting = Rotor()
        # self.rotSetting2 = Rotor()
        # self.rotSetting3 = Rotor()
        tab1Layout.addWidget(modelChoiceBox, 0, 0, 1, 1)
        tab1Layout.addWidget(self.rotSetting, 1, 0)
        # tab1Layout.addWidget(self.rotSetting2, 2, 0)
        # tab1Layout.addWidget(self.rotSetting3, 0, 1, 3, 1)

        tab1 = QtWidgets.QWidget()
        tab1.setLayout(tab1Layout)
  
        #### tab 2 : " bearing setting"
        tab2 = QtWidgets.QWidget()
        tab3 = QtWidgets.QWidget()
        tab4 = QtWidgets.QWidget()
        tab5 = QtWidgets.QWidget()
        
        # Add tabs
        self.tabs.addTab(tab1," Rotor ")
        self.tabs.addTab(tab2," Bearing ")
        self.tabs.addTab(tab3," Calculation setting ")
        self.tabs.addTab(tab4," Solve ")
        self.tabs.addTab(tab5," Results ")

        # Add tabs to widget
        tabsLayout.addWidget(self.tabs)
        self.mainLayout.addLayout(tabsLayout)
    
##  ##

    def _manageApplyButtonAction(self):

        self.rotSetting.applyButtonAction()
    

    def _manageTabs(self, step=0):

        tabIndex = self.tabs.currentIndex()
        if self.nextButton.isEnabled() and step == 1:
            # move to next tab
            tabIndex += 1
            self.tabs.setCurrentIndex(tabIndex)
            self._manageTabs(0)

        if self.backButton.isEnabled() and step == -1:
            # move to back tab 
            tabIndex -= 1
            self.tabs.setCurrentIndex(tabIndex)
            self._manageTabs(0)




