# -*- coding: utf-8 -*-

"""
DESCRIPTION: Plant linearization widgets

DATE OF CREATION/AUTHOR : 16/10/2018 B.Lecointre

Siemens Industry Software SAS
7 place des Minimes
42300 Roanne - France
tel: (33).04.77.23.60.30
fax: (33).04.77.23.60.31
www.siemens.com/plm

Copyright 2018 Siemens Industry Software NV
"""

import traceback
from PySide2 import QtCore, QtGui, QtWidgets
# import apps
# import AME
from amesim import *
import amepyplot
import numpy as np
import scipy.optimize as opt
from scipy import signal
from scipy.linalg import inv, hessenberg
import glob, time, cPickle, os
from utils import *



class PlantLin(QtWidgets.QGroupBox):
    """
    Plant linearization widget
    """

    # Define signals
    plotRequest = QtCore.Signal()

    def __init__(self, data):
        super(PlantLin, self).__init__()
        """
        Set up widget layout
        """
        self.filename = data.filename

        # Instantiations
        self.inputList = QtWidgets.QComboBox()
        self.outputList = QtWidgets.QComboBox()
        self.resList = QtWidgets.QComboBox()
        self.tLinList = QtWidgets.QComboBox()
        self.inputList.AdjustToMinimumContentsLength
        self.outputList.AdjustToMinimumContentsLength
        self.light = TrafficLight()
        self.message = QtWidgets.QLabel()
        msgstyle = "QLabel {color: darkGrey}"
        self.message.setStyleSheet(msgstyle)
        self.message.setAlignment(QtCore.Qt.AlignRight)

        iconRefresh = QtGui.QPixmap(os.path.dirname(__file__) + "/images/update_pix16.png")
        iconImport = QtGui.QPixmap(os.path.dirname(__file__) + "/images/file_browser_pix16.png")
        self.dataButton = QtWidgets.QToolButton()
        self.dataButton.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.dataButton.clicked.connect(self.initUI)           # default action if clicked
        self.dataButton.setIcon(iconRefresh)
        self.dataButton.setText("Refresh")
        menu = QtWidgets.QMenu(self.dataButton)
        menu.addAction(iconImport, "Import open-loop...", self.importModel)
        self.dataButton.setMenu(menu)
        self.dataButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.dataButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.dataButton.setToolTip('"Refresh": reload simulation results\n'
                                   '"Import": load .jac file of an open-loop SISO model')


        # Tooltips
        self.inputList.setToolTip('Select control variable connected to PID port 3 (e.g. "setpoint").\n\n'
                                  'If not in the list, turn L.A. status of port 3 to "control" and\n'
                                  'update simulation.')
        self.outputList.setToolTip('Select observer connected to PID port 1 (e.g. "actual").\n\n'
                                   'If not in the list, turn L.A. status of port 1 to "observer"\n'
                                   'and update simulation.')

        # Layout
        self.setTitle("Plant linearization")
        groupLayout = QtWidgets.QVBoxLayout()

        pic = apps.APPWidgets.Image()
        pic.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/images/IOpic.png"))
        pic.setScaledContents(0)
        pic.setAlignment(QtCore.Qt.AlignCenter)
        pic.setToolTip('Make sure PID port 2 "plant value" is connected directly\n'
                       'to plant output without any scaling.')
        groupLayout.addWidget(pic)

        layout = QtWidgets.QGridLayout()
        labels = ['control setpoint', 'plant value', 'result set', 'linearization time']
        for i in range(0, 4):
            lab = QtWidgets.QLabel('%s' % (labels[i]))
            layout.addWidget(lab, i , 0)
        layout.addWidget(self.inputList, 0, 1)
        layout.addWidget(self.outputList, 1, 1)
        layout.addWidget(self.resList, 2, 1)
        layout.addWidget(self.tLinList, 3, 1)
        layout.addWidget(self.dataButton, 4, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(0, 110)
        groupLayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.light)
        layout.addWidget(self.message)
        groupLayout.addLayout(layout)
        groupLayout.addStretch(1)
        self.setLayout(groupLayout)

        # Slots
        self.inputList.activated.connect(self.selectInput)
        self.outputList.activated.connect(self.selectOutput)
        self.resList.activated.connect(self.updateTlinList)
        self.tLinList.activated.connect(self.calcClosedLoop)

        # Default values
        self.status = 0     # 0: no data, 1: bad data, 2: data ok

    def initUI(self):
        """ load last saved set, set up with default otherwise """

        data = self.window()

        try:
           # populate lists with available .jac files
           self.scanJac()

           # restore previous settings if any
           if  data.appObject.hasAttribute("plantLinSettings"):
               s = data.appObject.loadAttribute("plantLinSettings")
               settings = cPickle.loads(str(s))
               if settings["inputItem"] != -1:
                   # restore settings (unless previous was using external import, then using default)
                   self.inputList.setCurrentIndex(settings["inputItem"])
                   self.outputList.setCurrentIndex(settings["outputItem"])
                   self.resList.setCurrentIndex(settings["resItem"])
                   self.tLinList.setCurrentIndex(settings["tLinItem"])
                   # load selected .jac and proceed with calculations
                   self.calcClosedLoop()
        except:
           # clean-up UI
           self.inputList.clear()
           self.outputList.clear()
           self.resList.clear()
           self.tLinList.clear()
           self.inputList.setEnabled(False)
           self.outputList.setEnabled(False)
           self.resList.setEnabled(False)
           self.tLinList.setEnabled(False)
           self.light.setLight(0)
           self.message.setText("Linearization data not ok")
           self.matchIO = 0
           self.light.setLight(0)
           self.waitbar.close()

    def updateTlinList(self):
        """ Update list of linearization times from selected result file """
        self.tLinList.setEnabled(True)
        res = self.resList.currentText()
        clist = []
        for i in range(0, len(self.jacRes)):
            if self.jacRes[i] == res:
                clist.append(self.jacTlin[i])
        self.tLinList.clear()
        self.tLinList.addItems(clist)
        if len(clist) > 1:
            self.tLinList.setCurrentIndex(1)  # do not show t=0.0 by default if there are others
        self.tLinList.setStyleSheet("")
        if len(clist) == 1:
            self.tLinList.setEnabled(False)
        self.calcClosedLoop()

    def selectInput(self):
        """
        highlight input on the sektch and move to next step
        """
        var = self.inputList.currentText()
        alias, aliasSub = getalias(self.filename, var)
        try:
            AME.AMEHighlightComponent(aliasSub)
        except:
            pass
        self.calcClosedLoop()

    def selectOutput(self):
        """
        highlight output on the sektch and move to next step
        """
        var = self.outputList.currentText()
        alias, aliasSub = getalias(self.filename, var)
        try:
            AME.AMEHighlightComponent(aliasSub)
        except:
            pass
        self.calcClosedLoop()

    def scanJac(self):
        """
        Scan existing .jac files, look for I/O match from ref set
        Return lists of results sets, tlin, I/Os
        """
        data = self.window()

        # start waitbar
        self.waitbar = QtWidgets.QProgressDialog()
        self.waitbar.setWindowTitle("PID tuner")
        self.waitbar.setLabelText("Loading data...")
        self.waitbar.setRange(0, 100)
        self.waitbar.show()
        self.waitbar.setValue(0)
        QtCore.QCoreApplication.processEvents()

        # reset styles for comboboxes
        self.inputList.clear()
        self.outputList.clear()
        self.resList.clear()
        self.tLinList.clear()
        self.inputList.setEnabled(True)
        self.outputList.setEnabled(True)
        self.resList.setEnabled(True)
        self.tLinList.setEnabled(True)

        # search for available .jac files and open them to get linearization time
        (jacFiles, jacRes, jacTlin) = ([], [], [])
        linmodeErr = 0
        linmodePar = data.appObject.paramProvider().getParamLink("linmode@#").getTitle()
        (info1, info2, info3, info4, info5, info6) = AME.AMEGetAliasInfos("#")
        Files = glob.glob(self.filename + "_.jac*")
        matchIO = 0
        for i, file in enumerate(Files):
            tmp = file.find(".jac") + 4
            tmp2 = file[tmp:].split(".")
            if len(tmp2) == 1:
                # "ref" run
                n, linmode = amegetp(self.filename, info3, info4, linmodePar)
                if n == []:
                    linmodeErr += 1
                elif int(linmode[0]) == 1:
                    jacRes.append("ref")
                else:
                    linmodeErr += 1
            else:
                # batch run
                n, linmode = amegetp(self.filename, info3, info4, linmodePar, tmp2[1])
                if n == []:
                    linmodeErr += 1
                elif int(linmode[0]) == 1:
                    jacRes.append(tmp2[1])
                else:
                    linmodeErr += 1

            if (n != []) and (int(linmode[0]) == 1):
                dir = os.path.dirname(data.appObject.execDir().decode('utf-8'))
                [A, B, C, D, x, u, y, t, xvals] = ameloadjNoprint(dir, file)  # get lin. time and var. names for IO check
                jacFiles.append(file)
                jacTlin.append('%s s' % (repr(t)))

            # Search for control and observer in "u" and "y" (which provide "output variables", whereas observer
            # and control inside the PID are "input variable", hence need to find connected variable)
            if (matchIO == 0) and (n != []) and (int(linmode[0]) == 1):
                (ufilt, yfilt) = ([], [])
                # search control setpoint
                (gtype, galias, gport) = AME.AMEGetConnectionInformation('#', 2)
                if gtype == "CONNECTION_LINE":
                    (gtype, galias, gport) = AME.AMEGetConnectionInformation(galias, np.mod(gport + 1, 2))
                if gtype == "CONNECTION_COMPONENT":
                    aliasu = AME.AMEGetVariablesOnPort(galias, gport)[0]
                    (tmp1, tmp2, gtitle, gunit, tmp5) = AME.AMEGetVariableInfos(aliasu)
                    (tmp1, tmp2, subname, subinst, tmp5, tmp6) = AME.AMEGetAliasInfos(galias)
                    uvarname = subname + " instance " + str(subinst) + " " + gtitle
                    lenv = len(uvarname)
                for sig in u:
                    if sig[0:lenv] == uvarname:
                        ufilt.append(sig)

                # search plant value
                (gtype, galias, gport) = AME.AMEGetConnectionInformation('#', 0)
                if gtype == "CONNECTION_LINE":
                    (gtype, galias, gport) = AME.AMEGetConnectionInformation(galias, np.mod(gport + 1, 2))
                if gtype == "CONNECTION_COMPONENT":
                    aliasy = AME.AMEGetVariablesOnPort(galias, gport)[0]
                    (tmp1, tmp2, gtitle, gunit, tmp5) = AME.AMEGetVariableInfos(aliasy)
                    (tmp1, tmp2, subname, subinst, tmp5, tmp6) = AME.AMEGetAliasInfos(galias)
                    yvarname = subname + " instance " + str(subinst) + " " + gtitle
                    lenv = len(yvarname)
                for sig in y:
                    if sig[0:lenv] == yvarname:
                        yfilt.append(sig)

                if len(ufilt) == 1 and len(yfilt) == 1:
                    matchIO = 1
            self.waitbar.setValue(int(90 * i / len(Files)))

        # check if required data is available and usable, return error otherwise
        error = 0
        if len(jacFiles) == 0:
            # no valid .jac file
            error = 1
        elif len(u) == 0 or len(y) == 0:
            # .jac file found without I/O names
            error = 2
        elif "ref" not in jacRes:
            # nof ref set
            error = 3
        if error > 0:
            # show error message, specific tooltip and return
            self.waitbar.close()
            self.light.setLight(0)
            self.message.setText("Linearization data not ok")
            self.message.setToolTip('Most common root causes:\n'
                                    '1. Linear analysis status at port 1 and 3 is not set to "observer" and '
                                    '"control"\n'
                                    '2. "linearization behavior" parameter is not set to "pid tuner compatible"\n'
                                    '3. The plant runs into saturation. Reduce excitation, controller gain or select'
                                    '\n     a linearization point where no saturation occurs\n'
                                    '4. Reference run is not up to date. Execute a "single run" again\n\n'
                                    'If the "plant estimate" was previously identified, this warning can be ignored\n'
                                    'and tuning might be resumed from the "PID tuning" tab')
            # last: ask for plot update
            self.status = 0
            self.plotRequest.emit()
            return

        self.status = 2
        self.jacFiles = jacFiles
        self.jacRes = jacRes
        self.jacTlin = jacTlin
        self.matchIO = matchIO

        # populate inputs and outputs list
        if len(ufilt) > 0:
            u = ufilt  # restrict displayed list to matching signals
        if len(yfilt) > 0:
            y = yfilt  # restrict displayed list to matching signals
        self.inputList.addItems(u)
        self.outputList.addItems(y)
        if len(u) == 1:
            self.inputList.setEnabled(False)
        if len(y) == 1:
            self.outputList.setEnabled(False)

        # populate "res" combo box
        self.message.setText("Plant import ok")
        clist = list(set(jacRes))  # remove duplicates for display
        clist.sort()
        self.resList.clear()
        self.resList.addItems(clist)
        ii = []
        if "ref" in clist:
            ii = clist.index("ref")
            self.resList.setCurrentIndex(ii)  # set to "ref" by default
        if len(clist) == 1:
            self.resList.setEnabled(False)
        self.waitbar.setValue(90)
        self.waitbar.setLabelText("Update analysis...")
        self.updateTlinList()
        self.waitbar.close()

    def importModel(self):
        """
        Import open-loop SISO model (.jac file)
        include simplified ameloadj code that doesn't look into other auxiliary files (e.g. .la)
        """

        # turn off inputs
        self.inputList.clear()
        self.outputList.clear()
        self.resList.clear()
        self.tLinList.clear()
        self.inputList.setEnabled(False)
        self.outputList.setEnabled(False)
        self.resList.setEnabled(False)
        self.tLinList.setEnabled(False)

        # file selection widget
        cwd = os.path.dirname(self.filename)
        dlg = QtWidgets.QFileDialog(self, 'Select .jac file of open-loop, SISO model',
                                    cwd, '*.jac*')
        dlg.exec_()
        file = dlg.selectedFiles()
        if len(file) == 0:
            # loading canceled, back to start
            self.initUI()
            return
        else:
            # load file (using simplified version of ameloadj to restrict parsing to .jac file only)
            try:
                A, B, C, D = ameloadjlight(file[0])
                B = B[0]
                D = D[0]
                A = np.matrix(A)
                B = np.matrix(B)
                C = np.matrix(C)
                D = np.matrix(D)
                # Use Hessenberg decomposition to improve computation robustness for large systems

                H, Q = hessenberg(A, calc_q=True)
                H = np.matrix(H)
                Q = np.matrix(Q)
                ol = signal.lti(H, Q.H * B, C * Q, D)
                # ol = signal.lti(A, B, C, D)

                # save and plot
                self.OL = ol
                self.matchIO = 1
                self.light.setLight(2)
                self.resList.addItem(os.path.basename(file[0]))
                self.message.setText("File imported successfully")

                # move to next step with checkPlant
                self.checkPlant()

            except:
                # show error message and return
                errorDlg = ErrorDlg(4, os.path.basename(file[0]))
                errorDlg.exec_()
                self.initUI()
                return

    def calcClosedLoop(self):
        """
        load inputs from linearization and make closed-loop transfer function
        """
        # load selected .jac file
        res = self.resList.currentText()
        tlin = self.tLinList.currentText()
        for i in range(0, len(self.jacFiles)):
            if self.jacRes[i] == res and self.jacTlin[i] == tlin:
                file = self.jacFiles[i]

        data = self.window()
        dir = os.path.dirname(data.appObject.execDir().decode('utf-8'))
        [A, B, C, D, x, u, y, t, xvals] = ameloadjNoprint(dir, file)
        B = B[0]
        D = D[0]
        A = np.matrix(A)
        B = np.matrix(B)
        C = np.matrix(C)
        D = np.matrix(D)

        # retrieve selected input and output
        tu = self.inputList.currentText()
        iu = u.index(tu)
        ty = self.outputList.currentText()
        iy = y.index(ty)

        # reshape to SISO model from selected input and output
        B = B[:, iu]
        C = C[iy, :]
        D = np.matrix(D[iy, iu])

        # Use Hessenberg decomposition to improve computation robustness for large systems
        H, Q = hessenberg(A, calc_q=True)
        H = np.matrix(H)
        Q = np.matrix(Q)
        cl = signal.lti(H, Q.H * B, C * Q, D)

        # go to next step
        self.CL = cl
        self.calcOpenLoop()

    def calcOpenLoop(self):
        """
        compute open-loop response from closed-loop in state-space format
        :return:
        """
        # compute open-loop response
        cl = self.CL
        (a, b, c, d) = (cl.A, cl.B, cl.C, cl.D)
        a = np.matrix(a)
        b = np.matrix(b)
        c = np.matrix(c)
        d = np.matrix(d)

        tmp = float(inv(1 - d))
        A = a + b * c * tmp
        B = b + b * d * tmp
        C = c * tmp
        D = d * tmp

        # Use Hessenberg decomposition to improve computation robustness for large systems
        H, Q = hessenberg(A, calc_q=True)
        H = np.matrix(H)
        Q = np.matrix(Q)
        ol = signal.lti(H, Q.H * B, C * Q, D)
        # ol = signal.lti(A, B, C, D)

        # save
        self.OL = ol

        # move to next step with checkPlant
        self.checkPlant()

    def checkPlant(self):
        """ check that input and output are correlated and update flag """

        # compute frequency response and step response
        data = self.window()
        ref = self.OL
        fmin = data.options.values["fmin"]
        fmax = data.options.values["fmax"]
        tf = data.options.values["tfinal"]
        f1, mag1, phase1 = ss2bode(ref.A, ref.B, ref.C, ref.D, fmin=fmin, fmax=fmax)
        t1 = np.linspace(0, tf, 1000)
        [t1, y1] = signal.step(ref, T=t1)
        y1 = np.real(y1)

        # update quality flag
        self.message.setToolTip("")
        if (len(f1) == 0) or any(np.isnan(mag1)) or any(np.isinf(mag1)):
            self.light.setLight(0)
            self.message.setText("Linearization data not ok")
            self.message.setToolTip('Most common root causes:\n'
                                    '1. Linear analysis status at port 1 and 3 is not set to "observer" and '
                                    '"control"\n'
                                    '2. "linearization behavior" parameter is not set to "pid tuner compatible"\n'
                                    '3. The plant runs into saturation. Reduce excitation, controller gain or select'
                                    '\n     a linearization point where no saturation occurs\n'
                                    '4. Reference run is not up to date. Execute a "single run" again\n\n'
                                    'If the "plant estimate" was previously identified, this warning can be ignored\n'
                                    'and tuning might be resumed from the "PID tuning" tab')
            self.status = 0
        elif self.matchIO == 0:
            self.light.setLight(1)
            self.message.setText("Can't confirm setpoint and output")
            self.status = 1
        else:
            self.light.setLight(2)
            self.message.setText("Linearization data ok")
            self.status = 2

        # last: ask for plot update
        self.plotRequest.emit()

