import functools
from typing import Union

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFrame, QPushButton


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        """
        Gray horizontal line which can be insert in layout.
        """
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: gray")
        self.setFixedHeight(1)


class AnimatedOnHoverButton(QPushButton):
    def __init__(self, parent, font_color: Union[None, QtGui.QColor] = None,
                 background_color: Union[None, QtGui.QColor] = None,
                 duration: int = 800):
        super().__init__(parent)
        if background_color is None:
            self._background_color = QtGui.QColor("#19232D")
        else:
            self._background_color = background_color

        if font_color is None:
            self._font_color = QtGui.QColor("white")
        else:
            self._font_color = font_color

        self._duration = duration

        self.display()

    def display(self):
        self.style_sheet = """
                            display: block;
                            text-decoration: none;
                            border-radius: 4px;
                            padding: 20px 30px;

                            color: %s;
                            border: 2px solid %s;
                            text-align: center;

                            text-decoration: none;
                            border-radius: 20px;


                            background-color: %s;
                            font-family: Arial, sans-serif;
                            font-weight: bold;
                            font-size: 14px;
                            """ % (self._font_color.name(), self._font_color.name(), self._background_color.name())

        self.setStyleSheet(self.style_sheet)

    def helper_function(self, color, other_color):

        self.setStyleSheet(
            self.style_sheet + "background-color: {bckgd};  color: {font};".format(bckgd=other_color.name(),
                                                                                   font=color.name()))

    def apply_color_animation(self, start_color, end_color, duration=1000):
        anim = QtCore.QVariantAnimation(
            self,
            duration=duration,
            startValue=start_color,
            endValue=end_color,
            loopCount=1,
        )
        anim.valueChanged.connect(functools.partial(self.helper_function, start_color))
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.apply_color_animation(
            start_color=self._background_color,
            end_color=self._font_color,
            duration=self._duration
        )
        super().enterEvent(a0)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self.apply_color_animation(
            start_color=self._font_color,
            end_color=self._background_color,
            duration=self._duration
        )
        super().leaveEvent(a0)