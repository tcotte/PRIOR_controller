import sys
import typing

import qdarkstyle
import qtawesome as qta
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLCDNumber, \
    QLabel, QFrame, QSizePolicy, QLayout, QSpacerItem
from superqt import QLabeledSlider

from app.ui_utils import QHLine, AnimatedOnHoverButton


class DirectionalButtons(QWidget):
    def __init__(self, size_btn: typing.Union[int, None] = None):
        super().__init__()
        if size_btn is None:
            size_btn = 100

        self.radius = round(size_btn / 2)

        up_icon = qta.icon('ri.arrow-up-s-line')
        self.up_button = QPushButton(up_icon, '')
        self.up_button.setFixedSize(QSize(size_btn, size_btn))
        self.up_button.setIconSize(QSize(round(size_btn), round(size_btn)))
        self.up_button.setObjectName('up')

        left_icon = qta.icon('ri.arrow-left-s-line')
        self.left_button = QPushButton(left_icon, '')
        self.left_button.setFixedSize(QSize(size_btn, size_btn))
        self.left_button.setIconSize(QSize(round(size_btn), round(size_btn)))
        self.left_button.setObjectName('left')

        right_icon = qta.icon('ri.arrow-right-s-line')
        self.right_button = QPushButton(right_icon, '')
        self.right_button.setFixedSize(QSize(size_btn, size_btn))
        self.right_button.setIconSize(QSize(round(size_btn), round(size_btn)))
        self.right_button.setObjectName('right')

        down_icon = qta.icon('ri.arrow-down-s-line')
        self.down_button = QPushButton(down_icon, '')
        self.down_button.setFixedSize(QSize(size_btn, size_btn))
        self.down_button.setIconSize(QSize(round(size_btn), round(size_btn)))
        self.down_button.setObjectName('down')

        layout = QGridLayout()
        layout.setObjectName('layout')
        layout.addWidget(self.up_button, 0, 1, 1, 1)
        layout.addWidget(self.left_button, 1, 0, 1, 1)
        layout.addWidget(self.right_button, 1, 2, 1, 1)
        layout.addWidget(self.down_button, 2, 1, 1, 1)

        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

        self.display()

        self.connect_actions()

    def connect_actions(self):
        for btn in [self.up_button, self.left_button, self.right_button, self.down_button]:
            btn.clicked.connect(lambda: self.setFocus())

    def keyPressEvent(self, e: QKeyEvent) -> None:
        key_right = 16777236
        key_left = 16777234
        key_up = 16777235
        key_down = 16777237

        if e.key() == key_right:
            self.right_button.animateClick()
        elif e.key() == key_left:
            self.left_button.animateClick()
        elif e.key() == key_down:
            self.down_button.animateClick()
        elif e.key() == key_up:
            self.up_button.animateClick()

        super().keyPressEvent(e)

    def display(self):
        self.setStyleSheet(
            """
            QPushButton {
            display: inline-block;
            background-color: #4CAF50;
            
            color: #fff;
            text-align: center;

            text-decoration: none;
            border-radius: %s;
            }     
            
            QPushButton:hover {
                background-color: #6ccc70;
            }
            
            QPushButton:pressed {
                background-color: #b7c4b7;     
            }
            """ % (str(self.radius)))


class XYHandler(QWidget):
    def __init__(self):
        super().__init__()

        # arrows
        # speed
        # acceleration

        self.xy_directions = DirectionalButtons(size_btn=50)
        self.xy_directions.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_btn = QHBoxLayout()
        hspacer = QSpacerItem(100, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.go_to_btn = AnimatedOnHoverButton("GO TO", duration=300)

        self.home_btn = AnimatedOnHoverButton("HOME", duration=300)

        layout_btn.addWidget(self.go_to_btn)
        layout_btn.addItem(hspacer)
        layout_btn.addWidget(self.home_btn)

        speed_label = QLabel("Speed")
        acceleration_label = QLabel("Acceleration")

        self.speed_slider = QLabeledSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setGeometry(10, 10, 30, 400)
        self.acceleration_slider = QLabeledSlider(Qt.Orientation.Horizontal)

        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.xy_directions)
        layout.addItem(spacer)
        layout.addLayout(layout_btn)
        layout.addItem(spacer)
        layout.addWidget(QHLine())
        layout.addItem(spacer)
        layout.addWidget(speed_label)
        layout.addWidget(self.speed_slider)
        layout.addItem(spacer)
        layout.addWidget(acceleration_label)
        layout.addWidget(self.acceleration_slider)
        layout.addItem(spacer)

        self.setLayout(layout)

        self.connect_actions()
        self.display()

    def connect_actions(self) -> None:
        self.go_to_btn.clicked.connect(self.open_absolute_position_window)

    def open_absolute_position_window(self) -> None:
        print("win")

    def display(self):
        self.setStyleSheet(
            """
            QPushButton#a {
                -webkit-transition: all 200ms cubic-bezier(0.390, 0.500, 0.150, 1.360);
                -moz-transition: all 200ms cubic-bezier(0.390, 0.500, 0.150, 1.360);
                -ms-transition: all 200ms cubic-bezier(0.390, 0.500, 0.150, 1.360);
                -o-transition: all 200ms cubic-bezier(0.390, 0.500, 0.150, 1.360);
                transition: all 200ms cubic-bezier(0.390, 0.500, 0.150, 1.360);
                display: block;
                margin: 20px auto;
                max-width: 180px;
                text-decoration: none;
                border-radius: 4px;
                padding: 20px 30px;
            }
            
            
            QPushButton#a {
                color: #fff;
                border: 2px solid rgba(255, 255, 255, 0.6);
                text-align: center;
    
                text-decoration: none;
                border-radius: 20px;
                

                box-shadow: rgba(30, 22, 54, 0.4) 0 0px 0px 2px inset;
                background-color: None;
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#a:hover {
                color: rgba(255, 255, 255, 0.85);
                box-shadow: rgba(30, 22, 54, 0.7) 0 0px 0px 40px inset;
            }
            
            """
        )


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

        self.x_dv = DisplayValue("X")
        self.y_dv = DisplayValue("Y")
        self.z_dv = DisplayValue("Z")

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
        print(self._z)
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


class DisplayValue(QWidget):
    def __init__(self, key: str):
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

    def display(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(400)
        self.setFixedHeight(90)
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


class Window(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        xy_widget = XYHandler()
        xy_widget.setFixedSize(QSize(500, 500))

        self.display_values = DisplayCurrentValues()
        layout.addWidget(xy_widget)
        layout.addWidget(self.display_values)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = Window()
    window.display_values.x = 5000
    # window.z = 12000000
    window.show()
    app.exec_()
