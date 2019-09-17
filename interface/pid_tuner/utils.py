#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DESCRIPTION: Option widget, Utility functions

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
from amesim import *
import numpy as np
from scipy import signal
from scipy.linalg import hessenberg, solve
import glob, os, time, cPickle, sys
from PySide2.QtCore import Qt, Signal, QTimer, QRect, QSize
from PySide2.QtGui import QColor, QPen, QPainterPath, QBrush, QPainter, QFontMetrics



class TrafficLight(QtWidgets.QLabel):
    """
    Traffic light widget (none/red/yellow/green for values <0, 0, 1, 2)
    """

    def __init__(self, state=0):
        super(TrafficLight, self).__init__()
        self.setLight(state)
        self.state = state

    def setLight(self, state):
        if state == 2:
            self.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/images/light_green_pix16.png"))
            self.state = state
        elif state == 1:
            self.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/images/light_yellow_pix16.png"))
            self.state = state
        elif state == 0:
            self.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/images/light_red_pix16.png"))
            self.state = state
        else:
            self.clear()
            self.state = -1
        self.setScaledContents(0)
        self.setAlignment(QtCore.Qt.AlignLeft)

class AppOptions(QtWidgets.QDialog):
    """
    Options widget
    """
    def __init__(self):
        super(AppOptions, self).__init__()
        self.setWindowTitle('PID tuner options')

        # Instantiations and layout
        mainLayout = QtWidgets.QVBoxLayout()

        # Linear analysis group
        group = QtWidgets.QGroupBox('Linear analysis')
        layout = QtWidgets.QGridLayout()
        attributes = ["fmin", "fmax", "tfinal"]
        labels = ["min frequency [Hz]", "max frequency [Hz]", "final time for step response [s]"]
        i = 0
        for lab, attr in zip(labels, attributes):
            widget = QtWidgets.QLineEdit("")
            widget.setAlignment(QtCore.Qt.AlignRight)
            setattr(self, attr, widget)
            layout.addWidget(QtWidgets.QLabel(lab), i, 0)
            layout.addWidget(widget, i, 1)
            i += 1
        layout.setColumnMinimumWidth(0, 160)
        group.setLayout(layout)
        mainLayout.addWidget(group)

        # Plant estimate group
        group = QtWidgets.QGroupBox('Plant estimate')
        layout = QtWidgets.QGridLayout()
        attributes = ["maxIter", "tolx", "fitTarget"]
        labels = ["max number of iterations", "termination tolerance", "fitting target"]
        clist = ["step response", "gain curve [dB]", "mixed"]
        i = 0
        for lab, attr in zip(labels, attributes):
            if i< 2:
                widget = QtWidgets.QLineEdit("")
                widget.setAlignment(QtCore.Qt.AlignRight)
            else:
                widget = QtWidgets.QComboBox()
                widget.addItems(clist)
            setattr(self, attr, widget)
            layout.addWidget(QtWidgets.QLabel(lab), i, 0)
            layout.addWidget(widget, i, 1)
            i += 1
        layout.setColumnMinimumWidth(0, 160)
        group.setLayout(layout)
        mainLayout.addWidget(group)

        # PID tuning group
        group = QtWidgets.QGroupBox("PID tuning")
        layout = QtWidgets.QGridLayout()
        lab = QtWidgets.QLabel('cutoff factor for d/dt')
        lab.setToolTip(u"= N such as\n\n"
                               u" d          s\n"
                               u"--- = ------------\n"
                               u" dt    1+\u03C4d/N.s\nwith \u03C4d = Kd / Kp")
        self.Ndiff = QtWidgets.QLineEdit("")
        self.Ndiff.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(lab, 0, 0)
        layout.addWidget(self.Ndiff, 0, 1)

        # tuning objective disabled (force to standard IMC, S-IMC option kept for future)
        self.tuningMethod = QtWidgets.QComboBox()
        clist = ["tracking", "rejection"]
        self.tuningMethod.addItems(clist)
        self.tuningLab = QtWidgets.QLabel("tuning objective")
        self.tuningLab.setToolTip("tracking: faster tracking response, slower disturbance rejection\n"
                                   "rejection: slower tracking response, faster disturbance rejection")
        layout.addWidget(self.tuningLab, 1, 0)
        layout.addWidget(self.tuningMethod, 1, 1)
        layout.setColumnMinimumWidth(0, 160)
        group.setLayout(layout)
        mainLayout.addWidget(group)
        mainLayout.addStretch(1)

        # message and button
        msgstyle = "QLabel {color: darkGrey}"
        self.message = QtWidgets.QLabel("")
        self.message.setStyleSheet(msgstyle)
        self.doneButton = QtWidgets.QPushButton('Done')
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.message)
        layout.addStretch(1)
        layout.addWidget(self.doneButton)
        mainLayout.addLayout(layout)
        self.setLayout(mainLayout)

        # Slots
        self.fmin.editingFinished.connect(self.checkInputs)
        self.fmax.editingFinished.connect(self.checkInputs)
        self.tfinal.editingFinished.connect(self.checkInputs)
        self.maxIter.editingFinished.connect(self.checkInputs)
        self.tolx.editingFinished.connect(self.checkInputs)
        self.Ndiff.editingFinished.connect(self.checkInputs)
        self.doneButton.clicked.connect(self.exit)

        # Expression evaluator
        self.evaluator = apps.kernel.Evaluator()

        # Initialize output dictionary
        self.status = 1
        self.values = {"fmin": "", "fmax": "", "tfinal": "", "maxIter": "", "tolx": "",
                       "fitTarget": "", "Ndiff": "", "tuningMethod": ""}

    def initUI(self, data):
        """ load last saved set, set up with default otherwise """
        try:
            # load last saved set if any
            s = data.appObject.loadAttribute("optionsSettings")
            settings = cPickle.loads(str(s))
            self.fmin.setText(str(settings["fmin"]))
            self.fmax.setText(str(settings["fmax"]))
            self.tfinal.setText(str(settings["tfinal"]))
            self.maxIter.setText(str(settings["maxIter"]))
            self.tolx.setText(str(settings["tolx"]))
            i = int(str(settings["fitTarget"]))
            self.fitTarget.setCurrentIndex(i)
            self.Ndiff.setText(str(settings["Ndiff"]))
            i = int(str(settings["tuningMethod"]))
            self.tuningMethod.setCurrentIndex(i)
        except:
            # set default values
            self.fmin.setText("0.01")
            self.fmax.setText("1000")
            self.tfinal.setText("1.0")
            self.maxIter.setText("1000")
            self.tolx.setText("1.0e-4")
            self.fitTarget.setCurrentIndex(2)
            self.Ndiff.setText("1000")
            self.tuningMethod.setCurrentIndex(0)

        # disable tuning target option (kept for future)
        self.tuningMethod.setCurrentIndex(0)        # force to IMC method
        self.tuningMethod.setEnabled(False)
        self.tuningMethod.setVisible(False)
        self.tuningLab.setVisible(False)

        # update output dictionary
        self.convert2dic()
        self.evaluator.setExternalContext(data.appObject.circuitNameId())

    def convert2dic(self):
        """ Convert string inputs into a dictionary """
        # convert into dictionary
        tmp = {}
        labels = ["fmin", "fmax", "tfinal", "maxIter", "tolx", "Ndiff"]
        for lab in labels:
            widget = getattr(self, lab)
            tmp[lab] = float(widget.text())
        tmp["fitTarget"] = self.fitTarget.currentIndex()
        tmp["tuningMethod"] = self.tuningMethod.currentIndex()
        self.values = tmp

    def checkInputs(self):
        """ Check inputs before accepting """
        okStyle = "QLineEdit {color: black}"
        errStyle = "QLineEdit {color: red}"
        self.status = 1
        self.message.setText("")

        self.fmin.setStyleSheet(okStyle)
        val = self.evaluator.getExpressionValue(self.fmin.text())
        err = self.evaluator.hasError()
        if (err == False) and (val > 1.0e-12) and (val < 1.0e9):
            self.fmin.setText(str(val))
        else:
            self.fmin.setStyleSheet(errStyle)
            self.status = 0
            self.message.setText("fmin should be >0")
            return

        fmin = val
        self.fmax.setStyleSheet(okStyle)
        val = self.evaluator.getExpressionValue(self.fmax.text())
        err = self.evaluator.hasError()
        if (err == False) and (val < 1.0e12):
            if (val < fmin * 100):
                val = fmin * 100
                self.message.setText("fmax should be >100*fmin")
            self.fmax.setText(str(val))
        else:
            self.fmax.setStyleSheet(errStyle)
            self.status = 0
            self.message.setText("fmax should be >100*fmin")
            return

        self.tfinal.setStyleSheet(okStyle)
        val = self.evaluator.getExpressionValue(self.tfinal.text())
        err = self.evaluator.hasError()
        if (err == False) and (val > 1.0e-9) and (val < 1.0e6):
            self.tfinal.setText(str(val))
        else:
            self.tfinal.setStyleSheet(errStyle)
            self.status = 0
            self.message.setText("tfinal be >0")
            return

        self.maxIter.setStyleSheet(okStyle)
        val = self.evaluator.getExpressionValue(self.maxIter.text())
        err = self.evaluator.hasError()
        if (err == False) and (val >= 10) and (val < 1.0e6):
            self.maxIter.setText(str(val))
        else:
            self.maxIter.setStyleSheet(errStyle)
            self.status = 0
            self.message.setText("max iter. should be >10")
            return

        self.tolx.setStyleSheet(okStyle)
        val = self.evaluator.getExpressionValue(self.tolx.text())
        err = self.evaluator.hasError()
        if (err == False) and (val > 1.0e-12) and (val <= 1.0):
            self.tolx.setText(str(val))
        else:
            self.tolx.setStyleSheet(errStyle)
            self.status = 0
            self.message.setText("tolx. should be in ]0..1]")
            return

        self.Ndiff.setStyleSheet(okStyle)
        val = self.evaluator.getExpressionValue(self.Ndiff.text())
        err = self.evaluator.hasError()
        if (err == False) and (val >= 1.0) and (val < 1.0e6):
            self.Ndiff.setText(str(val))
        else:
            self.Ndiff.setStyleSheet(errStyle)
            self.status = 0
            self.message.setText("Ndiff should be >1")
            return

        # update output dictionary
        self.convert2dic()

    def exit(self):
        # close if all checks are ok
        self.checkInputs()
        if self.status == 1:
            self.accept()
        else:
            return

