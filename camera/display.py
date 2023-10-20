# \file    display.py
# \author  IDS Imaging Development Systems GmbH
# \date    2021-01-15
# \since   1.2.0
#
# \brief   The Display class implements an easy way to display images from a
#          camera in a QT widgets window. It can be used for other QT widget
#          applications as well.
#
# \version 1.3.0
#
# Copyright (C) 2021 - 2023, IDS Imaging Development Systems GmbH.
#
# The information in this document is subject to change without notice
# and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
# IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
# that may appear in this document.
#
# This document, or source code, is provided solely as an example of how to utilize
# IDS Imaging Development Systems GmbH software libraries in a sample application.
# IDS Imaging Development Systems GmbH does not assume any responsibility
# for the use or reliability of any portion of this document.
#
# General permission to copy or modify is hereby granted.

import math


from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QRectF, pyqtSignal


class Display(QGraphicsView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.scene = CustomGraphicsScene(self)
        self.setScene(self.scene)

    def on_image_received(self, image: QImage):
        self.scene.set_image(image)
        self.update()

    def get_image(self):
        return self.scene.get_image()


class CustomGraphicsScene(QGraphicsScene):

    backgroundUpdate = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super(CustomGraphicsScene, self).__init__(parent)
        self.parent = parent
        self.image = QImage()

        self.view_width = 1
        self.view_height = 1
        self.image_ratio = 1

        self.setItemIndexMethod(QGraphicsScene.NoIndex)

    def debug(self):
        print('letsgo')

    def set_image(self, image: QImage) -> None:
        self.image = image
        image_width, image_height = self.getImageSize()
        self.image_ratio = image_width / image_height
        self.update()

    def getImageRatio(self):
        return(self.image_ratio)

    def getImageSize(self):
        return self.image.width(), self.image.height()

    def getZoomState(self):
        return(self.parent.getZoomState())

    def get_image(self):
        """
        Get the raw picture displayed on the QGraphicsScene
        :return: OPenCV RGB picture
        """
        return self.image.copy()

    def getRealImageSize(self):
        try:
            binning = self.parent.parent.camera.nodemap_remote_device.FindNode("BinningHorizontal").Value()
        except:
            binning = 1
        try:
            decimation = self.parent.parent.camera.nodemap_remote_device.FindNode("DecimationHorizontal").Value()
        except:
            decimation = 1

        return(self.image.size().width() * binning * decimation, self.image.size().height() * binning * decimation)

    def getBinningRatio(self):
        scene_resolution = self.get_bckgd_size()
        max_resolution = self.getRealImageSize()
        return max_resolution[0] / scene_resolution[0]

    def get_bckgd_size(self) -> [float, float]:
        """
        Get the background size in function of the display and the camera image sizes. No matter the sizes, the scene
        has to keep the aspect ratio of the camera picture.
        :return: image scene width, image scene height
        """
        # Image size
        image_width = self.image.width()
        image_height = self.image.height()

        if image_width == 0 or image_height == 0:
            print("no img")
            return 1, 1

        return image_width, image_height

    def computeSceneRect(self) -> QRectF:
        """
        Gives the SceneRect that should be used according to the current image flux
        :return: QRectF
        """
        image_width, image_height = self.get_bckgd_size()

        image_pos_x = -1.0 * (image_width / 2.0)
        image_pox_y = -1.0 * (image_height / 2.0)

        # Remove digits after point
        image_pos_x = math.trunc(image_pos_x)
        image_pox_y = math.trunc(image_pox_y)

        return QRectF(image_pos_x, image_pox_y, image_width, image_height)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        """
        Paint the scene background with the camera picture respecting its aspect ratio.

        The point (0, 0) will be the middle of the scene -> point '0' in the picture below.
        The point (-iw /2, -ih /2) wil be the top corner of the scene ->  point 'A' in the picture below.
        The point (+iw /2, +ih /2) wil be the top corner of the scene ->  point 'D' in the picture below.

        A -------------------- |
        |                      |
        |          0           |
        |                      |
        | -------------------- D

        With :
        - iw -> image width
        - ih -> image height

        :param painter:
        :param rect:
        """
        rect = self.computeSceneRect()
        painter.drawImage(rect, self.image)

        self.backgroundUpdate.emit(rect.width(), rect.height())
        self.setSceneRect(rect)

        # Visualisation du viewport
        #painter.setPen(QtGui.QColor(0,0,255,255))
        #painter.drawRect(self.parent.visible_rect)

        #painter.drawPoint(self.parent.getVisibleRect().center())

    def print_dimensions(self) -> None:
        image_width, image_height = self.get_bckgd_size()
        print('img : ', image_width, image_height)
        print('scene : ', self.width(), self.height())

