from typing import List, Union

import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QWidget
from numpy import ndarray



class Display(QGraphicsView):

    viewScaled = QtCore.pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.parent = parent

        self.visible_rect = self.getVisibleRect()

        ### Zoom parameters ###
        self.zoom_level = 0
        self.zoom_max = 20
        self.zoom_min = 0
        self.zoom_speed = 1.25

        self.setDragMode(QGraphicsView.NoDrag)
        # self.setRubberBandEnabled(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        ### MousePressed and SpaceBar state tracking ###

        self.mouse_pressed = False
        self.space_pressed = False

    ### Gestion du zoom ###

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Detect event of the mouse wheel to enable zoom
        :param event: enables to detect the delta of the mouse before calling zoom function
        """
        self.zoom(event.angleDelta().y())

    def zoom(self, direction: float) -> None:
        """
        Creation of zoom on Display class in function of a factor
        :param factor: float factor of zoom
        """
        if direction < 0:
            if self.zoom_level > self.zoom_min:
                factor = 1 / self.zoom_speed
                self.zoom_level -= 1
            else:
                factor = 1
        elif direction > 0:
            if self.zoom_level < self.zoom_max:
                factor = self.zoom_speed
                self.zoom_level += 1
            else:
                factor = 1

        self.scale(factor, factor)
        self.visible_rect = self.getVisibleRect()
        self.viewScaled.emit()

    def setZoomLevel(self, level: int):
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        if level >= self.zoom_min:
            self.fitView()
            for i in range(self.zoom_min, min(self.zoom_max, level)):
                self.zoom(1)
            self.zoom_level = min(self.zoom_max, level)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def getZoomLevel(self):
        return(self.zoom_level)

    def setZoomSpeed(self, speed: float):
        self.zoom_speed = speed

    def getZoomSpeed(self):
        return(self.zoom_speed)

    def getZoomState(self):
        return(self.transform().m11())

    def getDisplaySize(self):
        return self.width(), self.height()

    def getVisibleRect(self):
        view_rect = self.viewport().rect()
        A = self.mapToScene(view_rect.topLeft())
        B = self.mapToScene(view_rect.bottomRight())
        rect = QRectF(A, B)
        return(rect)

    def adaptView(self):
        self.fitView()
        self.viewScaled.emit()

    def fitView(self):
        rect = self.sceneRect()
        self.fitInView(rect, Qt.KeepAspectRatio)
        self.zoom_level = 0

    @pyqtSlot(QImage)
    def on_image_received(self, image: QImage):
        self.scene().set_image(image)
        self.update()

    def on_new_image_flux(self):
        self.fitView()
        self.visible_rect = self.getVisibleRect()
        self.zoom_max = 25

    @staticmethod
    def convertQImageToMat(incoming_image: QImage):
        """
        Converts a QImage into an opencv MAT format
        :param incoming_image:
        :return: OpenCV RGB picture
        """
        incoming_image = incoming_image.convertToFormat(4)

        width = incoming_image.width()
        height = incoming_image.height()

        ptr = incoming_image.bits()
        ptr.setsize(incoming_image.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
        return arr

    def get_image(self) -> ndarray:
        """
        Get the raw picture displayed on the QGraphicsView
        :return: OPenCV RGB picture
        """
        image = self.scene().get_image()
        # image = QImage()
        return self.convertQImageToMat(image)

    ### Event Handler ###

    def enterEvent(self, event: QtCore.QEvent) -> None:
        self.setFocus()
        super(Display, self).enterEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.adaptView()
        super(Display, self).resizeEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super(Display, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Space:
            if event.isAutoRepeat():
                return
            else:
                self.space_pressed = True
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                self.setInteractive(False)
        if event.key() == QtCore.Qt.Key.Key_D:
            self.setZoomLevel(10)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        super(Display, self).keyReleaseEvent(event)
        if event.key() == QtCore.Qt.Key_Space:
            print("space")
            if event.isAutoRepeat():
                return
            else:
                self.space_pressed = False
                if self.mouse_pressed:
                    return
                self.setDragMode(QGraphicsView.NoDrag)
                self.setInteractive(True)
                self.unsetCursor()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_pressed = True
        super(Display, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super(Display, self).mouseReleaseEvent(event)
        self.mouse_pressed = False

