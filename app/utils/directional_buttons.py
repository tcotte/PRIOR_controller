import sys
import typing

import qdarkstyle
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, QEvent, Qt
from PyQt5.QtGui import QKeyEvent, QWindowStateChangeEvent
from PyQt5.QtWidgets import QWidget, QGridLayout, QLayout, QApplication, QHBoxLayout
import qtawesome as qta

from long_click_w import LongClickButton


class Directions:
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class DirectionalButtons(QWidget):
    def __init__(self, size_btn: typing.Union[int, None] = None, only_two: bool = False):
        super().__init__()
        if size_btn is None:
            size_btn = 100
        self.radius = round(size_btn / 2)

        self.only_two = only_two

        self.up_button = ArrowButton(Directions.UP, round(size_btn))
        self.down_button = ArrowButton(Directions.DOWN, round(size_btn))

        if not only_two:
            self.left_button = ArrowButton(Directions.LEFT, round(size_btn))
            self.right_button = ArrowButton(Directions.RIGHT, round(size_btn))

        layout = QGridLayout()
        layout.setObjectName('layout')
        """
        layout.addWidget(self.up_button, 0, 1, 1, 1)
        if not only_two:
            layout.addWidget(self.left_button, 1, 0, 1, 1)
            layout.addWidget(self.right_button, 1, 2, 1, 1)
        else:
            space = QWidget()
            space.setFixedSize(QSize(size_btn, size_btn))
            layout.addWidget(space, 1, 0, 1, 1)
        layout.addWidget(self.down_button, 2, 1, 1, 1)
        """
        if not only_two:
            layout.addWidget(self.up_button, 0, 1)
            layout.addWidget(self.left_button, 1, 0)
            layout.addWidget(self.right_button, 1, 2)
            layout.addWidget(self.down_button, 2, 1)
        else:
            layout.addWidget(self.up_button, 0, 0)
            space = QWidget()
            space.setFixedSize(QSize(size_btn, size_btn))
            layout.addWidget(space, 1, 0)
            layout.addWidget(self.down_button, 2, 0)

        # layout.setSizeConstraint(QLayout.SetFixedSize)

        # create a parent widget for the buttons to have a more flexible control over the button layout
        self.button_holder = QWidget()
        self.button_holder.setLayout(layout)
        layout_button_holder = QHBoxLayout()
        layout_button_holder.addWidget(self.button_holder)

        self.setMinimumSize(QSize(100, 100))

        self.setLayout(layout_button_holder)

        self.display()

        self.connect_actions()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        # create square size
        # if using only self.width() or self.height() without trimming the values, the window will endlessly resize itself
        size = QSize(min(int(self.width() / 1.5), int(self.height() / 1.5)), min(int(self.width() / 1.5), int(self.height() / 1.5)))
        # buttons sizes
        btn_size = QSize(min(int(size.width() / 4), int(size.height() / 4)),
                         min(int(size.width() / 4), int(size.height() / 4)))
        self.button_holder.setFixedSize(size)
        self.resize_buttons(btn_size)

    def resize_buttons(self, size=None):
        if not self.only_two:
            list_btns = [self.up_button, self.left_button, self.right_button, self.down_button]
        else:
            list_btns = [self.up_button, self.down_button]
        if size is not None:
            w = size.width()
            h = size.height()
        else:
            w = self.size().width() / 4
            h = self.size().height() / 4
        # print(w, h)
        for btn in list_btns:
            btn.resize_icon(QSize(round(min(w, h)), round(min(w, h))))

    def connect_actions(self):
        if not self.only_two:
            list_btns = [self.up_button, self.left_button, self.right_button, self.down_button]
        else:
            list_btns = [self.up_button, self.down_button]

        for btn in list_btns:
            btn.clicked.connect(lambda: self.setFocus())

    def keyPressEvent(self, e: QKeyEvent) -> None:
        key_right = 16777236
        key_left = 16777234
        key_up = 16777235
        key_down = 16777237

        if not self.only_two:
            if e.key() == key_down:
                self.down_button.animateClick()
            elif e.key() == key_up:
                self.up_button.animateClick()
            elif e.key() == key_right:
                self.right_button.animateClick()
            elif e.key() == key_left:
                self.left_button.animateClick()
        else:
            if e.key() == key_down:
                self.down_button.animateClick()
            elif e.key() == key_up:
                self.up_button.animateClick()

        super().keyPressEvent(e)

    def display(self):
        self.setStyleSheet(
            """
            layout {
                margin: 500px;
            }
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


class ArrowButton(LongClickButton):

    def __init__(self, direction: int, size_btn: int):
        if direction == Directions.LEFT:
            name = "left"
        elif direction == Directions.RIGHT:
            name = "right"
        elif direction == Directions.UP:
            name = "up"
        else:
            name = "down"
        icon = qta.icon(f"ri.arrow-{name}-s-line")
        super(ArrowButton, self).__init__(icon, '')

        self.setFixedSize(QSize(size_btn, size_btn))
        self.setIconSize(QSize(size_btn, size_btn))
        self.setObjectName(name)

    def resize_icon(self, size: QSize):
        self.setFixedSize(size)
        self.setIconSize(size)

        # re-set the button's border radius acccording to its new size
        self.setStyleSheet(
            """
            QPushButton {
                border-radius: %s;
            }
            """ % str(int(self.iconSize().width()/2))
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    # Second task
    window = DirectionalButtons(size_btn=50)
    second_window = DirectionalButtons(size_btn=50, only_two=True)
    second_window.show()

    # Third task
    # window = DirectionalButtons(size_btn=50, only_two=True)

    window.show()
    app.exec_()