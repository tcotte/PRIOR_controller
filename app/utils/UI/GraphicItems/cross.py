from typing import Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class CrossItem(QGraphicsItem):

    def __init__(self, center_x_position: Union[int, None], center_y_position: Union[int, None]):
        super(CrossItem, self).__init__()
        if center_x_position is None:
            self._center_x_position = 0
        else:
            self._center_x_position = center_x_position

        if center_y_position is None:
            self._center_y_position = 0
        else:
            self._center_y_position = center_y_position

        self._size = 1
        self._color = QColor(Qt.black)
        self._thickness = 1

        self.setAcceptHoverEvents(False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = value

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, value: QColor) -> None:
        self._color = value

    @property
    def thickness(self) -> int:
        return self._thickness

    @thickness.setter
    def thickness(self, value: int) -> None:
        self._thickness = value

    def paint(self, painter, option, widget):
        pen = QPen(self._color)
        pen.setWidth(self._thickness)
        pen.setCosmetic(True)
        painter.setPen(pen)

        painter.drawLine(QPoint(round(self._center_x_position - self._size / 2), self._center_y_position),
                         QPoint(round(self._center_x_position + self._size / 2), self._center_y_position))
        painter.drawLine(QPoint(self._center_x_position, round(self._center_y_position - self._size / 2)),
                         QPoint(self._center_x_position, round(self._center_y_position + self._size / 2)))

    def boundingRect(self):
        return QRectF(round(self._center_x_position - self._size / 2), round(self._center_y_position - self._size / 2),
                      self._size, self._size)

    @property
    def center_x_position(self):
        return self._center_x_position

    @center_x_position.setter
    def center_x_position(self, value):
        self._center_x_position = value
        self.scene().update()
        # self.painter.update()

    @property
    def center_y_position(self):
        return self._center_y_position

    @center_y_position.setter
    def center_y_position(self, value):
        self._center_y_position = value
        self.scene().update()
        # self.painter.update()
