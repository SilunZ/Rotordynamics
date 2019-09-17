# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/msdvyv/AppData/Local/Temp/tmp80027/mainform.ui'
#
# Created: Tue Nov 06 15:42:06 2018
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainForm(object):
    
    def doAutoAssociations(self, appObject):
        pass

    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(400, 300)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

    def retranslateUi(self, MainForm):
        MainForm.setWindowTitle(QtWidgets.QApplication.translate("MainForm", "PID tuning", None, -1))