class WorkflowViewerLight(QtWidgets.QWidget):
    """ Simplified version of WorkflowViewer from toolbox_ice with:
            - Look & feel from Study Manager"""
    clicked = QtCore.Signal(object)

    def __init__(self, names):
        QtWidgets.QWidget.__init__(self)

        self.__names = names

        self.__availables = [False] * len(names)

        self.__selected = None
        self.__from_selected = None
        self.__item_width = 1
        self.__item_height = 1

        self.__arrow_size = 10
        self.__arrow_space = 5

        # self.__color_selected = QColor(85, 160, 185)
        self.__color_selected = QColor(0, 100, 135)
        # self.__color_unselected = QColor(170, 170, 170)
        self.__color_unselected = QColor(220, 220, 220)
        self.__color_notavailable = QColor(200, 200, 200)
        self.__textColor_selected = QColor(255, 255, 255)       # added
        self.__textColor_unselected = QColor(0, 0, 0)           # added

        self.__pen_text = QPen()
        self.__pen_text.setColor(QColor(255, 255, 255))

        # added to have same as Study Manager
        self.__pen_line = QPen()
        self.__pen_line.setColor(QColor(192, 192, 192))

        self.__font = self.font()
        self.__font.setBold(True)               # added
        # self.__font.setPointSize(10)          # removed to keep same font size as in the UI

        self.setMinimumHeight(1)
        self.repaint()

        self.__timer = QTimer()
        self.__timer.setInterval(10)
        self.__timer.setSingleShot(False)
        self.__timer.timeout.connect(self.__updateAnim)

        self.__mode = 'stop'  # 'left' 'right'
        self.__pos = 0

    ### Selected ###
    def getSelected(self):
        return self.__selected

    def setSelected(self, selected, anim=False):
        # change default anim status to False
        if selected is None:
            pass
        elif selected < 0:
            selected = 0
        elif selected >= len(self.__names):
            selected = len(self.__names) - 1

        if self.__from_selected is None:
            self.__from_selected = selected

        if self.__mode == 'stop':
            self.__pos = self.__from_selected * self.__item_width

        self.__selected = selected

        if not anim:
            self.__from_selected = self.__selected

        if self.__from_selected < selected:
            self.__mode = 'right'
        elif self.__from_selected > selected:
            self.__mode = 'left'
        else:
            self.__mode = 'stop'

        self.__timer.start()
        self.repaint()

    ### Availables ###
    def getAvailables(self):
        return list(self.__availables)

    def setAvailables(self, availables):
        """ availables = [x, x, x, ...] with x = 0/1 for each step, e.g list size is number
        of steps """
        self.__availables = list(availables)
        self.repaint()

    def setAvailable(self, num, available):
        self.__availables[num] = available
        self.repaint()

    ### Paint ###
    def getItemHeight(self):
        return self.__item_height

    def __paintStart(self, painter, color):
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(self.__item_width - self.__arrow_size / 2.0 - self.__arrow_space / 2.0, 0)
        path.lineTo(self.__item_width + self.__arrow_size / 2.0 - self.__arrow_space / 2.0, self.__item_height / 2.0)
        path.lineTo(self.__item_width - self.__arrow_size / 2.0 - self.__arrow_space / 2.0, self.__item_height)
        path.lineTo(0, self.__item_height)
        path.lineTo(0, 0)
        painter.fillPath(path, QBrush(color))
        painter.strokePath(path, self.__pen_line)

    def __paintMiddle(self, painter, start, color):
        path = QPainterPath()
        path.moveTo(start - self.__arrow_size / 2.0 + self.__arrow_space / 2.0, 0)
        path.lineTo(start + self.__item_width - self.__arrow_size / 2.0 - self.__arrow_space / 2.0, 0)
        path.lineTo(start + self.__item_width + self.__arrow_size / 2.0 - self.__arrow_space / 2.0,
                    self.__item_height / 2.0)
        path.lineTo(start + self.__item_width - self.__arrow_size / 2.0 - self.__arrow_space / 2.0, self.__item_height)
        path.lineTo(start - self.__arrow_size / 2.0 + self.__arrow_space / 2.0, self.__item_height)
        path.lineTo(start + self.__arrow_size / 2.0 + self.__arrow_space / 2.0, self.__item_height / 2.0)
        path.lineTo(start - self.__arrow_size / 2.0 + self.__arrow_space / 2.0, 0)
        painter.fillPath(path, QBrush(color))
        painter.strokePath(path, self.__pen_line)

    def __paintStop(self, painter, start, color):
        path = QPainterPath()
        path.moveTo(start - self.__arrow_size / 2.0 + self.__arrow_space / 2.0, 0)
        path.lineTo(start + self.__item_width, 0)
        path.lineTo(start + self.__item_width, self.__item_height)
        path.lineTo(start - self.__arrow_size / 2.0 + self.__arrow_space / 2.0, self.__item_height)
        path.lineTo(start + self.__arrow_size / 2.0 + self.__arrow_space / 2.0, self.__item_height / 2.0)
        path.lineTo(start - self.__arrow_size / 2.0 + self.__arrow_space / 2.0, 0)
        painter.fillPath(path, QBrush(color))
        painter.strokePath(path, self.__pen_line)

    def __paintOnlyOne(self, painter, color):
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(self.__item_width, 0)
        path.lineTo(self.__item_width, self.__item_height)
        path.lineTo(0, self.__item_height)
        path.lineTo(0, 0)
        painter.fillPath(path, QBrush(color))
        painter.strokePath(path, self.__pen_line)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setFont(self.__font)
        painter.setPen(self.__pen_line)
        metrics = QFontMetrics(self.__font)
        # text_height = metrics.height()
        text_width = max(metrics.size(Qt.TextExpandTabs, name).width() for name in self.__names) * 1.2
        self.__item_width = self.width() / float(len(self.__names))
        # self.__item_height = 2.5 * text_height
        self.__item_height = self.frameGeometry().height()      # modified to auto-fit height from layout

        for i, name in enumerate(self.__names):
            if self.__availables[i]:
                color = self.__color_unselected
            else:
                color = self.__color_notavailable
            if i == 0:
                if len(self.__names) == 1:
                    self.__paintOnlyOne(painter, color)
                else:
                    self.__paintStart(painter, color)
            elif i == len(self.__names) - 1:
                self.__paintStop(painter, self.__item_width * i, color)
            else:
                self.__paintMiddle(painter, self.__item_width * i, color)

        if self.__selected is not None:
            if self.__mode == 'stop':
                pos_x = self.__selected * self.__item_width
                if self.__selected == 0:
                    if len(self.__names) == 1:
                        self.__paintOnlyOne(painter, self.__color_selected)
                    else:
                        self.__paintStart(painter, self.__color_selected)
                elif self.__selected == len(self.__names) - 1:
                    self.__paintStop(painter, self.__item_width * self.__selected, self.__color_selected)
                else:
                    self.__paintMiddle(painter, self.__item_width * self.__selected, self.__color_selected)
            else:
                self.__paintMiddle(painter, self.__pos, self.__color_selected)

        painter.setPen(self.__pen_text)
        for i, name in enumerate(self.__names):
            if i == self.__selected:
                painter.setPen(self.__textColor_selected)
            else:
                painter.setPen(self.__textColor_unselected)
            painter.drawText(QRect(self.__item_width * i, 0, self.__item_width, self.__item_height), Qt.AlignCenter,
                             name)
        painter.end()

        self.setMinimumHeight(self.__item_height)
        self.setMinimumWidth(text_width * len(self.__names))
        # self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)

    ### GUI action ###
    def mousePressEvent(self, event):
        for i, name in enumerate(self.__names):
            if i * self.__item_width <= event.x() <= (i + 1) * self.__item_width:
                self.clicked.emit(i)
                break

    ### Animation ###
    def __updateAnim(self):
        # not used, removed from original
        pass

