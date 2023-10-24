import sys

import qdarkstyle
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSize, QRect, Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QLCDNumber, QHBoxLayout, QApplication, QSizePolicy


class DisplayCurrentValues(QWidget):
    def __init__(self):
        super().__init__()

        self._x = None
        self._y = None
        self._z = None

        frame = QFrame()
        frame.setObjectName("frame")
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(6)

        layout = QHBoxLayout(frame)

        self.x_dv = DisplayValue("X", parent=self)
        self.y_dv = DisplayValue("Y", parent=self)
        self.z_dv = DisplayValue("Z", parent=self)

        layout.addWidget(self.x_dv)
        layout.addWidget(self.y_dv)
        layout.addWidget(self.z_dv)

        lay = QHBoxLayout()
        lay.addWidget(frame)

        self.setLayout(lay)

        self.display()

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = round(value)
        self.x_dv.value = self._x

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = round(value)
        self.y_dv.value = self._y

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = round(value)
        self.z_dv.value = self._z

    def display(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(
            """
            QFrame#frame {
                border: 0px solid rgba(255, 255, 255, 0.6);
                padding-top: 0px;
                padding-bottom: 0px;
                margin-top: 0px;
                margin-bottom: 0px;
                padding-right: 0px;
                padding-left: 0px;
                background-color: #14171f;
                border-radius: 40px;
            }
            """
        )
        # self.setMaximumHeight(150)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # print(self.size())
        super().resizeEvent(a0)
        self.x_dv.resize(self.size())
        self.y_dv.resize(self.size())
        self.z_dv.resize(self.size())

        print("window size:",self.size())


class DisplayValue(QWidget):
    def __init__(self, key: str, parent=None):
        self.parent = parent
        super().__init__()
        self._value = None

        self.label_font = QFont()
        self.label_font.setStyleHint(QFont.Courier)
        self.key_label = QLabel(key)
        self.key_label.setFont(self.label_font)

        frame = QFrame()
        frame.setObjectName("frame")
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(6)

        self.value_qlcd = QLCDNumber(self)
        self.value_qlcd.setDecMode()
        self.value_qlcd.display(self._value)
        self.value_qlcd.setFixedWidth(100)

        layout = QHBoxLayout(frame)

        layout.addWidget(self.key_label)
        layout.addWidget(self.value_qlcd)

        lay = QHBoxLayout()
        lay.addWidget(frame)

        self.setLayout(lay)

        self.display()

        self.prev_parent_size = None
        if self.parent is not None:
            self.prev_parent_size = self.parent.size()

    def resize(self, a0: QtCore.QSize) -> None:
        # flags to prevent visual issues
        resize_x = True
        resize_y = True
        if self.prev_parent_size is not None:
            if self.prev_parent_size.height() == a0.height():
                resize_y = False
            if self.prev_parent_size.width() == a0.width():
                resize_x = False

        print("self" + self.key_label.text() + ":", self.width(), self.height(), "minimums:", self.minimumWidth(),
              self.minimumHeight(), "resize x:", resize_x, "resize y", resize_y)

        if resize_x:
            width = round(a0.width() / 4)
        else:
            width = self.width()

        if resize_y:
            height = round(width / 3)  # round(a0.height() / 1.5)
        else:
            height = self.height()

        if width < self.minimumWidth():
            width = self.minimumWidth()
            height = self.minimumHeight()

        self.resizeElements(width, height)
        self.setFixedWidth(width)
        self.setFixedHeight(height)

        # re-set minimum size
        self.setMinimumWidth(175)
        self.setMinimumHeight(75)

        self.prev_parent_size = a0
        
        """width = round(a0.width() / 4)
        height = round(width/3)             # round(a0.height() / 1.5)
        if width < self.minimumWidth():
            width = self.minimumWidth()
            height = self.minimumHeight()

        self.resizeElements(width, height)
        self.setFixedWidth(width)
        self.setFixedHeight(height)

        # re-set minimum size
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)"""

    def resizeElements(self, width, height):
        # https://stackoverflow.com/questions/40861305/dynamically-change-font-size-of-qlabel-to-fit-available-space
        # total space available
        available_space = QRect(self.x(), self.y(), width, height)
        # get space taken by key_label
        text_space: QRect = QFontMetrics(self.label_font).boundingRect(self.key_label.text())

        factorw = (available_space.width() / 2) / float(text_space.width())
        factorh = (available_space.height() / 2) / float(text_space.height())
        factor = min(factorw, factorh)

        if factor < 0.95 or factor > 1.05:
            new_font_size = self.label_font.pointSizeF() * factor
            new_font = self.key_label.font()
            new_font.setPointSizeF(round(new_font_size * 0.7))
            self.key_label.setFont(new_font)

            # self.value_qlcd.setFixedHeight(new_font_size*1.4)
            qlcd_width = available_space.width()-new_font_size*5
            self.value_qlcd.setFixedWidth(qlcd_width)

    def display(self):
        """if self.parent is not None:
            print(self.parent.size())

        print(self.parent.size())"""

        self.setContentsMargins(0, 0, 0, 0)
        # font-size: 28px;
        self.setStyleSheet(
            """
            QLabel {

              text-align: center;

              margin-top: 0px;
              font-family: Arial, Helvetica, sans-serif;
              background-color: None;

            }

            QLCDNumber{
                color:red;
                background-color: None;
                margin: None;
            }

            QHBoxLayout {
                border-radius: 50%;
                background-color: gray;
                margin-top:0px;
                margin-bottom:0px;
                padding:None;
            }

            QFrame#frame {
                border: 1px dashed rgba(255, 255, 255, 0.6);
                border-radius: 6px;
            }


            """
        )

        palette = QtGui.QPalette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(255, 0, 0))
        # background color
        palette.setColor(palette.Background, QtGui.QColor(255, 0, 0))
        # "light" border
        palette.setColor(palette.Light, QtGui.QColor(255, 0, 0))
        # "dark" border
        palette.setColor(palette.Dark, QtGui.QColor(255, 0, 0))

        self.value_qlcd.setPalette(palette)
        self.value_qlcd.setDigitCount(8)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        self._value = round(val)
        self.value_qlcd.display(str(self._value))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    # First task
    window = DisplayCurrentValues()
    window.x = 288000
    window.y = 100000
    window.z = 5000
    window.resize(QSize(1229, 126))

    window.show()
    app.exec_()
