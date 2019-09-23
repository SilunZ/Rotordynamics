# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets, QtCore

from interface.ui_rotorWidget import Rotor
from interface.ui_bearingWidget import Bearing
from interface.ui_analysisWidget import Analysis
from interface.ui_resolutionWidget import Resolution
from interface.ui_postProcessingWidget import PostProcessing


from functools import partial


class Ui_MainForm(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('ORACode')
        # self.resize(1280, 1024)
        self.resize(800, 600)
       
        self.mainLayout = QtWidgets.QVBoxLayout()  # creat main layout
        self._setMenu()  # creat mainMenu              
        self._setTabs()  # creat tabs
        self._setLowerBanner()  # creat Lower banner

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

##  creat lower banner
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

##  creat Tab and Tabs
    def _setTabs(self):
        
        # init the tabs concer
        self._tabs_list = []
        self.tabsLabel_list = ["Rotor", "Bearing", "Analysis", "Resolution", "Post-processing"]
        self._tabLayout_list = []

        # set the tab one by one
        self._setTab1()
        self._setTab2()
        self._setTab3()
        self._setTab4()
        self._setTab5()

        # creat tabs in main layout
        self.tabs = QtWidgets.QTabWidget()
        for i, label in enumerate(self.tabsLabel_list):
            self._tabs_list.append( QtWidgets.QWidget() )
            self._tabs_list[i].setLayout( self._tabLayout_list[i] )
            self.tabs.addTab(self._tabs_list[i], label)

        # Add tabs to widget
        tabsLayout = QtWidgets.QVBoxLayout()
        tabsLayout.addWidget(self.tabs)
        self.mainLayout.addLayout(tabsLayout)

    def _setTab1(self):

        #### tab 1 : " rotor setting"
        
        self.rotSetting = Rotor()

        #     # set model choice box
        # modelChoiceBox = QtWidgets.QGroupBox(" Rotor model : ")
        # layout = QtWidgets.QHBoxLayout()
        # radioButton1 = QtWidgets.QRadioButton("Jeffcott model ")
        # radioButton2 = QtWidgets.QRadioButton("4-degree-of-freedow model")
        # radioButton3 = QtWidgets.QRadioButton("Finite element model")
        # layout.addWidget(radioButton1)
        # layout.addWidget(radioButton2)
        # layout.addWidget(radioButton3)
        # layout.addStretch(1)
        # modelChoiceBox.setLayout(layout)

            # deployment
        tab1Layout = QtWidgets.QGridLayout()
        # tab1Layout.addWidget(modelChoiceBox, 0, 0, 1, 1)
        tab1Layout.addWidget(self.rotSetting, 1, 0)

        self._tabLayout_list.append( tab1Layout )

    def _setTab2(self):
        """
        tab 2 : " Bearing setting"
        """
        self.brgSetting = Bearing()

            # set model choice box
        modelChoiceBox = QtWidgets.QGroupBox(" Bearing model : ")
        layout = QtWidgets.QHBoxLayout()
        radioButton1 = QtWidgets.QRadioButton("Stiffness-damping model ")
        radioButton2 = QtWidgets.QRadioButton("Isothermal model")
        radioButton3 = QtWidgets.QRadioButton("ThermoHydroDynamic(THD) model")
        radioButton4 = QtWidgets.QRadioButton("ThermoElastoHydroDynamic(TEHD) model")
        layout.addWidget(radioButton1)
        layout.addWidget(radioButton2)
        layout.addWidget(radioButton3)
        layout.addWidget(radioButton4)
        layout.addStretch(1)
        modelChoiceBox.setLayout(layout)

        tab2Layout = QtWidgets.QGridLayout()
        tab2Layout.addWidget(modelChoiceBox, 0, 0, 1, 1)
        tab2Layout.addWidget(self.brgSetting, 1, 0)
        
        self._tabLayout_list.append( tab2Layout )

    def _setTab3(self):
        """
        tab 3 : " Analysis setting"
        """
        self.analySetting = Analysis()

        # set model choice box
        choiceBox = QtWidgets.QGroupBox(" Analysis setting : ")
        layout = QtWidgets.QHBoxLayout()
        radioButton1 = QtWidgets.QRadioButton(" Transient analysis ")

        layout.addWidget(radioButton1)

        layout.addStretch(1)
        choiceBox.setLayout(layout)

        tab3Layout = QtWidgets.QGridLayout()
        tab3Layout.addWidget(choiceBox, 0, 0, 1, 1)
        tab3Layout.addWidget(self.analySetting, 1, 0)
        
        self._tabLayout_list.append( tab3Layout )

    def _setTab4(self):
        """
        tab 4 : " Resolution  "
        """
        self.solve = Resolution()

        tab4Layout = QtWidgets.QGridLayout()
        tab4Layout.addWidget(self.solve, 1, 0)

        self._tabLayout_list.append( tab4Layout )

    def _setTab5(self):
        """
        tab 5 : " Post-processing  "
        """
        self.pst = PostProcessing( self.solve )

        tab5Layout = QtWidgets.QGridLayout()
        # tab5Layout.addWidget(plotBox, 0, 0, 1, 1)
        tab5Layout.addWidget(self.pst, 1, 0)

        # self.addToolBar(NavigationToolbar(static_canvas, self))

        self._tabLayout_list.append( tab5Layout )

##  

    def _manageApplyButtonAction(self):
        
        tabIndex = self.tabs.currentIndex()
        if tabIndex == 0:
            self.rotSetting.RotorModelWidgets.applyButtonAction()
        elif tabIndex == 1:
            self.brgSetting.applyButtonAction()
        if tabIndex == 2:
            self.analySetting.applyButtonAction()
        if tabIndex == 3:
            self.solve.click_SetButtonAction()
        if tabIndex == 4:
            self.pst.applyButtonAction()

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