class ErrorDlg(QtWidgets.QDialog):
    """
    Error Dialog widget used by plantLin when failing to load .jac files
    """
    def __init__(self, errCode, info=""):
        super(ErrorDlg, self).__init__()
        self.setWindowTitle("PID tuner")

        self.okButton = QtWidgets.QPushButton("OK")

        # default values
        ico = QtGui.QPixmap(os.path.dirname(__file__) + "/images/warning_pix24_bw.png")
        text = "??"
        pic = []

        # icon and picture selection = f(error code)
        if errCode == 4:
            # error while importing and external .jac file
            text = 'Fail importing "%s"\n\n' \
                   'This app supports only .jac file with:\n\n' \
                   ' - only one control\n' \
                   ' - only one observer\n' \
                   ' - no implicit state' %(info)
        elif errCode == 10:
            # running under Linux
            text = "The PID tuner is not compatible with Linux."

        # format text and icon
        labmsg = QtWidgets.QLabel(text)
        labmsg.setAlignment(QtCore.Qt.AlignLeft)
        labico = QtWidgets.QLabel()
        labico.setPixmap(ico)
        labpic = QtWidgets.QLabel()
        if pic != []:
            labpic.setPixmap(pic)
            labpic.setAlignment(QtCore.Qt.AlignCenter)

        # layout
        mainLayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QGridLayout()
        layout.addWidget(labico, 0, 0)
        layout.addWidget(labmsg, 0, 1)
        layout.addWidget(QtWidgets.QLabel(), 1, 0, 1, 2)
        if pic != []:
            layout.addWidget(labpic, 2, 0, 1, 2)
        layout.setColumnStretch(1, 1)
        mainLayout.addLayout(layout)
        layout = QtWidgets.QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.okButton)
        mainLayout.addLayout(layout)
        self.setLayout(mainLayout)

        self.okButton.clicked.connect(self.close)
        QtCore.QCoreApplication.processEvents()

    def close(self):
        self.accept()