class ModelFit(QtWidgets.QGroupBox):
    """
    Model fitting parameters widget
    """

    # Define signals
    plotRequest = QtCore.Signal()

    def __init__(self):
        super(ModelFit, self).__init__()

        # Instantiations
        clist = ["none", "1st order", "2nd order", "integrator", "1st order + integrator",
                 "double integrator"]
        self.fitType = QtWidgets.QComboBox()
        self.fitType.addItems(clist)
        self.modelPic = QtWidgets.QLabel()
        self.fitParLabel0 = QtWidgets.QLabel("gain [dB]")
        self.fitParLabel1 = QtWidgets.QLabel("natural frequency [Hz]")
        self.fitParLabel2 = QtWidgets.QLabel("damping ratio [-]")
        self.fitParLabel3 = QtWidgets.QLabel("...")
        self.fitParValue0 = QtWidgets.QLineEdit("")
        self.fitParValue1 = QtWidgets.QLineEdit("")
        self.fitParValue2 = QtWidgets.QLineEdit("")
        self.fitParValue3 = QtWidgets.QLineEdit("")
        self.fitParValue0.setAlignment(QtCore.Qt.AlignRight)
        self.fitParValue1.setAlignment(QtCore.Qt.AlignRight)
        self.fitParValue2.setAlignment(QtCore.Qt.AlignRight)
        self.fitParValue3.setAlignment(QtCore.Qt.AlignRight)
        self.findBestButton = QtWidgets.QPushButton("Find best estimate")
        self.fitParButton = QtWidgets.QPushButton("Fit parameters")
        self.light = TrafficLight()
        self.message = QtWidgets.QLabel()
        msgstyle = "QLabel {color: darkGrey}"
        self.message.setStyleSheet(msgstyle)
        self.message.setAlignment(QtCore.Qt.AlignRight)

        # Layout
        self.setTitle("Plant estimate")
        groupLayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.modelPic, 0, 0, 1, 2)
        layout.addWidget(QtWidgets.QLabel("model type"), 1, 0)
        layout.addWidget(self.fitType, 1, 1)

        layout.addWidget(self.fitParLabel0, 2, 0)
        layout.addWidget(self.fitParLabel1, 3, 0)
        layout.addWidget(self.fitParLabel2, 4, 0)
        # layout.addWidget(self.fitParLabel3, 5, 0)
        layout.addWidget(self.fitParValue0, 2, 1)
        layout.addWidget(self.fitParValue1, 3, 1)
        layout.addWidget(self.fitParValue2, 4, 1)
        # layout.addWidget(self.fitParValue3, 5, 1)
        layout.addWidget(self.fitParButton, 5, 1)
        layout.addWidget(self.findBestButton, 6, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(0, 110)
        groupLayout.addLayout(layout)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.light)
        self.light.setLight(0)
        layout.addWidget(self.message)
        groupLayout.addLayout(layout)
        groupLayout.addStretch(1)
        self.setLayout(groupLayout)

        # Slots
        self.fitType.activated.connect(self.updateFitType)
        self.fitParValue0.editingFinished.connect(self.checkInputs)
        self.fitParValue1.editingFinished.connect(self.checkInputs)
        self.fitParValue2.editingFinished.connect(self.checkInputs)
        self.fitParValue3.editingFinished.connect(self.checkInputs)
        self.fitParButton.clicked.connect(self.fitModel)
        self.findBestButton.clicked.connect(self.findBest)

        # Default values
        self.status = 0

        # Tooltips
        self.fitType.setToolTip('Select model type that best fit plant response within frequency\n'
                                'range of interest. PID tuning will be based on this model.\n\n'
                                'Use "Fit" for automatic identification and/or edit coefficients.')
        self.fitParButton.setToolTip("Fit automatically model parameters.\n\n"
                                  "For best identification performance, define frequency\n"
                                  "and time range of interest in App/Options (fmin, fmax, tfinal)")
        self.findBestButton.setToolTip("Search for best model type and parameters.\n\n"
                                     "For best identification performance, define frequency\n"
                                     "and time range of interest in App/Options (fmin, fmax, tfinal)")
        self.fitParLabel0.setToolTip("= 20.log10( k )")
        self.fitParLabel1.setToolTip(u"= 1 / ( 2.\u03C0.\u03C4 )\n with \u03C4 in [s]")
        self.fitParLabel2.setToolTip(u"= \u03B6")
        self.fitParLabel3.setToolTip(u"= 1 / ( 2.\u03C0.\u03B2 )\n with \u03B2 in [s]\n")

        # Expression evaluator
        self.evaluator = apps.kernel.Evaluator()

    def initUI(self):
        """ load last saved set, set up with default otherwise """

        # reset UI
        self.fitType.setCurrentIndex(0)
        self.light.setLight(0)
        self.message.setText("")

        # load data if existing
        data = self.window()
        try:
            # restore previous settings if any
            s = data.appObject.loadAttribute("modelFitSettings")
            settings = cPickle.loads(str(s))
            self.fitType.setCurrentIndex(settings["fitItem"])
            self.modParam = settings["modParam"]
        except:
            fmin = data.options.values["fmin"]
            fmax = data.options.values["fmax"]
            f0 = 10 ** ((np.log10(fmin) + np.log10(fmax)) / 2.)
            tmp = [0, f0, 0.01, f0 * 2]
            self.modParam = np.matrix([tmp, tmp, tmp, tmp, tmp, tmp])
            self.message.setText("Select model type")
        self.updateFitType()

    def updateFitType(self):
        """
        Update UI upon selected model type by enabling / disabling matching fields
        Refresh inputs
        """
        modType = self.fitType.currentIndex()
        modParam = self.modParam
        if modType > 0:
            self.fitParLabel0.setEnabled(True)
            self.fitParValue0.setEnabled(True)
            self.fitParValue0.setText(("%6g" % (modParam[modType, 0])).strip())
        else:
            self.fitParLabel0.setEnabled(False)
            self.fitParValue0.setEnabled(False)
            self.fitParValue0.setText("")
        if modType in [1, 2, 4]:
            self.fitParLabel1.setEnabled(True)
            self.fitParValue1.setEnabled(True)
            self.fitParValue1.setText(("%6g" % (modParam[modType, 1])).strip())
        else:
            self.fitParLabel1.setEnabled(False)
            self.fitParValue1.setEnabled(False)
            self.fitParValue1.setText("")
        if modType == 2:
            self.fitParLabel2.setEnabled(True)
            self.fitParValue2.setEnabled(True)
            self.fitParValue2.setText(("%6g" % (modParam[modType, 2])).strip())
        else:
            self.fitParLabel2.setEnabled(False)
            self.fitParValue2.setEnabled(False)
            self.fitParValue2.setText("")
        # last parameter is unused (provision for more models)
        self.fitParLabel3.setEnabled(False)
        self.fitParValue3.setEnabled(False)
        self.fitParValue3.setText("")

        # show model equation
        picname = "/images/model" + str(modType) + ".png"
        self.modelPic.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + picname))
        self.modelPic.setScaledContents(0)
        self.modelPic.setAlignment(QtCore.Qt.AlignCenter)

        data = self.window()
        if modType > 0 and data.plantLin.status >= 1:
            self.fitParButton.setEnabled(True)
            self.findBestButton.setEnabled(True)
        else:
            self.fitParButton.setEnabled(False)
            self.findBestButton.setEnabled(False)

        # go to next step
        self.checkInputs()

    def checkInputs(self):
        """
        Check input validity, proceed with model assembly and plot if data is ok
        """
        modType = self.fitType.currentIndex()
        modParam = self.modParam
        errStyle = "QLineEdit {color: red}"
        data = self.window()
        self.evaluator.setExternalContext(data.appObject.circuitNameId())

        # gain
        if self.fitParValue0.isEnabled():
            val = self.evaluator.getExpressionValue(self.fitParValue0.text())
            err = self.evaluator.hasError()
            if (err == False) and (val > -1.0e30) and (val < 1.0e30):
                self.fitParValue0.setText(str(val))
                self.fitParValue0.setStyleSheet("")
                modParam[modType, 0] = val
            else:
                self.fitParValue0.setStyleSheet(errStyle)
                self.light.setLight(0)
                self.message.setText("Gain is undefined")
                self.status = 0
                self.plotRequest.emit()
                return

        # natural frequency
        if self.fitParValue1.isEnabled():
            val = self.evaluator.getExpressionValue(self.fitParValue1.text())
            err = self.evaluator.hasError()
            if (err == False) and (val > 1.0e-12) and (val < 1.0e30):
                self.fitParValue1.setText(str(val))
                self.fitParValue1.setStyleSheet("")
                modParam[modType, 1] = val
            else:
                self.fitParValue1.setStyleSheet(errStyle)
                self.light.setLight(0)
                self.message.setText("Natural frequency must be > 0")
                self.status = 0
                self.plotRequest.emit()
                return

        # damping ratio
        if self.fitParValue2.isEnabled():
            val = self.evaluator.getExpressionValue(self.fitParValue2.text())
            err = self.evaluator.hasError()
            if (err == False) and (val > 0.) and (val < 1.0e30):
                self.fitParValue2.setText(str(val))
                self.fitParValue2.setStyleSheet("")
                modParam[modType, 2] = val
            else:
                self.fitParValue2.setStyleSheet(errStyle)
                self.light.setLight(0)
                self.message.setText("Damping ratio must be >= 0")
                self.status = 0
                self.plotRequest.emit()
                return

        self.modParam = modParam  # update saved values

        # update traffic light and message if parameters are ok
        if modType == 0:
            self.light.setLight(0)
            self.message.setText("Select model type")
            self.status = 0
        else:
            self.light.setLight(2)
            self.message.setText("")
            self.status = 1
            self.updateModel()      # update model

        # update plot (note that self.plotPlant can append message and change traffic light)
        self.plotRequest.emit()

    def updateModel(self):
        """ update model numerator and denominator """
        modType = self.fitType.currentIndex()
        modParam = self.modParam

        k = 10**(modParam[modType, 0]/20)
        tau = 1 / (2 * np.pi * modParam[modType, 1])
        dz = modParam[modType, 2]
        b = 1 / (2 * np.pi * modParam[modType, 3])
        if modType == 0:
            num = 0
            den = 1
        elif modType == 1:
            num = k
            den = [tau, 1]
        elif modType == 2:
            num = k
            den = [tau * tau, 2 * dz * tau, 1]
        elif modType == 3:
            num = k
            den = [1, 0]
        elif modType == 4:
            num = k
            den = [tau, 1, 0]
        elif modType == 5:
            num = k
            den = [1, 0, 0]
        sys = signal.lti(num, den)
        self.model = sys

    def fitModel(self):
        """
        try to fit model on plant data
        update final cost function for use in batch with findBest
        """
        data = self.window()

        # exit if plant model is not valid
        if data.plantLin.status == 0:
            self.message.setText("Plant data not ok, can't fit it")
            self.light.setLight(1)
            self.modelFitRes = 1e3      # dummy NRMSD value (reminder: 0 is perfect fit)
            return

        self.message.setText("Fitting in progress...")
        self.light.setLight(1)

        # generic fitting parameters
        tic = time.time()
        timeout = 15                # max duration in [s] for fitting one model
        dzmin = 0.001               # min damping ratio for fitting
        a = 2
        dzmax = (1 + 10 ** a) / (2 * np.sqrt(10 ** a))  # max damping to capture 2 time constants in a=2 decades)


        # force UI update (otherwise wait for optimization completion)
        QtCore.QCoreApplication.processEvents()
        if QtCore.QCoreApplication.hasPendingEvents():
            QtCore.QCoreApplication.processEvents()

        # retrieve data and options
        ref = data.plantLin.OL
        modType = self.fitType.currentIndex()
        modParam = self.modParam
        fmin = data.options.values["fmin"]
        fmax = data.options.values["fmax"]
        tf = data.options.values["tfinal"]
        maxIter = data.options.values["maxIter"]
        tolx = data.options.values["tolx"]
        fitTarget = data.options.values["fitTarget"]

        # compute properties of the plant
        f1, mag1, phase1 = ss2bode(ref.A, ref.B, ref.C, ref.D, fmin=fmin, fmax=fmax)
        if len(f1) == 0:
            self.message.setText("Plant data not ok, can't fit it")
            self.light.setLight(1)
            self.modelFitRes = 1e3  # dummy NRMSD value (reminder: 0 is perfect fit)
            return
        fmin = np.max([fmin, np.min(f1)])       # in case there are NaN in Bode computation
        fmax = np.min([fmax, np.max(f1)])
        t1 = np.linspace(0, tf, 1000)
        [t1, y1] = signal.step(ref, T=t1)
        y1 = np.real(y1)
        i = np.nonzero(np.isfinite(y1))
        t1 = t1[i]
        y1 = y1[i]

        # Identify gain
        # Numerical approach to deal with tentatively poor conditioning of A which prevent from inverting it
        # Starts at fmin * 10 and move down decade per decade until a flat gain decade is found
        # Performs zero cancellation automatically (in case of pure integrator(s))
        fa = fmin * 10
        fb = 10 * fa
        kdB = np.nan
        while fa > data.tol:
            f_, m_, p_ = ss2bode(ref.A, ref.B, ref.C, ref.D, fmin=fa, fmax=fb, N=10)
            intOrder = 0
            while intOrder < 5:
                mi_ = m_ + intOrder * 20 * np.log10(2 * np.pi * f_)
                mavg = np.mean(mi_)
                sigma = np.std(mi_)
                if sigma < 0.01:
                    kdB = mavg  # gain change is standard deviation is < ?? dB within this decade
                    break       # constant. gain is taken as average value from those 3 points
                else:
                    intOrder += 1
            if not np.isnan(kdB):
                break           # exit identification loop
            fa /= 10
            fb = 10 * fa
        if np.isnan(kdB):
            self.message.setText("Gain identification failed, prefer manual fitting")
            self.light.setLight(0)
            self.modelFitRes = 1e3  # set dummy NRMSD value (reminder: 0 is perfect fit)
            return
        self.fitParValue0.setText(("%6g" % (kdB)).strip())
        modParam[modType, 0] = kdB

        # identify dynamic parameters
        # pick up actual inputs as starting values, normalize and define bounds
        tmp = np.array(modParam[modType, :])[0]
        bnd = []
        x0 = []

        if modType in [3, 5]:
            # for pure integrator type, no other parameter to identify
            # however, run simulation to evaluate fitting error (for find best feature)
            if fitTarget == 0:
                J = simFit([], modType, kdB, fmin, fmax, dzmin, dzmax, t1, y1, [], [], tic, timeout)
            elif fitTarget == 1:
                J = simFit([], modType, kdB, fmin, fmax, dzmin, dzmax, [], [], f1, mag1, tic, timeout)
            else:
                J = simFit([], modType, kdB, fmin, fmax, dzmin, dzmax, t1, y1, f1, mag1, tic, timeout)
            self.modelFitRes = J
            self.modParam = modParam
            self.checkInputs()
            self.message.setText("Fitting completed with %2.1f %% match" %(data.plotPlant.matchIndex))
            if data.plotPlant.matchIndex < 50:
                self.light.setLight(1)
            else:
                self.light.setLight(2)
            return
        else:
            # natural frequency (bounded between fmin and fmax)
            bnd.append((0., 1.))
            x0_ = (tmp[1] - fmin) / (fmax - fmin)
            x0_ = np.min([1., np.max([0., x0_])])
            x0.append(x0_)
        if modType == 2:
            # damping (bounded between 1e-3 and value to capture 2 time constants in a=2 decades)
            bnd.append((0., 1.))
            x0_ = (tmp[2] - dzmin) / (dzmax - dzmin)
            x0_ = np.min([1., np.max([0., x0_])])
            x0.append(x0_)

        cstr = [{'type': 'ineq', 'fun': lambda x: np.min(x)},
                {'type': 'ineq', 'fun': lambda x: 1.0 - np.max(x)}]

        if fitTarget == 0:
            # fit on step response
            args = (modType, kdB, fmin, fmax, dzmin, dzmax, t1, y1, [], [], tic, timeout)
        elif fitTarget == 1:
            # fit on gain curve
            args = (modType, kdB, fmin, fmax, dzmin, dzmax, [], [], f1, mag1, tic, timeout)
        else:
            # fit on both step response and gain curve
            args = (modType, kdB, fmin, fmax, dzmin, dzmax, t1, y1, f1, mag1, tic, timeout)

        res = opt.minimize(simFit, x0=x0,
                           args=args,
                           method='COBYLA',
                           options={'disp': False, 'rhobeg': 0.02, 'tol': tolx,
                                    'maxiter': maxIter, 'catol': 0.},
                           constraints=cstr)
        # opt.show_options('minimize', method='cobyla')
        self.modelFitRes = res["fun"]           # final cost function
        if res['success']:
            # unscale and apply parameters
            x = res['x']
            if modType not in [3, 5]:
                # natural frequency (bounded between fmin and fmax)
                fo = (fmax - fmin) * x[0] + fmin
                modParam[modType, 1] = fo
                self.fitParValue1.setText(("%6g" % (fo)).strip())
            if modType == 2:
                # damping (bounded between 0.001 and value to capture 2 time constants in a=2 decades)
                dz = (dzmax - dzmin) * x[1] + dzmin
                modParam[modType, 2] = dz
                self.fitParValue2.setText(("%6g" % (dz)).strip())
            self.modParam = modParam
            self.checkInputs()
            self.message.setText("Fitting completed with %2.1f %% match" % (data.plotPlant.matchIndex))
            if data.plotPlant.matchIndex < 50:
                self.light.setLight(1)
            else:
                self.light.setLight(2)
        else:
            self.modParam = modParam            # apply gain only, let others to default or previous
            self.modelFitRes = 1e3              # set dummy NRMSD value (reminder: 0 is perfect fit)
            self.checkInputs()
            self.message.setText(res["message"])
            self.light.setLight(0)

    def findBest(self):
        """
        Attempt to identify and fit best model from the list automatically
        Running a batch over all possible models and retains the best one
        """

        # start waitbar
        self.waitbar = QtWidgets.QProgressDialog()
        self.waitbar.setWindowTitle("PID tuner")
        self.waitbar.setLabelText("Auto-fitting...")
        self.waitbar.setRange(0, 100)
        self.waitbar.show()
        self.waitbar.setValue(0)
        QtCore.QCoreApplication.processEvents()

        J = []
        k = 0
        testList = [1, 2, 3, 4, 5]
        for i in testList:
            k += 1.
            self.fitType.setCurrentIndex(i)
            self.fitModel()
            J.append(self.modelFitRes)
            self.waitbar.setValue(int(k / (len(testList) + 1.) * 100))
            self.waitbar.show()
        ii = np.argmin(J, axis=0)
        ij = testList[ii]
        self.fitType.setCurrentIndex(ij)
        self.updateFitType()
        self.waitbar.close()
        data = self.window()
        if J[ii] >= 1000:
            msg = "Auto-fitting failed, prefer manual fitting"
            self.light.setLight(1)
        else:
            msg = "Search completed with %2.1f %% match" %(data.plotPlant.matchIndex)
        self.message.setText(msg)

