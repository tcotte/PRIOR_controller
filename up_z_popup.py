import os
import os
import sys

import qdarkstyle
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QPoint, Qt, QSize
from PyQt5.QtGui import QPixmap, QPainter, QPolygon, QPen, QColor, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDialog, QHBoxLayout, QFrame
import qtawesome as qta

from app.ui_utils import QHLine


def clamp(min_val, max_val, x):
    return max(min_val, min(max_val, x))


class TooltipLabel(QLabel):
    '''
    QLabel affichant des informations lors du survol par la souris
    '''

    def __init__(self, label: str, tooltip_message: str):
        super(TooltipLabel, self).__init__(label)

        self.backgroundcolor = 'background-color : DarkSlateGray'
        self.maincolor = 'color : lightBlue'
        self.hovercolor = 'color : lightGray'

        tooltip = QLabel(tooltip_message)
        tooltip.setWindowFlag(Qt.FramelessWindowHint)
        tooltip.setStyleSheet(self.backgroundcolor)
        tooltip.setFrameShape(QFrame.StyledPanel)
        tooltip.setWindowFlag(Qt.Tool)
        tooltip.hide()
        self.tooltip = tooltip

        self.setStyleSheet(self.maincolor)

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super(TooltipLabel, self).mouseMoveEvent(event)
        screen = self.screen().geometry()
        frame = self.tooltip.frameGeometry()
        if event.globalPos().y() + frame.height() * 1.1 >= screen.bottom():
            x = clamp(screen.left(), screen.right() - frame.width(), event.globalPos().x() - frame.width() * 0.3)
            y = clamp(screen.top(), screen.bottom() - frame.height(), event.globalPos().y() - frame.height() * 1.2)
        else:
            x = clamp(screen.left(), screen.right() - frame.width(), event.globalPos().x() - frame.width() * 0.3)
            y = clamp(screen.top(), screen.bottom() - frame.height(), event.globalPos().y() + frame.height() * 0.2)
        self.tooltip.move(x, y)

    def enterEvent(self, event: QtCore.QEvent) -> None:
        super(TooltipLabel, self).enterEvent(event)
        self.setStyleSheet(self.hovercolor)
        self.tooltip.show()

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        super(TooltipLabel, self).leaveEvent(event)
        self.setStyleSheet(self.maincolor)
        self.tooltip.hide()

    def setBackgroundColor(self, color: str):
        self.backgroundcolor = 'background-color : ' + color
        self.tooltip.setStyleSheet(self.backgroundcolor)

    def setMainColor(self, color: str):
        self.maincolor = 'color : ' + color
        self.tooltip.setStyleSheet(self.maincolor)

    def setHoverColor(self, color: str):
        self.hovercolor = 'color : ' + color

    def setToolTipMessage(self, message: str):
        self.tooltip.setText(message)


class ZLegend(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel()

        pix_path = os.path.join(r"C:\Users\tristan_cotte\Pictures", "microscope_without_bckgd2.png")
        self.pixmap = QPixmap(pix_path)
        self.pixmap = self.pixmap.scaledToWidth(400)

        self.paint_arrow()
        label.setPixmap(self.pixmap)

        layout.addWidget(label)
        self.setLayout(layout)

    def paint_arrow(self):
        painter = QPainter(self.pixmap)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("orange")))

        start_point = QPoint(301, 360 - 40)

        points = QPolygon([
            QPoint(308, 260),
            QPoint(308, 304),
            QPoint(317, 304),
            start_point,
            QPoint(285, 304),
            QPoint(294, 304),
            QPoint(294, 260)
        ])

        painter.drawPolygon(points)
        painter.end()


class InfoZ(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(ZLegend())
        layout.addWidget(QHLine())
        explanation_label = QLabel("The colored arrow shows the upper direction in Z axis.")
        explanation_label.setStyleSheet("color: darkgray;")
        layout.addWidget(explanation_label, alignment=Qt.AlignCenter)
        self.setLayout(layout)


class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.icon = IconZInfo()
        layout.addWidget(self.icon)
        self.setLayout(layout)


class IconZInfo(QLabel):
    def __init__(self):
        super().__init__()
        self.setPixmap(qta.icon('ph.info-bold', color_off=QColor(100, 150, 215)).pixmap(18, 18))

        self.window = InfoZ()
        self.window.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.setFixedSize(QSize(20, 20))

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        pt0 = QCursor().pos()

        y_ceil = (pt0.y() - self.window.height()) if (pt0.y() - self.window.height()) > 0 else 0
        self.window.move(pt0.x() + 20, y_ceil)

        self.window.show()

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self.window.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    w = TestWidget()
    # window.z = 12000000
    w.show()
    app.exec_()
