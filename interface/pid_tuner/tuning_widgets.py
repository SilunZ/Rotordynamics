# -*- coding: utf-8 -*-

"""
DESCRIPTION: PID tuning widgets

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
import apps
import AME
import numpy as np
import glob, cPickle
from amesim import *
import amepyplot
from plant_widgets import *
from utils import *

class Tuning(QtWidgets.QWidget):
    """
    PID tuning widget
    """
    def __init__(self, data):
        super(Tuning, self).__init__()
        """
        Set up widget layout
        """
        self.filename = data.filename

        # Instantiations
        msgStyle = "QLabel {color: darkGrey}"
        titleStyle = "QLabel {color: rgb(120, 135, 145); font: bold}"
        titleStyleR = "QRadioButton {color: rgb(120, 135, 145); font: bold}"
        
        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.fPid = QtWidgets.QLineEdit("")
        self.fPidLabel = QtWidgets.QLabel("tuning frequency [Hz]")
        self.autoButton = QtWidgets.QRadioButton("Model-based tuning")
        self.editButton = QtWidgets.QRadioButton("Manual tuning")
        self.kPLabel = QtWidgets.QLabel("proportional gain [-]")
        self.kILabel = QtWidgets.QLabel("integral gain [-]")
        self.kDLabel = QtWidgets.QLabel("derivative gain [-]")
        self.fDLabel = QtWidgets.QLabel("cutoff freq. for d/dt [Hz]")
        self.kP = QtWidgets.QLineEdit("")
        self.kI = QtWidgets.QLineEdit("")
        self.kD = QtWidgets.QLineEdit("")
        self.fD = QtWidgets.QLineEdit("")
        self.gainMargin = QtWidgets.QLabel("")
        self.phaseMargin = QtWidgets.QLabel("")
        self.modelType = QtWidgets.QLabel("")
        self.linPlant = QtWidgets.QLabel("")
        self.fPid.setAlignment(QtCore.Qt.AlignRight)
        self.kP.setAlignment(QtCore.Qt.AlignRight)
        self.kI.setAlignment(QtCore.Qt.AlignRight)
        self.kD.setAlignment(QtCore.Qt.AlignRight)
        self.fD.setAlignment(QtCore.Qt.AlignRight)
        self.gainMargin.setAlignment(QtCore.Qt.AlignRight)
        self.phaseMargin.setAlignment(QtCore.Qt.AlignRight)
        self.modelType.setAlignment(QtCore.Qt.AlignRight)
        self.modelType.setStyleSheet(msgStyle)
        self.linPlant.setAlignment(QtCore.Qt.AlignRight)
        self.linPlant.setStyleSheet(msgStyle)
        self.linPlantLight = TrafficLight()
        self.modelTypeLight = TrafficLight()

        self.light = TrafficLight()
        self.lightInfo = TrafficLight()
        self.message = QtWidgets.QLabel()
        self.messageInfo = QtWidgets.QLabel()
        self.message.setStyleSheet(msgStyle)
        self.message.setAlignment(QtCore.Qt.AlignRight)
        self.messageInfo.setStyleSheet(msgStyle)
        self.messageInfo.setAlignment(QtCore.Qt.AlignRight)

        self.plotsButton = QtWidgets.QToolButton()
        self.plotsButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        iconPlots = QtGui.QPixmap(os.path.dirname(__file__) + "/images/plot_pix16.png")
        self.plotsButton.setIcon(iconPlots)
        self.plotsButton.setText("More plots")
        self.plotsButton.setStyleSheet("background-color:white;")
        menu = QtWidgets.QMenu(self.plotsButton)
        self.plotBodeMenu = menu.addAction("Bode plots", self.plotBode)
        self.plotMarginMenu = menu.addAction("Stability margins", self.plotMargin)
        self.plotBatchMenu = menu.addAction("Stability batch", self.runBatch)
        self.plotsButton.setMenu(menu)
        self.plotsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.plot = amepyplot.PlotWidget()

        # Layout
        groupLayout = QtWidgets.QHBoxLayout()

        # left column
        leftGroup = QtWidgets.QGroupBox("PID gain synthesis")
        layout = QtWidgets.QGridLayout()
        self.autoButton.setStyleSheet(titleStyleR)
        layout.addWidget(self.autoButton, 0, 0, 1, 2)
        # layout.addWidget(QtWidgets.QLabel("closed-loop dynamic"), 1, 0, 1, 2)
        layout.addWidget(self.slider, 2, 0, 1, 2)
        layout.addWidget(self.fPidLabel, 3, 0)
        layout.addWidget(self.fPid, 3, 1)
        layout.addWidget(QtWidgets.QLabel(""), 4, 0)

        self.editButton.setStyleSheet(titleStyleR)
        layout.addWidget(self.editButton, 5, 0, 1, 2)
        layout.addWidget(self.kPLabel, 6, 0)
        layout.addWidget(self.kILabel, 7, 0)
        layout.addWidget(self.kDLabel, 8, 0)
        layout.addWidget(self.fDLabel, 9, 0)
        layout.addWidget(self.kP, 6, 1)
        layout.addWidget(self.kI, 7, 1)
        layout.addWidget(self.kD, 8, 1)
        layout.addWidget(self.fD, 9, 1)
        layout.addWidget(QtWidgets.QLabel(""), 10, 0)

        lab = QtWidgets.QLabel("Stability margins")
        lab.setStyleSheet(titleStyle)
        layout.addWidget(lab, 11, 0, 1, 3)
        lab = QtWidgets.QLabel("phase margin [degree]")
        lab.setToolTip("Recommended: 30-60°")
        layout.addWidget(lab, 12, 0)
        layout.addWidget(self.phaseMargin, 12, 1)
        lab = QtWidgets.QLabel("gain margin [dB]")
        lab.setToolTip("Recommended > 6 dB")
        layout.addWidget(lab, 13, 0)
        layout.addWidget(self.gainMargin, 13, 1)
        layout.addWidget(QtWidgets.QLabel(""), 14, 0)
        layout.addWidget(self.light, 15, 0)
        layout.addWidget(self.message, 15, 1)
        layout.addWidget(QtWidgets.QLabel(""), 16, 0)

        # FOR GAIN SCHEDULING
        lab = QtWidgets.QLabel("Gain scheduling")
        lab.setStyleSheet(titleStyle)
        self.SetMessage = QtWidgets.QLabel()
        self.SetMessage.setStyleSheet(msgStyle)
        self.SetMessage.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(lab, 17, 0, 1, 3)
        self.addSetButton = QtWidgets.QPushButton("Add tuning set")
        self.clearSetButton = QtWidgets.QPushButton("Reset GS.data")
        layout.addWidget(self.clearSetButton, 18, 0)
        layout.addWidget(self.addSetButton, 18, 1)
        layout.addWidget(self.SetMessage, 19, 0, 1, 2)

        layout.setRowStretch(20, 1)
        # /FOR GAIN SCHEDULING

        leftGroup.setLayout(layout)

        # right column
        rightGroup = QtWidgets.QGroupBox("Closed-loop response")
        layout = QtWidgets.QGridLayout()
        lab = QtWidgets.QLabel("Preview assuming time invariant plant")
        lab.setStyleSheet(msgStyle)
        layout.addWidget(lab, 0, 0, 1, 2)
        layout.addWidget(self.plotsButton,0, 2)
        layout.setAlignment(self.plotsButton, QtCore.Qt.AlignRight)
        layout.addWidget(self.plot, 1, 0, 1, 3)
        lab = QtWidgets.QLabel("Info")
        lab.setStyleSheet(titleStyle)
        layout.addWidget(lab, 2, 0, 1, 3)
        labels = ["Plant linearization", "Plant estimate", "PID gains"]
        for i in range(0, 3):
            lab = QtWidgets.QLabel('%s' % (labels[i]))
            layout.addWidget(lab, i + 3, 1)
        layout.addWidget(self.linPlant, 3, 2)
        layout.addWidget(self.modelType, 4, 2)
        layout.addWidget(self.linPlantLight, 3, 0)
        layout.addWidget(self.modelTypeLight, 4, 0)
        layout.addWidget(self.lightInfo, 5, 0)
        layout.addWidget(self.messageInfo, 5, 2)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(1, 1)

        rightGroup.setLayout(layout)
        groupLayout.addWidget(leftGroup)
        groupLayout.addWidget(rightGroup)
        groupLayout.setStretch(1, 1)

        self.setLayout(groupLayout)

        # Slots
        self.slider.valueChanged.connect(self.updateFromSlider)
        self.slider.setTracking(False)              # emits the valueChanged() signal when the user releases the
        # mouse button (unless the value happens to be the same as before). True is emitting whenever the slider is
        # being dragged
        self.fPid.editingFinished.connect(self.updateFromNum)
        self.autoButton.toggled.connect(self.updateUI)    # only one of the 2 buttons is needed (otherwise action
        # is duplication because changing one radio button toggles the other one)
        self.kP.editingFinished.connect(self.editCustom)
        self.kI.editingFinished.connect(self.editCustom)
        self.kD.editingFinished.connect(self.editCustom)
        self.fD.editingFinished.connect(self.editCustom)

        # FOR GAIN SCHEDULING
        self.addSetButton.clicked.connect(self.addTuningSet)
        self.clearSetButton.clicked.connect(self.clearTuningSet)
        # /FOR GAIN SCHEDULING

        # Default values
        self.params = [0, 1, 0, 0, 100]     # [fpid, kP, kI, kD, fD]
        self.sliderLims = [1, 100]          # Hz corresponding to 0 and 99 slider position
        self.margins = np.nan * np.array([1, 1, 1, 1])

        # Expression evaluator
        self.evaluator = apps.kernel.Evaluator()
        self.evaluator.setExternalContext(data.appObject.circuitNameId())


        # Get submodel parameters uid
        self.kPuid = data.appObject.paramProvider().getParamLink("Kp@#")
        self.kIuid = data.appObject.paramProvider().getParamLink("Ki@#")
        self.kDuid = data.appObject.paramProvider().getParamLink("Kd@#")
        self.tauDuid = data.appObject.paramProvider().getParamLink("tau@#")
        self.kSuid = data.appObject.paramProvider().getParamLink("Ks@#")

    def updateFromSlider(self):
        """
        update fPid input when user changes slider position
        """
        [fmin, fmax] = self.sliderLims
        xi = self.slider.value()
        x = np.linspace(0, 99, 100)
        f = np.logspace(np.log10(fmin), np.log10(fmax), num=100)
        fi = np.interp(xi, x, f)
        self.fPid.setStyleSheet("")
        self.fPid.setText(("%6g" % (fi)).strip())
        self.params[0] = fi

        # update gains and plot
        self.updateUI()

    def updateFromNum(self):
        """
        update slide and fPid when user changes numerical input
        """
        errStyle = "QLineEdit {color: red}"
        [fmin, fmax] = self.sliderLims
        x = np.linspace(0, 99, 100)
        f = np.logspace(np.log10(fmin), np.log10(fmax), num=100)
        val = self.evaluator.getExpressionValue(self.fPid.text())
        err = self.evaluator.hasError()
        if err:
            fPid = 0
            mode = 0
        elif val <= 0.:
            fPid = fmin
            mode = 0
        elif val < fmin:
            fPid = val
            mode = 1
        elif val > fmax:
            fPid = val
            mode = 2
        else:
            fPid = val
            mode = 1
        self.fPid.setText(str(fPid))
        if mode == 0:
            self.fPid.setStyleSheet(errStyle)
            self.light.setLight(0)
            self.message.setText("Tuning frequency error")
            self.params[0] = 0
            return
        else:
            self.fPid.setStyleSheet("")
            self.light.setLight(2)
            fs = np.max([fPid, fmin])
            fs = np.min([fs, fmax])
            xi = np.interp(fs, f, x)
        self.params[0] = fPid

        # update slider position (turn signal off for this to avoid looping with this function)
        self.slider.valueChanged.disconnect(self.updateFromSlider)
        self.slider.setValue(xi)
        self.slider.valueChanged.connect(self.updateFromSlider)

        # update gains and plot
        self.updateUI()

    def editCustom(self):
        """ Check user inputs for gains and launch simulation if ok"""

        errStyle = "QLineEdit {color: red}"

        # proportional gain
        val = self.evaluator.getExpressionValue(self.kP.text())
        err = self.evaluator.hasError()
        if (err == False) and (val > -1.0e30) and (val < 1.0e30):
            self.kP.setText(str(val))
            self.kP.setStyleSheet("")
            self.params[1] = val
        else:
            self.kP.setStyleSheet(errStyle)
            self.light.setLight(0)
            self.message.setText("Proportional gain is undefined")
            self.status = 0
            return

        # integral gain
        val = self.evaluator.getExpressionValue(self.kI.text())
        err = self.evaluator.hasError()
        if (err == False) and (val > -1.0e30) and (val < 1.0e30):
            self.kI.setText(str(val))
            self.kI.setStyleSheet("")
            self.params[2] = val
        else:
            self.kI.setStyleSheet(errStyle)
            self.light.setLight(0)
            self.message.setText("Integral gain is undefined")
            self.status = 0
            return

        # derivative gain
        val = self.evaluator.getExpressionValue(self.kD.text())
        err = self.evaluator.hasError()
        if (err == False) and (val > -1.0e30) and (val < 1.0e30):
            self.kD.setText(str(val))
            self.kD.setStyleSheet("")
            self.params[3] = val
        else:
            self.kD.setStyleSheet(errStyle)
            self.light.setLight(0)
            self.message.setText("Derivative gain is undefined")
            self.status = 0
            return

        # cutoff frequency for d/dt
        val = self.evaluator.getExpressionValue(self.fD.text())
        err = self.evaluator.hasError()
        data = self.window()
        fmin = data.options.values["fmin"]
        if (err == False) and (val > fmin) and (val < 1.0e30):
            self.fD.setText(str(val))
            self.fD.setStyleSheet("")
            self.params[4] = val
        else:
            self.fD.setStyleSheet(errStyle)
            self.light.setLight(0)
            self.message.setText("Cutoff frequency must be > %.4f" % fmin)
            self.status = 0
            return

        # go to simulation and plot
        self.plotPID()

    def modelUpdate(self):
        """
        update frequency tuning limits and initial value when model is changed
        """
        data = self.window()
        if data.modelFit.status == 0:
            # nothing to do, will be managed in updateUI
            self.updateUI()
            return

        # retrieve last tuning frequency at UI opening
        if self.fPid.text() == "":
            try:
                s = data.appObject.loadAttribute("tuningSettings")
                settings = cPickle.loads(str(s))
                fold = float(str(settings["fPid"]))
            except:
                fold = 0.
        else:
            # keep previous tuning frequency
            fold = float(str(self.fPid.text()))

        # initialize tuning frequency and limits from model's natural frequency
        modType = data.modelFit.fitType.currentIndex()
        modParam = data.modelFit.modParam
        f0 = modParam[modType, 1]
        if modType in [3, 5]:
            f1 = data.options.values["fmin"]
            f2 = data.options.values["fmax"]
            f0 = 10**( (np.log10(f1) + np.log10(f2)) / 2.)    # dummy value for pure integrator models

        klim = 20           # factor applied to f0 defining slider limits (keeping f0 centered)
        fmin = f0 / klim    # not constrained, can be any low value (but keeping slider scale usable)
        fmax = f0 * klim    # equivalent to "lambda > 0.1 * tau"
        finit = f0          # starting value for tuning (recommended from S-IMC paper)
        self.sliderLims = [fmin, fmax]

        # apply either init value or previous fit if saved
        if fold > 0.:
            finit = fold
        self.params[0] = finit

        # update slider position according to this log-scale
        x = np.linspace(0, 99, 100)
        f = np.logspace(np.log10(fmin), np.log10(fmax), num=100)
        xi = int(np.interp(finit, f, x))
        self.slider.valueChanged.disconnect(self.updateFromSlider)
        self.slider.setValue(xi)
        self.slider.valueChanged.connect(self.updateFromSlider)
        self.fPid.setText(("%6g" % (finit)).strip())

        # switch to auto tuning mode
        self.autoButton.toggled.disconnect(self.updateUI)
        self.autoButton.setChecked(True)
        self.autoButton.toggled.connect(self.updateUI)

        # update gains and plot
        self.updateUI()

    def updateUI(self):
        """
        Update UI according to active tuning mode, min/max frequencies...
        Start gain calculation and plot if active tuning mode
        """
        data = self.window()

        # update Info fields
        if data.plantLin.status <= 1:
            tmp = data.plantLin.message.text()
        else:
            tmp = 'Result set: "%s", lin. time: %s' %(data.plantLin.resList.currentText(),
                                                     data.plantLin.tLinList.currentText())
        self.linPlant.setText(tmp)
        tmp = data.modelFit.fitType.currentText()
        if data.plotPlant.matchIndex > 0:
            tmp += ", %2.1f %% match" %(data.plotPlant.matchIndex)
        self.modelType.setText(tmp)
        self.linPlantLight.setLight(data.plantLin.light.state)
        self.modelTypeLight.setLight(data.modelFit.light.state)
        self.lightInfo.setLight(1)
        self.messageInfo.setText("New parameters not applied")
        expressionInterpretor = apps.utils.ExpressionInterpretor()
        expressionInterpretor.setExternalContext(data.appObject.circuitNameId())

        # manage user mode (e.g. slider or edit mode)
        if data.plantLin.status <= 1 and data.modelFit.status == 0:
            # no plant + no model (doesn't exist, blocked by  tab manager)
            return
        elif data.plantLin.status == 2 and data.modelFit.status == 0:
            # plant OK + no model, set UI to manual edit
            self.autoButton.setEnabled(False)
            self.slider.setEnabled(False)
            self.fPidLabel.setEnabled(False)
            self.fPid.setEnabled(False)
            self.kPLabel.setEnabled(True)
            self.kILabel.setEnabled(True)
            self.kDLabel.setEnabled(True)
            self.fDLabel.setEnabled(True)
            self.kP.setEnabled(True)
            self.kI.setEnabled(True)
            self.kD.setEnabled(True)
            self.fD.setEnabled(True)
            self.autoButton.toggled.disconnect(self.updateUI)
            self.editButton.setChecked(True)
            self.autoButton.toggled.connect(self.updateUI)
            # self.slider.setProperty("value", 49)
            self.plotBodeMenu.setEnabled(True)
            self.plotMarginMenu.setEnabled(True)
            self.plotBatchMenu.setEnabled(data.plantLin.tLinList.count() > 1)
            # retrieve actual PID parameters
            tmp = [0, 0, 0, 0, 0]

            val = self.evaluator.getExpressionValue(self.kPuid.getValue())
            err = self.evaluator.hasError()
            if err:
                tmp[1] = 1
            else:
                tmp[1] = val
            val = self.evaluator.getExpressionValue(self.kIuid.getValue())
            err = self.evaluator.hasError()
            if err:
                tmp[2] = 0
            else:
                tmp[2] = val
            val = self.evaluator.getExpressionValue(self.kDuid.getValue())
            err = self.evaluator.hasError()
            if err:
                tmp[3] = 0
            else:
                tmp[3] = val
            val = self.evaluator.getExpressionValue(self.tauDuid.getValue())
            err = self.evaluator.hasError()
            if err:
                tmp[4] = 0.001
            else:
                tmp[4] = 1 / (2 * np.pi *val)
            self.params = tmp
            self.fPid.setText("")
            self.kP.setText(("%6g" % (tmp[1])).strip())
            self.kI.setText(("%6g" % (tmp[2])).strip())
            self.kD.setText(("%6g" % (tmp[3])).strip())
            self.fD.setText(("%6g" % (tmp[4])).strip())

            # go to simulation and plot
            self.plotPID()
        else:
            # plant OK + model OK, enable auto mode
            self.autoButton.setEnabled(True)

            # if no input (e.g. init of UI), force auto mode
            if not(self.autoButton.isChecked()) and not(self.editButton.isChecked()):
                self.autoButton.toggled.disconnect(self.updateUI)
                self.autoButton.setChecked(True)
                self.autoButton.toggled.connect(self.updateUI)

            # toggle input based on user choice
            if self.autoButton.isChecked():
                self.slider.setEnabled(True)
                self.fPidLabel.setEnabled(True)
                self.fPid.setEnabled(True)
                self.kPLabel.setEnabled(False)
                self.kILabel.setEnabled(False)
                self.kDLabel.setEnabled(False)
                self.fDLabel.setEnabled(False)
                self.kP.setEnabled(False)
                self.kI.setEnabled(False)
                self.kD.setEnabled(False)
                self.fD.setEnabled(False)
                self.kP.setStyleSheet("")
                self.kI.setStyleSheet("")
                self.kD.setStyleSheet("")
                self.fD.setStyleSheet("")
            else:
                self.slider.setEnabled(False)
                self.fPidLabel.setEnabled(False)
                self.fPid.setEnabled(False)
                self.kPLabel.setEnabled(True)
                self.kILabel.setEnabled(True)
                self.kDLabel.setEnabled(True)
                self.fDLabel.setEnabled(True)
                self.kP.setEnabled(True)
                self.kI.setEnabled(True)
                self.kD.setEnabled(True)
                self.fD.setEnabled(True)

            self.plotBodeMenu.setEnabled(True)
            self.plotMarginMenu.setEnabled(True)
            self.plotBatchMenu.setEnabled(data.plantLin.tLinList.count() > 1)

            # go to gain calculation (and plot afterwards)
            self.calcGains()

    def calcGains(self):
        """
        Compute PID gains from fitted model and tuned frequency
        """
        # retrieve model and parameters
        data = self.window()
        modType = data.modelFit.fitType.currentIndex()
        modParam = data.modelFit.modParam
        k = 10 ** (modParam[modType, 0] / 20)
        tau = 1 / (2 * np.pi * modParam[modType, 1])
        dz = modParam[modType, 2]
        Ndiff = data.options.values["Ndiff"]
        tuningMethod = data.options.values["tuningMethod"]        # 0: IMC, 1: S-IMC (detuned integral gain)

        # tuning frequency
        fPid = float(self.fPid.text())
        if len(self.fPid.text())==0:
            return
        lam = 1 / (2 * np.pi * fPid)

        # compute gains
        if modType == 1:
            # first order
            kc = tau / (k * lam)
            if tuningMethod == 0:
                tauI = tau
            else:
                tauI = np.min([tau, 4 * lam])
            [kP, kI, kD] = [kc, kc / tauI, 0]
        elif modType == 2:
            # 2nd order
            kc = 2 * dz * tau / (k * lam)
            if tuningMethod == 0:
                tauI = 2 * dz * tau
            else:
                r = np.roots([tau * tau, 2 * dz * tau, 1])
                tau1 = -1. / (2 * np.pi * np.real(r[0]))
                tauI = np.min([tau1, 4 * lam])
            tauD = tau / (2 * dz)
            [kP, kI, kD] = [kc, kc / tauI, kc * tauD]
        elif modType == 3:
            # integrator
            kc = 1 / (k * lam)
            if tuningMethod == 0:
                [kP, kI, kD] = [kc, 0, 0]
            else:
                tauI = 4 * lam
                [kP, kI, kD] = [kc, kc / tauI, 0]
        elif modType == 4:
            # 1st order + integrator
            kc = 1 / (k * lam)
            tauD = tau
            if tuningMethod == 0:
                [kP, kI, kD] = [kc, 0, kc * tauD]
            else:
                tauI = 4 * lam
                [kP, kI, kD] = [kc, kc / tauI, kc * tauD]
        elif modType == 5:
            # double integrator
            # if tuningMethod == 0:
            [kP, kI, kD] = [0, 0, 1 / (k * lam)]
            tauD = lam                  # for cutoff frequency
            # else:
            #     Turned off, doesn't work as indicated in the reference S-IMC paper
            #     tau2 = 1 / (data.options.values["fmin"])
            #     kc = 1 / (tau2 * k * 4 * lam * lam)
            #     tauI = 4 * lam
            #     tauD = 4 * lam
            #     [kP, kI, kD] = [kc, kc / tauI, kc * tauD]

        # max frequency for derivative estimate
        if kD == 0:
            fD = 10             # unused in that case
        else:
            fD = 1/(2*np.pi*tauD) * Ndiff          # "tauD * N" with N > 3

        # update UI
        self.kP.setText(("%6g" %(kP)).strip())
        self.kI.setText(("%6g" %(kI)).strip())
        self.kD.setText(("%6g" %(kD)).strip())
        self.fD.setText(("%6g" %(fD)).strip())
        self.params = [fPid, kP, kI, kD, fD]  # [fpid, kP, kI, kD, fD]

        # go to simulation and plot
        self.plotPID()

    def plotPID(self):
        """
        Assemble closed loop models (either plant + pid and/or model + pid)
        Simulate closed-loop step response and plot
        Launch margin computation
        """
        # retrieve plant, model and PID data
        plotRef = False
        plotFit = False
        data = self.window()
        if data.plantLin.status >= 1:
            plotRef = True
            ref = data.plantLin.OL
        if data.modelFit.status == 1:
            plotFit = True
            fit = data.modelFit.model
        if plotRef == False and plotFit == False:
            self.plot.clear()
            return
        tf = data.options.values["tfinal"]

        # create transfer function of PID
        [fPid, kP, kI, kD, fD] = self.params
        pidN = [kP, kI]
        pidD = [1, 0]
        if kD != 0.:
            tau = 1/(2*np.pi*fD)
            pidN = [kP * tau + kD, kP + kI * tau, kI]
            pidD = [tau, 1, 0]
        pid = signal.lti(pidN, pidD)

        # computation for "plant + pid"
        # Temporary coding while waiting for recent version of numpy signal with ability to combine lti systems simply
        if plotRef:
            # retrieve state space models
            pidss = pid.to_ss()
            [A1, B1, C1, D1] = [pidss.A, pidss.B, pidss.C, pidss.D]
            [A2, B2, C2, D2] = [ref.A, ref.B, ref.C, ref.D]

            A1 = np.matrix(A1)
            B1 = np.matrix(B1)
            C1 = np.matrix(C1)
            D1 = np.matrix(D1)
            A2 = np.matrix(A2)
            B2 = np.matrix(B2)
            C2 = np.matrix(C2)
            D2 = np.matrix(D2)

            # open-loop with controller state space model (e.g. PID + plant) for margin calculation
            a11 = A1
            a12 = np.zeros((A1.shape[0], A2.shape[0]))
            a21 = B2 * C1
            a22 = A2
            b11 = B1
            b21 = B2 * D1
            c11 = D2 * C1
            c12 = C2
            d11 = D2 * D1

            a1_ = np.hstack((a11, a12))
            a2_ = np.hstack((a21, a22))
            aolc = np.vstack((a1_, a2_))

            bolc = np.vstack((b11, b21))
            colc = np.hstack((c11, c12))
            dolc = d11

            olc1 = signal.lti(aolc, bolc, colc, dolc)

            # closed-loop state space model for step response calculation
            one_d = 1. + D2*D1
            A11 = A1 - B1 * D2 * C1 / one_d
            A12 = -B1 * C2 / one_d
            A22 = A2 - B2 * D1 * C2 / one_d
            A21 = B2 * C1 - B2 * D1 * D2 * D1 / one_d
            B11 = B1 - B1 * D2 * D1 / one_d
            B21 = B2 * D1 - B2 * D1 * D2 * D1 / one_d
            C11 = D2 * C1 / one_d
            C12 = C2 / one_d
            D11 = D2 * D1 / one_d

            A1_ = np.hstack((A11, A12))
            A2_ = np.hstack((A21, A22))
            Acl = np.vstack((A1_, A2_))

            Bcl = np.vstack((B11, B21))
            Ccl = np.hstack((C11, C12))
            Dcl = D11

            sys1 = signal.lti(Acl, Bcl, Ccl, Dcl)

            # simulate step response
            t1 = np.linspace(0, tf, 1000)
            [t1, y1] = signal.step(sys1, T=t1)
            y1 = np.real(y1)

        # computation for  "model + pid"
        if plotFit:
            # open-loop with controller state space model (e.g. PID + plant) for margin calculation
            olcNum = np.polymul(pid.num, fit.num)
            olcDen = np.polymul(pid.den, fit.den)
            olc2 = signal.lti(olcNum, olcDen)

            # closed-loop state space model for step response calculation
            clNum = olcNum
            clDen = np.polyadd(olcNum, olcDen)
            sys2 = signal.lti(clNum, clDen)

            # simulate step response
            t2 = np.linspace(0, tf, 1000)
            [t2, y2] = signal.step(sys2, T=t2)
            y2 = np.real(y2)

        # plot
        graph = self.plot.firstGraph()
        graph.clear()
        legPos = amepyplot.GUI.INSIDE_BOTTOM_RIGHT
        displaySP = amepyplot.Display2DLine()
        displaySP.configure(lineColor=QtGui.QColor(120, 135, 145))
        displayRef = amepyplot.Display2DLine()
        displayRef.configure(lineColor=QtGui.QColor(15, 130, 135), lineThickness=2)
        displayFit = amepyplot.Display2DLine()
        displayFit.configure(lineColor=QtGui.QColor(235, 120, 10), lineThickness=1.5, lineStyle=QtCore.Qt.DashLine)

        if plotRef:
            t0 = t1
            u0 = np.copy(t0) * 0. + 1.
        else:
            t0 = t2
            u0 = np.copy(t0) * 0. + 1.
        itemX = amepyplot.Item(t0, title="time", unit="s")
        itemY = amepyplot.Item(u0, title="setpoint", unit="")
        curve = amepyplot.Curve2D(itemX, itemY)
        curve.changeDisplay(displaySP)
        graph.addCurve(curve)
        if plotRef:
            itemX = amepyplot.Item(t1, title="time", unit="s")
            itemY = amepyplot.Item(y1, title="linearized plant + pid", unit="")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayRef)
            graph.addCurve(curve)
        if plotFit:
            itemX = amepyplot.Item(t2, title="time", unit="s")
            itemY = amepyplot.Item(y2, title="plant estimate + pid", unit="")
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayFit)
            graph.addCurve(curve)
        graph.setTitle('Step response')
        graph.configureTitles(showTitle=True, legendPosition=legPos, showLegend=True)

        # save models and go to margin calculation
        if plotRef:
            self.OL = data.plantLin.OL
            self.OLC = olc1
            self.CL = sys1
        else:
            self.OL = data.modelFit.model.to_ss()
            self.OLC = olc2
            self.CL = sys2
        self.OLC = self.OLC.to_ss()
        self.CL = self.CL.to_ss()
        self.calcMargins()

    def calcMargins(self):
        """
        Compute margin. Basic algorithm that works for available models
        Should be replaced by scipy "margin" function in Python 3.x
        Update quality flag
        """

        # retrieve corrected open-loop model (e.g. pid + plant)
        sys = self.OLC

        # compute Bode curve within extended user range (+2/+3 decades on left/right ends)
        # (make sure that we keep same calculation points as in the final margin plot to avoid mistmatch between
        #  calculation and plot caused by resolution)
        data = self.window()
        (fmin, fmax) = (data.options.values["fmin"], data.options.values["fmax"])
        (n1, n2) = (np.log10(fmin), np.log10(fmax))
        npd = 200 / (n2 - n1)                           # actual Bode resolution in points per decade
        dn1 = np.ceil(npd) * 2                          # number of extra points on low end
        dn2 = np.ceil(npd) * 3                          # number of  extra points on high end
        d = (n2 - n1) / (200 - 1)                       # actual step size in [fmin, fmax]
        n1_ = n1 - dn1 * d
        n2_ = n2 + dn2 * d
        N = int(200 + dn1 + dn2)
        (f1, f2) = (10 ** n1_, 10 ** n2_)
        f, mag, phase = ss2bode(sys.A, sys.B, sys.C, sys.D, fmin=f1, fmax=f2, N=N)
        ij1 = np.where(np.isfinite(mag))[0]
        ij2 = np.where(np.isfinite(phase))[0]
        ij = np.intersect1d(ij1, ij2, assume_unique=True)       # all items that are non-inf and non-nan
        f = f[ij]
        mag = mag[ij]
        phase = phase[ij]

        # exit if empty arrays
        if len(mag) == 0:
            self.margins = [np.nan, np.nan, np.nan, np.nan, "?", "?"]
            self.light.setLight(1)
            self.message.setText("Margin computation failed")
            return

        # phase margin
        # look for last frequency crossing down the 0 dB axis
        ii = np.argwhere(mag >= 0.)
        if len(ii) > 0:
            ii = int(ii[-1])
            if ii == len(mag) - 1:
                pm = 180 + phase[-1]
                fpm = f[-1]
                self.phaseMargin.setText("< %.1f" % (pm))
            else:
                # note: need to invert mag array ([::-1]) because np.interp works only with increasing values
                fpm = np.interp(0., mag[ii:ii+2][::-1], np.log10(f[ii:ii+2][::-1]))
                fpm = 10 ** fpm
                ph0dB = np.interp(fpm, f, phase)
                pm = 180 + ph0dB
                self.phaseMargin.setText("%.1f" % (pm))
        elif mag[0] <= 0.:
            fpm = f[0]
            pm = 180 + phase[0]
            self.phaseMargin.setText("> %.1f" % pm)
        else:
            fpm = np.nan
            pm = np.nan
            self.phaseMargin.setText("?")

        # gain margin
        # look for last frequency crossing down the cross-over frequency -180 degree
        ii = np.argwhere(phase >= -180.)
        if len(ii) > 0:
            ii = int(ii[-1])
            if ii == len(mag) - 1:
                fgm = f[-1]
                gm = - mag[-1]
                if gm > 40.:
                    self.gainMargin.setText("Inf" % (gm))
                else:
                    self.gainMargin.setText("> %.1f" % (gm))
            else:
                # note: need to invert mag array ([::-1]) because np.interp works only with increasing values
                fgm = np.interp(-180., phase[ii:ii + 2][::-1], np.log10(f[ii:ii + 2][::-1]))
                fgm = 10 ** fgm
                gm = -np.interp(fgm, f, mag)
                self.gainMargin.setText("%.1f" % (gm))
        else:
            fgm = np.nan
            gm = np.nan
            self.gainMargin.setText("?")

        # confirm stability in case phase margin suggests it's not a minimal phase system
        isStable = not(pm < 0. or gm < 0.)
        if pm > 135:
            try:
                poles = signal.ZerosPolesGain(self.CL).poles
                if any(np.real(poles) > 1.0e-7):
                     isStable = False
            except:
                isStable = False        # capture error when A is not inversible
        pmLeg = self.phaseMargin.text()
        gmLeg = self.gainMargin.text()
        self.margins = [pm, fpm, gm, fgm, pmLeg, gmLeg, isStable]

        # update stability flag
        okStyle = "QLabel {color: green; font: bold}"
        warnStyle = "QLabel {color: orange; font: bold}"
        nokStyle = "QLabel {color: red; font: bold}"

        # update tuning quality flag
        if (pm > 30 and isStable):
            self.phaseMargin.setStyleSheet(okStyle)
        elif pm < 0 or not isStable:
            self.phaseMargin.setStyleSheet(nokStyle)
        else:
            self.phaseMargin.setStyleSheet(warnStyle)
        if gm > 6:
            self.gainMargin.setStyleSheet(okStyle)
        elif gm < 0:
            self.phaseMargin.setStyleSheet(nokStyle)
        else:
            self.gainMargin.setStyleSheet(warnStyle)

        if (pm > 30 and isStable):
            self.light.setLight(2)
            self.message.setText("Tuning ok")
        elif not isStable:
            self.light.setLight(0)
            self.message.setText("Unstable")
        else:
            self.light.setLight(1)
            self.message.setText("Low margin")

    def plotMargin(self):
        data = self.window()
        fmin = data.options.values["fmin"]
        fmax = data.options.values["fmax"]
        if hasattr(self, "plot_margin"):
            self.plot_margin.close()
        self.plot_margin = PlotMargin(self.OLC, fmin, fmax, self.margins)
        self.plot_margin.show()

    def plotBode(self):
        data = self.window()
        fmin = data.options.values["fmin"]
        fmax = data.options.values["fmax"]
        if hasattr(self, "plot_bode"):
            self.plot_bode.close()
        self.plot_bode = PlotBode(self.OL, self.OLC, self.CL, fmin, fmax)
        self.plot_bode.show()

    def runBatch(self):
        """
        Simulate step response for all linearization sets (result set and tlin)
        Show all results in a plot
        Show stability margins in a table
        """
        # start waitbar
        self.waitbar = QtWidgets.QProgressDialog()
        self.waitbar.setWindowTitle("PID tuner")
        self.waitbar.setLabelText("Batch run in progress..")
        self.waitbar.setRange(0, 100)
        self.waitbar.show()
        self.waitbar.setValue(0)
        QtCore.QCoreApplication.processEvents()

        # collect actual settings (for reloading afterwards)
        data = self.window()
        tf = data.options.values["tfinal"]
        i0 = data.plantLin.resList.currentIndex()
        j0 = data.plantLin.tLinList.currentIndex()
        [fPid, kP, kI, kD, fD] = self.params
        pidN = [kP, kI]
        pidD = [1, 0]
        if kD != 0.:
            tau = 1 / (2 * np.pi * fD)
            pidN = [kP * tau + kD, kP + kI * tau, kI]
            pidD = [tau, 1, 0]
        pid = signal.lti(pidN, pidD)
        pidss = pid.to_ss()

        # disconnect plant widget and tuning widget (to avoid useless computations)
        data.plantLin.plotRequest.disconnect(data.tuning.modelUpdate)
        data.modelFit.plotRequest.disconnect(data.tuning.modelUpdate)

        # batch computation of step response
        res = []
        tlin = []
        gm = []
        pm = []
        isStable = []
        (tdata, ydata) = ({}, {})
        k = 0
        kdata = 0
        ktot = data.plantLin.resList.count() * data.plantLin.tLinList.count()
        for i in range(data.plantLin.resList.count()):
            data.plantLin.resList.setCurrentIndex(i)
            for j in range(data.plantLin.tLinList.count()):
                self.waitbar.setValue(int(90 * (k+1) / ktot))
                QtCore.QCoreApplication.processEvents()
                # if QtCore.QCoreApplication.hasPendingEvents():
                #     QtCore.QCoreApplication.processEvents()

                # get plant model for this result / time set
                data.plantLin.tLinList.setCurrentIndex(j)
                try:
                    data.plantLin.calcClosedLoop()         # update plant model
                    ref = data.plantLin.OL
                    calcRun = True
                except:
                    # if .jac doesn't exist (e.g batch results were purged or sketch changed)
                    calcRun = False

                if (data.plantLin.status != 2) or (calcRun == False):
                    k += 1      # if plant is badly conditioned or .jac is not there, skip and move to next
                else:
                    # retrieve state space models
                    [A1, B1, C1, D1] = [pidss.A, pidss.B, pidss.C, pidss.D]
                    [A2, B2, C2, D2] = [ref.A, ref.B, ref.C, ref.D]
                    A1 = np.matrix(A1)
                    B1 = np.matrix(B1)
                    C1 = np.matrix(C1)
                    D1 = np.matrix(D1)
                    A2 = np.matrix(A2)
                    B2 = np.matrix(B2)
                    C2 = np.matrix(C2)
                    D2 = np.matrix(D2)

                    # open-loop with controller state space model (e.g. PID + plant) for margin calculation
                    a11 = A1
                    a12 = np.zeros((A1.shape[0], A2.shape[0]))
                    a21 = B2 * C1
                    a22 = A2
                    b11 = B1
                    b21 = B2 * D1
                    c11 = D2 * C1
                    c12 = C2
                    d11 = D2 * D1

                    a1_ = np.hstack((a11, a12))
                    a2_ = np.hstack((a21, a22))
                    aolc = np.vstack((a1_, a2_))

                    bolc = np.vstack((b11, b21))
                    colc = np.hstack((c11, c12))
                    dolc = d11

                    olc1 = signal.lti(aolc, bolc, colc, dolc)

                    # closed-loop state space model for step response calculation
                    one_d = 1. + D2 * D1
                    A11 = A1 - B1 * D2 * C1 / one_d
                    A12 = -B1 * C2 / one_d
                    A22 = A2 - B2 * D1 * C2 / one_d
                    A21 = B2 * C1 - B2 * D1 * D2 * D1 / one_d
                    B11 = B1 - B1 * D2 * D1 / one_d
                    B21 = B2 * D1 - B2 * D1 * D2 * D1 / one_d
                    C11 = D2 * C1 / one_d
                    C12 = C2 / one_d
                    D11 = D2 * D1 / one_d

                    A1_ = np.hstack((A11, A12))
                    A2_ = np.hstack((A21, A22))
                    Acl = np.vstack((A1_, A2_))

                    Bcl = np.vstack((B11, B21))
                    Ccl = np.hstack((C11, C12))
                    Dcl = D11

                    sys1 = signal.lti(Acl, Bcl, Ccl, Dcl)

                    # simulate step response
                    t1 = np.linspace(0, tf, 1000)
                    [t1, y1] = signal.step(sys1, T=t1)
                    y1 = np.real(y1)

                    # compute stability margins
                    self.OLC = olc1.to_ss()
                    self.CL = sys1.to_ss()
                    self.calcMargins()

                    # save data
                    res.append(data.plantLin.resList.currentText())
                    tlin.append(data.plantLin.tLinList.currentText())
                    pm.append(self.margins[4])
                    gm.append(self.margins[5])
                    tdata[kdata] = t1
                    ydata[kdata] = y1
                    isStable.append(self.margins[6])
                    kdata += 1
                    k += 1

        # restore initial plant selection and PID settings in UI
        self.waitbar.setValue(95)
        data.plantLin.resList.setCurrentIndex(i0)
        data.plantLin.tLinList.setCurrentIndex(j0)
        data.plantLin.calcClosedLoop()
        self.fPid.setText(str(fPid))
        self.kP.setText(str(kP))
        self.kI.setText(str(kI))
        self.kD.setText(str(kD))
        self.fD.setText(str(fD))
        self.editCustom()        # (proceed with self.updateUI() from there)
        data.plantLin.plotRequest.connect(data.tuning.modelUpdate)
        data.modelFit.plotRequest.connect(data.tuning.modelUpdate)
        self.waitbar.close()

        # show batch plot
        if hasattr(self, "plot_batch"):
            self.plot_batch.close()
        self.plot_batch = PlotBatch(res, tlin, pm, gm, tdata, ydata, isStable)
        self.plot_batch.show()

    def applyGains(self):
        [fPid, kP, kI, kD, fD] = self.params
        self.kPuid.setValue(self.kP.text())
        self.kIuid.setValue(self.kI.text())
        self.kDuid.setValue(self.kD.text())
        self.kSuid.setValue(self.kI.text())         # set backtracking gain Ks = Ki in case saturation is used (best
        # setting for unwind)
        tau = 1 / (2 * np.pi * float(self.fD.text()))
        self.tauDuid.setValue(str(tau))
        self.lightInfo.setLight(2)
        self.messageInfo.setText("Parameters applied")

    def addTuningSet(self):
        """ export tuning set (gains, inputs and control) to "pidtuning.data" """
        # /FOR GAIN SCHEDULING
        data = self.window()
        cwd = os.path.dirname(self.filename)

        # get linearization time and batch set
        tlin = data.plantLin.tLinList.currentText()
        tlin = float(tlin[:-2])
        resSet = data.plantLin.resList.currentText()
        if "ref" in resSet:
            resSet = ""

        # get target value
        aliasu = AME.AMEGetVariablesOnPort('#', 2)
        res = AME.AMEGetVariableValues(aliasu[0], resSet)
        res = np.array(res)
        t = res[:, 0]
        y = res[:, 1]
        spo = np.interp(tlin, t, y)

        # get actual value
        aliasu = AME.AMEGetVariablesOnPort('#', 0)
        res = AME.AMEGetVariableValues(aliasu[0], resSet)
        res = np.array(res)
        t = res[:, 0]
        y = res[:, 1]
        yo = np.interp(tlin, t, y)

        # get pid output
        aliasu = AME.AMEGetVariablesOnPort('#', 1)
        res = AME.AMEGetVariableValues(aliasu[0], resSet)
        res = np.array(res)
        t = res[:, 0]
        y = res[:, 1]
        uo = np.interp(tlin, t, y)
        
        # get pid parameters
        [fPid, kP, kI, kD, fD] = self.params

        # export to text file
        # [tlin, setpoint, actual value, pid output, fPid; kP; kI; kD; fD]
        newset = [tlin, spo, yo, uo, fPid, kP, kI, kD, fD]
        out = "\n" + str(newset[0])
        for val in newset[1:]:
            out += "\t" + str(val)
        fileGS = os.path.join(cwd, "GS.data")
        with open(fileGS, "a") as file:
            file.write(out)

        try:
            z = np.loadtxt(fileGS)
            (p, q) = z.shape
            self.SetMessage.setText("set exported to 'GS.data' (%i sets total)" %p)
        except:
            self.SetMessage.setText("set exported to 'GS.data'")        
        # / FOR GAIN SCHEDULING

    def clearTuningSet(self):
        """ reset GS.data file where gain scheduling data is stored """
        # FOR GAIN SCHEDULING
        cwd = os.path.dirname(self.filename)
        fileGS = os.path.join(cwd, "GS.data")
        try:
            os.remove(fileGS)
            self.SetMessage.setText("'GS.data' deleted")
        except:
            self.SetMessage.setText("'GS.data' doesn't exist")

        # /FOR GAIN SCHEDULING


class PlotMargin(QtWidgets.QWidget):
    """
    Open-loop Bode diagram with stability margins
    :param OL: lti object of open-loop model (with or without pid)
    :param fmin: min frequency for plot
    :param fmax: min frequency for plot
    :param margins: [pm, fpm, gm, fgm, pmLeg, gmLeg] phase margin & frequency, gain margin & frequency,
    legends for margins
    """
    def __init__(self, sys, fmin, fmax, margins):
        super(PlotMargin, self).__init__()
        self.setWindowTitle('Stability margins')
        self.resize(600,600)
        layout = QtWidgets.QHBoxLayout()
        self.plot = amepyplot.PlotWidget()
        self.plot.addRow()
        layout.addWidget(self.plot)
        self.setLayout(layout)

        [pm, fpm, gm, fgm, pmLeg, gmLeg, isStable] = margins

        for i in range(0,2):
            graph = self.plot.getGraph(i, 0)
            amepyplot.Graph.clear(graph)

        # Colors
        bodeColor = QtGui.QColor(15, 130, 135)      # for Bode curve
        okColor = QtGui.QColor("green")             # for margin if stable
        warnColor = QtGui.QColor("orange")          # for phase margin if low
        nokColor = QtGui.QColor("red")              # for margin if unstable
        lineColor = QtGui.QColor(60, 70, 75)        # for construction lines that explain margins
        piColor =  QtGui.QColor(65, 170, 200)       # for -180 deg horizontal line

        # configure displays
        displayBode = amepyplot.Display2DLine()
        displayBode.configure(lineColor=bodeColor)
        displayLine = amepyplot.Display2DLine()
        displayLine.configure(lineColor=lineColor, lineStyle=QtCore.Qt.DotLine)

        if (fgm <= fmin) or (fgm >= fmax):
            gm_linestyle = QtCore.Qt.DashDotLine
            gm_fill = amepyplot.NoFill
        else:
            gm_linestyle = QtCore.Qt.SolidLine
            gm_fill = amepyplot.RadialFill
        if gm > 6:
            gm_color = okColor
        elif gm < 0:
            gm_color = nokColor
        else:
            gm_color = warnColor

        if (fpm <= fmin) or (fpm >= fmax):
            pm_linestyle = QtCore.Qt.DashDotLine
            pm_fill = amepyplot.NoFill
        else:
            pm_linestyle = QtCore.Qt.SolidLine
            pm_fill = amepyplot.RadialFill
        if pm > 30 and isStable:
            pm_color = okColor
        elif pm < 0 or not isStable:
            pm_color = nokColor
        else:
            pm_color = warnColor


        legPos = amepyplot.GUI.INSIDE_BOTTOM_LEFT

        displayGrey = amepyplot.Display2DLine()
        displayGrey.configure(lineColor=QtGui.QColor(60, 70, 75), lineStyle=QtCore.Qt.DotLine)
        displayOrange = amepyplot.Display2DLine()
        displayOrange.configure(lineColor=QtGui.QColor(235, 120, 10), lineStyle=QtCore.Qt.DotLine)
        displayMargin = amepyplot.Display2DLine()
        title = "pid + plant (open-loop)"



        # compute bode curve
        f, mag, phase = ss2bode(sys.A, sys.B, sys.C, sys.D, fmin=fmin, fmax=fmax, N = 200)
        graph = self.plot.getGraph(0, 0)

        # gain plot
        itemX = amepyplot.Item(f, title="frequency", unit="Hz")
        itemY = amepyplot.Item(mag, title=title, unit="")
        curve = amepyplot.Curve2D(itemX, itemY)
        curve.changeDisplay(displayBode)
        graph.addCurve(curve)
        if not np.isnan(gm):
            # if fgm is out of plot limits
            if fgm < fmin:
                fgm = fmin
                gm = -np.interp(fmin, f, mag)
            elif fgm > fmax:
                fgm = fmax
                gm = -np.interp(fmax, f, mag)

            # gain margin line
            itemX = amepyplot.Item([fgm, fgm])
            itemY = amepyplot.Item([0, -gm])
            curve = amepyplot.Curve2D(itemX, itemY)
            display = amepyplot.Display2DLine()
            display.configure(lineColor=gm_color, lineStyle=gm_linestyle, lineThickness=3)
            curve.changeDisplay(display)
            graph.addCurve(curve)

            # gain margin end mark (if in range)
            if (fgm > fmin) and (fgm < fmax):
                point = amepyplot.GraphPoint(graph)
                point.avoidManipulation()
                point.setModelPosition(fgm, -gm)
                point.setSizeFactor(0.5)
                point.configureSymbol(style=amepyplot.Circle, size=1, color=gm_color,
                                      fill=gm_fill)

            # vertical dotted line for gain margin (continuation of gain margin)
            ylim = graph.yAxis().range()
            itemX = amepyplot.Item([fgm, fgm])
            itemY = amepyplot.Item([ylim[0], -gm])
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayLine)
            graph.addCurve(curve)

        ylim = graph.yAxis().range()
        if not np.isnan(pm):
            # vertical dotted line and 0 dB for phase margin (if in range only)
            if (fpm > fmin) and (fpm < fmax):
                itemX = amepyplot.Item([fpm, fpm])
                itemY = amepyplot.Item([0, ylim[0]])
                curve = amepyplot.Curve2D(itemX, itemY)
                curve.changeDisplay(displayLine)
                graph.addCurve(curve)
                point = amepyplot.GraphPoint(graph)
                point.avoidManipulation()
                point.setModelPosition(fpm, 0)
                point.setSizeFactor(0.5)
                point.configureSymbol(style=amepyplot.Square, size=0.5, color=lineColor,
                                      fill=amepyplot.NoFill)

        graph.configureTitles(showTitle=True, showLegend=False)
        graph.xAxis().setLogScale(1)
        graph.setTitle('Gain [dB]')
        graph.yAxis().setRange(ylim[0], ylim[1])

        # legends for gain plot
        xlim = graph.xAxis().range()
        xt = np.interp(0.02, [0, 1], np.log10([xlim[0], xlim[1]]))
        xt = 10 ** xt
        dylim = ylim[1] - ylim[0]
        gainLeg = amepyplot.GraphText(graph)
        gainLeg.setText("gain of " + title)
        font = gainLeg.textFont()
        font.setBold(True)
        gainLeg.setTextFont(font)
        gainLeg.setTextColor(bodeColor)
        gainLeg.setTranslucentBackground(False)
        gainLeg.setModelPosition(xt, ylim[0] + dylim * 0.3)

        gMargLeg = amepyplot.GraphText(graph)
        gMargLeg.setText("gain margin (" + gmLeg + " dB)")
        font = gMargLeg.textFont()
        font.setBold(True)
        gMargLeg.setTextFont(font)
        gMargLeg.setTextColor(gm_color)
        gMargLeg.setTranslucentBackground(False)
        gMargLeg.setModelPosition(xt, ylim[0] + dylim * 0.2)


        # Phase plot
        graph = self.plot.getGraph(1, 0)
        itemX = amepyplot.Item(f, title="frequency", unit="Hz")
        itemY = amepyplot.Item(phase, title=title, unit="deg")
        curve = amepyplot.Curve2D(itemX, itemY)
        curve.changeDisplay(displayBode)
        graph.addCurve(curve)
        if not np.isnan(pm):
            # if fpm is out of plot limits
            if fpm < fmin:
                fpm = fmin
                pm = 180 + np.interp(fmin, f, phase)
            elif fgm > fmax:
                fpm = fmax
                pm = 180 + np.interp(fmax, f, phase)

            # horizontal line at -180 deg (phase crossover)
            itemX = amepyplot.Item([fmin, fmax])
            itemY = amepyplot.Item([-180, -180])
            curve = amepyplot.Curve2D(itemX, itemY)
            display = amepyplot.Display2DLine()
            display.configure(lineColor=piColor, lineStyle=QtCore.Qt.DotLine)
            curve.changeDisplay(display)
            graph.addCurve(curve)

            # phase margin line
            itemX = amepyplot.Item([fpm, fpm])
            itemY = amepyplot.Item([-180, -180 + pm])
            curve = amepyplot.Curve2D(itemX, itemY)
            display = amepyplot.Display2DLine()
            display.configure(lineColor=pm_color, lineStyle=pm_linestyle, lineThickness=3)
            curve.changeDisplay(display)
            graph.addCurve(curve)

            # phase margin end mark (if in range)
            if (fpm > fmin) and (fpm < fmax):
                point = amepyplot.GraphPoint(graph)
                point.avoidManipulation()
                point.setModelPosition(fpm, -180 + pm)
                point.setSizeFactor(0.5)
                point.configureSymbol(style=amepyplot.Circle, size=1, color=pm_color,
                                      fill=pm_fill)

            # vertical dotted line at 0 dB crossover (continuating phase margin line)
            ylim = graph.yAxis().range()
            itemX = amepyplot.Item([fpm, fpm])
            itemY = amepyplot.Item([-180 + pm, ylim[1]])
            curve = amepyplot.Curve2D(itemX, itemY)
            curve.changeDisplay(displayLine)
            graph.addCurve(curve)

        if not np.isnan(gm):
            # vertical dotted line and mark at phase crossover for gain margin (if in range only)
            if (fgm > fmin) and (fgm < fmax):
                pgm = np.interp(fgm, f, phase)
                itemX = amepyplot.Item([fgm, fgm])
                itemY = amepyplot.Item([pgm, ylim[1]])
                curve = amepyplot.Curve2D(itemX, itemY)
                curve.changeDisplay(displayLine)
                graph.addCurve(curve)
                point = amepyplot.GraphPoint(graph)
                point.avoidManipulation()
                point.setModelPosition(fgm, pgm)
                point.setSizeFactor(0.5)
                point.configureSymbol(style=amepyplot.Square, size=0.5, color=lineColor,
                                      fill=amepyplot.NoFill)

        graph.xAxis().setLogScale(1)
        graph.setTitle('Phase [degree]')
        graph.configureTitles(showTitle=True, showLegend=False)
        graph.yAxis().setRange(ylim[0], ylim[1])

        # legends for phase plot
        dylim = ylim[1] - ylim[0]
        PhaseLeg = amepyplot.GraphText(graph)
        PhaseLeg.setText("phase of " + title)
        font = PhaseLeg.textFont()
        font.setBold(True)
        PhaseLeg.setTextFont(font)
        PhaseLeg.setTextColor(bodeColor)
        PhaseLeg.setTranslucentBackground(False)
        PhaseLeg.setModelPosition(xt, ylim[0] + dylim * 0.3)

        phMargLeg = amepyplot.GraphText(graph)
        phMargLeg.setText("phase margin (" + pmLeg + " deg)")
        font = phMargLeg.textFont()
        font.setBold(True)
        phMargLeg.setTextFont(font)
        phMargLeg.setTextColor(pm_color)
        phMargLeg.setTranslucentBackground(False)
        phMargLeg.setModelPosition(xt, ylim[0] + dylim * 0.2)

class PlotBode(QtWidgets.QWidget):
    """
    Bode diagram of plant, pid+plant and closed-loop systems

    :param OL: lti object of open-loop model
    :param OLC: lti object of open-loop model + pid
    :param CL: lti object of closed-loop model
    :param fmin: min frequency for plot
    :param fmax: min frequency for plot
    """

    def __init__(self, OL, OLC, CL, fmin, fmax):
        super(PlotBode, self).__init__()
        self.setWindowTitle('Bode plots')
        self.resize(600, 600)
        layout = QtWidgets.QHBoxLayout()
        self.plot = amepyplot.PlotWidget()
        self.plot.addRow()
        layout.addWidget(self.plot)
        self.setLayout(layout)

        for i in range(0, 2):
            graph = self.plot.getGraph(i, 0)
            amepyplot.Graph.clear(graph)

        legPos = amepyplot.GUI.INSIDE_BOTTOM_LEFT
        displayOL = amepyplot.Display2DLine()
        displayOL.configure(lineColor=QtGui.QColor(80, 90, 100), lineThickness=1.5, lineStyle=QtCore.Qt.DashLine)
        displayOLC = amepyplot.Display2DLine()
        # displayOLC.configure(lineColor=QtGui.QColor(80, 90, 100), lineThickness=1.5)
        displayOLC.configure(lineColor=QtGui.QColor(80, 90, 100), lineThickness=1.5)
        displayCL = amepyplot.Display2DLine()
        displayCL.configure(lineColor=QtGui.QColor(0, 153, 153), lineThickness=2.5)
        displayGrey = amepyplot.Display2DLine()
        displayGrey.configure(lineColor=QtGui.QColor(60, 70, 75), lineStyle=QtCore.Qt.DotLine)
        title = ["plant (open-loop)", "pid + plant (open-loop)", "pid + plant (closed-loop)"]


        i = 0
        for sys in (OL, OLC, CL):
            f, mag, phase = ss2bode(sys.A, sys.B, sys.C, sys.D, fmin=fmin, fmax=fmax, N = 200)
            graph = self.plot.getGraph(0, 0)

            itemX = amepyplot.Item(f, title="frequency", unit="Hz")
            itemY = amepyplot.Item(mag, title=title[i], unit="")
            curve = amepyplot.Curve2D(itemX, itemY)
            if i == 0:
                curve.changeDisplay(displayOL)
            elif i == 1:
                curve.changeDisplay(displayOLC)
            elif i == 2:
                curve.changeDisplay(displayCL)
            graph.addCurve(curve)
            graph.configureTitles(showTitle=True, legendPosition=legPos)

            graph.xAxis().setLogScale(1)
            graph.setTitle('Gain [dB]')

            graph = self.plot.getGraph(1, 0)
            itemX = amepyplot.Item(f, title="frequency", unit="Hz")
            itemY = amepyplot.Item(phase, title=title[i], unit="deg")
            curve = amepyplot.Curve2D(itemX, itemY)
            if i == 0:
                curve.changeDisplay(displayOL)
            elif i == 1:
                curve.changeDisplay(displayOLC)
            elif i == 2:
                curve.changeDisplay(displayCL)
            graph.addCurve(curve)
            graph.xAxis().setLogScale(1)
            graph.setTitle('Phase [degree]')
            graph.configureTitles(showTitle=True, legendPosition=legPos, showLegend=False)
            i += 1

class PlotBatch(QtWidgets.QWidget):
    """
    Plot widget for batch run (step response + margins)
    """

    def __init__(self, res, tlin, pm, gm, tdata, ydata, isStable):
        super(PlotBatch, self).__init__()
        self.setWindowTitle('Batch results - Closed-loop step response')
        self.resize(700, 350)
        layout = QtWidgets.QGridLayout()
        self.plot = amepyplot.PlotWidget()

        nItems = len(res)
        self.table = QtWidgets.QTableWidget(4, nItems)
        headers = ["result set", "linearization time", "phase margin [deg]", "gain margin [dB]"]
        hstyle = 'QHeaderView::section{background-color: lightGray}'
        self.table.horizontalHeader().setStyleSheet(hstyle)
        k = 0
        for h in headers:
            item = QtWidgets.QTableWidgetItem('%s' % (h))
            self.table.setVerticalHeaderItem(k, item)
            k += 1
        self.table.horizontalHeader().hide()  # hide vertical axis
        self.table.resizeRowsToContents()

        layout.addWidget(self.plot, 0, 0)
        layout.addWidget(self.table, 1, 0)
        layout.setRowStretch(0,1)
        layout.setRowMinimumHeight(0, 300)
        self.setLayout(layout)

        resSet = list(set(res))               # list of unique result sets
        nPlot = len(resSet)
        legPos = amepyplot.GUI.INSIDE_BOTTOM_RIGHT

        # plot run sets in individual plots
        for i in range(0, nPlot):
            if i>0:
                self.plot.addColumn()
            graph = self.plot.getGraph(0, i)
            amepyplot.Graph.clear(graph)

            for j in range(0, len(tlin)):
                if res[j] == resSet[i]:
                    itemX = amepyplot.Item(tdata[j], title="time", unit="s")
                    itemY = amepyplot.Item(ydata[j], title=tlin[j], unit="")
                    curve = amepyplot.Curve2D(itemX, itemY)
                    graph.addCurve(curve)
            graph.setTitle("result set: " + resSet[i])
            graph.configureTitles(showTitle=True, legendPosition=legPos, showLegend=True)

        # stability margins table
        table = self.table
        for i in range(0, len(tlin)):
            for j in range(0, 4):
                if j == 0:
                    tmp = str(res[i])
                elif j == 1:
                    tmp = str(tlin[i])
                elif j == 2:
                    tmp = str(pm[i])
                elif j == 3:
                    tmp = str(gm[i])
                item = QtWidgets.QTableWidgetItem()
                item.setData(QtCore.Qt.EditRole, ('%s' % (tmp)))
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                if j == 2:
                    val = float(pm[i])
                    if val > 30 and isStable[i]:
                        item.setBackground(QtGui.QColor("green"))
                        item.setForeground(QtGui.QColor("white"))
                    elif val < 0 or not isStable[i]:
                        item.setBackground(QtGui.QColor("red"))
                        item.setForeground(QtGui.QColor("white"))
                    else:
                        item.setBackground(QtGui.QColor("orange"))

                elif j == 3:
                    val = float(gm[i])
                    if val > 6:
                        item.setBackground(QtGui.QColor("green"))
                        item.setForeground(QtGui.QColor("white"))
                    elif val < 0:
                        item.setBackground(QtGui.QColor("red"))
                        item.setForeground(QtGui.QColor("white"))
                    else:
                        item.setBackground(QtGui.QColor("orange"))
                table.setItem(j, i, item)

        table.resizeColumnsToContents()

