def ameloadjNoprint(dir, file):
    """execute ameloadj with printout redirected to debug.log file"""

    __stdout__ = sys.stdout             # ref output for prints
    debug_file = None

    try:
        # redirect prints to debug file
        debug_file = open(os.path.join(dir, "debug.log"), "w")
        sys.stdout = debug_file
    except EnvironmentError:
        # if error, restore output to log window
        print "Error opening debug file"
        traceback.print_exception()
        sys.stdout = __stdout__

    # execute ameloadj
    [A, B, C, D, x, u, y, t, xvals] = ameloadj(file)

    # restore prints
    sys.stdout = __stdout__

    return A, B, C, D, x, u, y, t, xvals

def ameloadjlight(file):
    """
    same as legacy 'ameloadj()' without parsing '_.la' and '_.state' files
    return error if system is not SISO (mandatory here)
    :param file:
    :return: A, B, C, D
    """
    EPSILON_CMPLX = 1.0e-7

    #####################################################
    # Constants related to Unique Identifier management #
    #####################################################
    strip_unique_identifier = True
    unique_identifier_keyword = 'Data_Path'
    unique_identifier_search_regex = ' ' + unique_identifier_keyword + '=.*@\S*'

    jname = file
    X = []

    #####################
    # Read state matrix #
    #####################

    # Open Jacobian file
    try:
        fid = open(jname, 'r')
    except:
        print 'error, can not open %s' % (jname)
        return

    read_line = fid.readline().strip()
    if read_line == '':
        fid.close()
        print 'empty file %s' % (jname)
        return
    nfree = int(read_line.split()[0])
    ncontrol = int(read_line.split()[1])  # Number of control inputs
    nobserve = int(read_line.split()[2])  # Number of outputs
    T = float(read_line.split()[3])  # Time

    # print 'ncontrol: %i' %ncontrol
    # print 'nobs: %i' % nobserve
    if (ncontrol != 1) or (nobserve != 1):
        return

    A = []
    if nfree != 0:
        if X != []:
            X = X[:nfree]  # Suppress implicit states

        for i in range(nfree):
            read_line = fid.readline().strip()
            templist = read_line.split()
            A.append([])
            for j in range(nfree):
                A[i].append(float(templist[j]))
    B = []
    B0 = []
    if (nfree != 0) and (ncontrol != 0):
        for i in range(nfree):
            read_line = fid.readline().strip()
            templist = read_line.split()
            B0.append([])
            for j in range(ncontrol):
                B0[i].append(float(templist[j]))
    B.append(B0)
    C = []
    if (nfree != 0) and (nobserve != 0):
        for i in range(nobserve):
            read_line = fid.readline().strip()
            templist = read_line.split()
            C.append([])
            for j in range(nfree):
                C[i].append(float(templist[j]))
    D = []
    D0 = []
    if (ncontrol != 0) and (nobserve != 0):
        for i in range(nobserve):
            read_line = fid.readline().strip()
            templist = read_line.split()
            D0.append([])
            for j in range(ncontrol):
                D0[i].append(float(templist[j]))
    D.append(D0)
    B0 = []
    D0 = []
    line_nil = fid.readline().strip()
    state_values = []
    if line_nil[:23] == 'Index of nilpotency is ':
        index_nil_pot = int(line_nil[23:])
        for iter_var in range(index_nil_pot):
            if (nfree != 0) and (ncontrol != 0):
                for i in range(nfree):
                    read_line = fid.readline().strip()
                    templist = read_line.split()
                    B0.append([])
                    for j in range(ncontrol):
                        B0[i].append(float(templist[j]))
            B.append(B0)
            B0 = []

            if (nobserve != 0) and (ncontrol != 0):
                for i in range(nobserve):
                    read_line = fid.readline().strip()
                    templist = read_line.split()
                    D0.append([])
                    for j in range(ncontrol):
                        D0[i].append(float(templist[j]))
            D.append(D0)
            D0 = []
    else:
        if nfree > 0:
            state_values.append(float(line_nil))
    if nfree > 0:
        while 1:
            read_line = fid.readline()
            if not read_line:
                break

            state_values.append(float(read_line.strip()))
    fid.close()
    return A, B, C, D

