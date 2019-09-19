# -*- coding: utf-8 -*-

__author__="Silun Zhang (silun.zhang@gmail.com)"

import os,sys
from PyQt5 import QtWidgets 
from interface.ui_mainform import Ui_MainForm


app = QtWidgets.QApplication(sys.argv)
ex = Ui_MainForm()
sys.exit(app.exec_()) 


