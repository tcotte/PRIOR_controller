import sys

import qdarkstyle
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QLCDNumber, QHBoxLayout, QApplication


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
                padding-right: 40px;
                padding-left: 40px;
                background-color: #14171f;
                border-radius: 50px;
            }
            """
        )
        self.setMaximumHeight(150)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        print(self.size())
        super().resizeEvent(a0)
        # self.x_dv.resize(self.size())
        # self.y_dv.resize(self.size())
        # self.z_dv.resize(self.size())


class DisplayValue(QWidget):
    def __init__(self, key: str, parent=None):
        self.parent = parent
        super().__init__()
        self._value = None

        label_font = QFont()
        label_font.setStyleHint(QFont.Courier)
        key_label = QLabel(key)
        key_label.setFont(label_font)

        frame = QFrame()
        frame.setObjectName("frame")
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(6)

        self.value_qlcd = QLCDNumber()
        self.value_qlcd.setDecMode()
        self.value_qlcd.display(self._value)

        layout = QHBoxLayout(frame)

        layout.addWidget(key_label)
        layout.addWidget(self.value_qlcd)

        lay = QHBoxLayout()
        lay.addWidget(frame)

        self.setLayout(lay)

        self.display()

    def resize(self, a0: QtCore.QSize) -> None:
        self.setFixedWidth(round(a0.width() / 5))
        self.setFixedHeight(round(a0.height() / 2))
        print(round(self.parent.size().width() / (640 / 400)), round(self.parent.size().height() / (480 / 90)))

    def display(self):
        if self.parent is not None:
            print(self.parent.size())

        print(self.parent.size())

        self.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet(
            """
            QLabel {

              text-align: center;

              margin-top: 0px;
              font-size: 28px;
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