def getalias(amefile, var):
    """
    get alias from variable label given by ameloadj (u or y)
    return alias and submodel alis
    e.g. 'out@step', 'step' = getalias('test.ame', 'STEP0 instance 1 step output')
    """

    # parse full name
    i1 = var.find(' instance')
    submodel = var[0:i1]
    var = var[i1 + len(' instance '):]
    i2 = var.find(' ')
    instance = var[0:i2]
    variable = var[i2 + 1:]

    # find alias
    alias = amegetvaruifromname(amefile, submodel, int(instance), variable)[0]
    i = alias.find('@')
    subalias = alias[i + 1:]

    return alias, subalias

def ss2bode(A, B, C, D, fmin=0.01, fmax=100, tol=1.0e-9, N=200):
    '''
    Compute gain and phase for Bode plot from state space representation of a SISO model
    tol = threshold for assuming zero gain
    :return: freqHz, gaindB, phasedeg (Inf and NaN values are excluded)

    Note: might return empty lists if frequency response is all NaN (poor conditioning). To be
    improved with matrix balancing and Scipy 0.19
    '''

    # TO DO: implement balancing for large systems (not available in scipy 0.13.1, see linalg.matrix_balancing)
    H, Q = hessenberg(A, calc_q=True)
    H = np.matrix(H)
    Q = np.matrix(Q)

    # define frequency range for plot
    n1 = np.log10(fmin)
    n2 = np.log10(fmax)

    freqHz = np.logspace(n1, n2, N)
    p = 2 * np.pi * freqHz * 1j
    gaindB = np.zeros(N)
    phasedeg = np.zeros(N)
    n = len(A)
    for i in range(0, len(p)):
        # h = C * linalg.inv(p[i] * np.eye(n) - A) * B + D                      # method 1: limited robustness for n>>1
        # h = D - (C * Q) * linalg.inv(H - p[i] * np.eye(n)) * (Q.T * B)        # method 2: much better
        x = solve(H - p[i] * np.eye(n), Q.T * B)  # method 3: same as 2??
        h = D - (C * Q) * x
        if np.abs(h)[0][0] < tol or np.isnan(h[0][0]):
            gaindB[i] = -np.inf
            phasedeg[i] = 0.
        else:
            gaindB[i] = 20 * np.log10(np.abs(h)[0][0])
            phasedeg[i] = np.angle(h, deg=True)[0][0]
    phasedeg = np.unwrap(phasedeg * np.pi/180, discont=np.pi) * 180 / np.pi

    # restrict output to non-NaN data that would make other function fail
    i = np.nonzero(np.isfinite(gaindB))
    gaindB = gaindB[i]
    phasedeg = phasedeg[i]
    freqHz = freqHz[i]
    i = np.nonzero(np.isfinite(phasedeg))
    gaindB = gaindB[i]
    phasedeg = phasedeg[i]
    freqHz = freqHz[i]

    return freqHz, gaindB, phasedeg

