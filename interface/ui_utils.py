#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from scipy import signal
from scipy.linalg import hessenberg, solve
import glob, os, time, sys
from PyQt5.QtCore import Qt, QTimer, QRect, QSize
from PyQt5.QtGui import QColor, QPen, QPainterPath, QBrush, QPainter, QFontMetrics


class WorkflowViewerLight(QtWidgets.QWidget):
    """ Simplified version of WorkflowViewer from toolbox_ice with:
            - Look & feel from Study Manager"""

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

