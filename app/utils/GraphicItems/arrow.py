import math
from typing import Final

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Arrow(QGraphicsPathItem):
    #  draw an arrow like this
    #                           |\
    #                ___   _____| \
    #    length_width |   |        \  _____
    #                _|_  |_____   /    |
    #                           | /     | arrow_width
    #                           |/    __|__
    #
    #                           |<->|
    #                        arrow_height
    def __init__(self, source: QtCore.QPointF, destination: QtCore.QPointF, arrow_height, arrow_width, length_width,
                 *args, **kwargs):
        super(Arrow, self).__init__(*args, **kwargs)

        self._sourcePoint = source
        self._destinationPoint = destination

        self._arrow_height = arrow_height
        self._arrow_width = arrow_width
        self._length_width = length_width

    def boundingRect(self):
        x0 = self._sourcePoint.x()
        y0 = self._sourcePoint.y() - self._arrow_width
        x1 = self._destinationPoint.x()
        y1 = self._destinationPoint.y() + self._arrow_width
        return QtCore.QRectF(QPointF(x0, y0), QPointF(x1, y1))

    def arrowCalc(self, start_point=None, end_point=None):  # calculates the point where the arrow should be drawn

        try:
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self._sourcePoint

            if endPoint is None:
                endPoint = self._destinationPoint

            dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

            leng = math.sqrt(dx ** 2 + dy ** 2)
            normX, normY = dx / leng, dy / leng  # normalize

            # parallel vector (normX, normY)
            # perpendicular vector (perpX, perpY)
            perpX = -normY
            perpY = normX

            #           p2
            #           |\
            #    p4____p5 \
            #     |        \ endpoint
            #    p7____p6  /
            #           | /
            #           |/
            #          p3
            point2 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height + QtCore.QPointF(perpX,
                                                                                                   perpY) * self._arrow_width
            point3 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height - QtCore.QPointF(perpX,
                                                                                                   perpY) * self._arrow_width

            point4 = startPoint + QtCore.QPointF(perpX, perpY) * self._length_width
            point5 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height + QtCore.QPointF(perpX,
                                                                                                   perpY) * self._length_width
            point6 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height - QtCore.QPointF(perpX,
                                                                                                   perpY) * self._length_width
            point7 = startPoint - QtCore.QPointF(perpX, perpY) * self._length_width

            polygon = QPolygonF([point4, point5, point2, endPoint, point3, point6, point7])
            return polygon

        except (ZeroDivisionError, Exception):
            return None

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        # painter.setRenderHint(painter.Antialiasing)

        my_pen = QtGui.QPen()
        my_pen.setWidth(1)
        my_pen.setCosmetic(False)
        my_pen.setColor(QtGui.QColor(0, 0, 0, 100))
        painter.setPen(my_pen)

        painter.setBrush(QColor(0, 0, 0, 200))

        arrow_polygon = self.arrowCalc()
        if arrow_polygon is not None:
            # painter.drawPolyline(arrow_polygon)
            painter.drawPolygon(arrow_polygon)