def simFit(x, modType, kdB, fmin, fmax, dzmin, dzmax, t1, y1, f1, mag1, tic, timeout):
    """
    Compute Step response and/or Frequency response of given model with scaled parameters x
    (using fmin and fmax for unscaling and static gain k in dB)
    Compare to reference gain curve (y1=f(t1) or mag1=f(f1)) and return quadratic error function

    if elapsed time since t = tic > timeout, returns 0.0 to force exit of optimization loop
    """

    Jerr = 1000.            # default value if error during execution

    # time out management
    if time.time() - tic > timeout:
        # print "time out"
        return Jerr

    # un-scale parameters
    k = 10**(kdB / 20.)
    if modType not in [3, 5]:
        # natural frequency (bounded between fmin and fmax)
        fo = (fmax - fmin) * x[0] + fmin
        fo = np.max([fo, fmin])
        tau = 1 / (2 * np.pi * fo)
    if modType == 2:
        # damping (bounded between 0.001 and value to capture 2 time constants in 2 decades)
        dz = (dzmax - dzmin) * x[1] + dzmin
        dz = np.max([dz, dzmin])

    # assemble model
    if modType == 0:
        num = [0]
        den = [1]
    elif modType == 1:
        num = [k]
        den = [tau, 1]
    elif modType == 2:
        num = [k]
        den = [tau * tau, 2 * dz * tau, 1]
    elif modType == 3:
        num = [k]
        den = [1, 0]
    elif modType == 4:
        num = [k]
        den = [tau, 1, 0]
    elif modType == 5:
        num = [k]
        den = [1, 0, 0]

    sys = signal.lti(num, den)

    # check inputs
    modeStep = True if len(t1) > 0 else False
    modeBode = True if len(f1) > 0 else False
    if any(np.isnan(num)) or any(np.isnan(den)) or (modeStep == False and modeBode == False):
        return Jerr

    # compute Bode
    if modeBode:
        try:
            w = 2 * np.pi * f1
            w2, mag2, phase2 = signal.bode(sys, w=w)
            val, nrmsd = matchIndex(w, mag1, mag2)
            Jbode = 1. - val
        except:
            Jbode = Jerr
        J = Jbode

    # simulate step response
    if modeStep:
        try:
            [t2, y2] = signal.step(sys, T=t1)
            y2 = np.real(y2)
            val, nrmsd = matchIndex(t1, y1, y2)
            Jstep = 1. - val
        except:
            Jstep = Jerr
        J = Jstep

    # combine cost functions if mixed criteria
    if modeStep and modeBode:
        J = Jbode * Jstep

    # make sure output is not NaN (otherwise COBYLA might turn into infinite loops)
    if np.isnan(J):
        J = Jerr

    return J

def matchIndex(x, yref, y):
    """
    compute normalized root mean square deviation for signals yref = f(x) and y = f(x)
    returns: val, nrmsd
    with:
            val = 1 for perfect match, down to 0 otherwise
            nrmsd = 0 for perfect match, >0 otherwise
    """
    val = np.nan
    nrmsd = np.nan
    yref = np.real(yref)
    y = np.real(y)
    ymin = np.min(yref)
    ymax = np.max(yref)
    if (ymin == ymax) or (len(x) == 0):
        return val, nrmsd
    elif (len(yref) != len(x)) or (len(y) != len(x)):
        print "matchIndex: yref and y dimensions not matching"
        return val, nrmsd
    elif not all(np.isfinite(yref-y)):
        return val, nrmsd

    nrmsd = np.sum((yref - y) ** 2) / len(x)
    nrmsd = np.sqrt(nrmsd) / (ymax - ymin)
    val = np.max([0., 1.0 - nrmsd])
    return val, nrmsd