class PlotPlant(QtWidgets.QGroupBox):
    """
    Open-loop plot widget and compute match index when the 2 curves exist
    """

    def __init__(self):
        super(PlotPlant, self).__init__()

        # Instantiations
        self.plot = amepyplot.PlotWidget()
        self.plot.addRow()
        self.plot.addRow()
        self.matchIndex = np.nan

        # Layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.plot)
        self.setLayout(layout)
        self.setTitle("Open-loop response")

        # Slots (internal)

    def updateUI(self):
        plotRef = False
        plotFit = False
        self.matchIndex = np.nan
        data = self.window()
        if (data.plantLin.status == 0) and (data.modelFit.status == 0):
            # no data to plot, clean-up and exit
            for i in range(0, 3):
                graph = self.plot.getGraph(i, 0)
                amepyplot.Graph.clear(graph)
            return
        if data.plantLin.status >= 1:
            ref = data.plantLin.OL
            plotRef = True
        if data.modelFit.status == 1:
            fit = data.modelFit.model
            plotFit = True

        # plot options
        fmin = data.options.values["fmin"]
        fmax = data.options.values["fmax"]
        tf = data.options.values["tfinal"]

        # computations for plant model
        if plotRef:
            f1, mag1, phase1 = ss2bode(ref.A, ref.B, ref.C, ref.D, fmin=fmin, fmax=fmax)
            if len(f1) == 0:
                # if all-NaN, abort plotRef
                plotRef = False
            else:
                t1 = np.linspace(0, tf, 1000)
                [t1, y1] = signal.step(ref, T=t1)
                y1 = np.real(y1)

        # computation for model estimate
        if plotFit:
            if plotRef:
                f2 = f1
            else:
                n1 = np.log10(fmin)
                n2 = np.log10(fmax)
                f2 = np.logspace(n1, n2, 200)
            w = 2*np.pi*f2
            w2, mag2, phase2 = signal.bode(fit, w=w)

            if plotRef:
                t2 = t1
            else:
                t2 = np.linspace(0, tf, 1000)
            [t2, y2] = signal.step(fit, T=t2)
            y2 = np.real(y2)

        # compute match index and append plant estimate message
        if plotRef and plotFit:
            fitTarget = data.options.values["fitTarget"]
            if fitTarget == 0:
                # index from step response
                val, tmp = matchIndex(t1, y1, y2)
            elif fitTarget == 1:
                # index from gain curve
                val, tmp = matchIndex(f1, mag1, mag2)
            else:
                # mixed index
                val1, tmp1 = matchIndex(t1, y1, y2)
                val2, tmp2 = matchIndex(f1, mag1, mag2)
                val = val1 * val2

            if not np.isfinite(val):
                val = 0
            self.matchIndex = val * 100

            # update Plant estimate message with match index
            data.modelFit.message.setText("%2.1f %% match" %(self.matchIndex))
            if self.matchIndex < 50:
                data.modelFit.light.setLight(1)
            else:
                data.modelFit.light.setLight(2)
        elif plotFit:
            data.modelFit.light.setLight(1)
            data.modelFit.message.setText("")
        else:
            data.modelFit.light.setLight(0)
            data.modelFit.message.setText("Select model type")

        legPos = amepyplot.GUI.INSIDE_BOTTOM_LEFT
        displayRef = amepyplot.Display2DLine()
        displayRef.configure(lineColor=QtGui.QColor(15, 130, 135), lineThickness=2)
        displayFit = amepyplot.Display2DLine()
        displayFit.configure(lineColor=QtGui.QColor(235, 120, 10), lineThickness=1.5, lineStyle=QtCore.Qt.DashLine)

        # Bode / gain
        graph = self.plot.getGraph(0, 0)
        amepyplot.Graph.clear(graph)
        if plotRef:
            itemX = amepyplot.Item(f1, title="frequency", unit="Hz")
            itemY = amepyplot.Item(mag1, title="linearized plant", unit="")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayRef)
            graph.addCurve(curve)
        if plotFit:
            itemX = amepyplot.Item(f2, title="frequency", unit="Hz")
            itemY = amepyplot.Item(mag2, title="plant estimate", unit="")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayFit)
            graph.addCurve(curve)
        graph.xAxis().setLogScale(1)
        graph.setTitle('Gain [dB]')
        graph.configureTitles(showTitle=True, legendPosition=legPos, showLegend=True)


        # Bode / phase
        graph = self.plot.getGraph(1, 0)
        amepyplot.Graph.clear(graph)
        if plotRef:
            itemX = amepyplot.Item(f1, title="frequency", unit="Hz")
            itemY = amepyplot.Item(phase1, title="linearized plant", unit="deg")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayRef)
            graph.addCurve(curve)
        if plotFit:
            itemX = amepyplot.Item(f2, title="frequency", unit="Hz")
            itemY = amepyplot.Item(phase2, title="plant estimate", unit="deg")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayFit)
            graph.addCurve(curve)
        graph.xAxis().setLogScale(1)
        graph.setTitle('Phase [degree]')
        graph.configureTitles(showTitle=True, legendPosition=legPos, showLegend=False)

        # step response
        graph = self.plot.getGraph(2, 0)
        amepyplot.Graph.clear(graph)
        if plotRef:
            itemX = amepyplot.Item(t1, title="time", unit="s")
            itemY = amepyplot.Item(y1, title="lin. plant", unit="null")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayRef)
            graph.addCurve(curve)
        if plotFit:
            itemX = amepyplot.Item(t2, title="time", unit="s")
            itemY = amepyplot.Item(y2, title="plant est.", unit="null")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayFit)
            graph.addCurve(curve)
        graph.setTitle('Step response')
        graph.configureTitles(showTitle=True, legendPosition=legPos, showLegend=False)
        self.plot.updateGraphs()
