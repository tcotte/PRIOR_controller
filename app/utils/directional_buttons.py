import sys
import typing

import qdarkstyle
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QGridLayout, QLayout, QApplication
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

        up_icon = qta.icon('ri.arrow-up-s-line')
        self.up_button = LongClickButton(up_icon, '')
        self.up_button.setFixedSize(QSize(size_btn, size_btn))
        self.up_button.setIconSize(QSize(round(size_btn), round(size_btn)))
        self.up_button.setObjectName('up')

        down_icon = qta.icon('ri.arrow-down-s-line')
        self.down_button = LongClickButton(down_icon, '')
        self.down_button.setFixedSize(QSize(size_btn, size_btn))
        self.down_button.setIconSize(QSize(round(size_btn), round(size_btn)))
        self.down_button.setObjectName('down')

        if not only_two:
            left_icon = qta.icon('ri.arrow-left-s-line')
            self.left_button = LongClickButton(left_icon, '')
            self.left_button.setFixedSize(QSize(size_btn, size_btn))
            self.left_button.setIconSize(QSize(round(size_btn), round(size_btn)))
            self.left_button.setObjectName('left')

            right_icon = qta.icon('ri.arrow-right-s-line')
            self.right_button = LongClickButton(right_icon, '')
            self.right_button.setFixedSize(QSize(size_btn, size_btn))
            self.right_button.setIconSize(QSize(round(size_btn), round(size_btn)))
            self.right_button.setObjectName('right')

        layout = QGridLayout()
        layout.setObjectName('layout')
        layout.addWidget(self.up_button, 0, 1, 1, 1)
        if not only_two:
            layout.addWidget(self.left_button, 1, 0, 1, 1)
            layout.addWidget(self.right_button, 1, 2, 1, 1)
        else:
            space = QWidget()
            space.setFixedSize(QSize(size_btn, size_btn))
            layout.addWidget(space, 1, 0, 1, 1)
        layout.addWidget(self.down_button, 2, 1, 1, 1)

        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

        self.display()

        self.connect_actions()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))



    # Second task
    # window = DirectionalButtons(size_btn=50)

    # Third task
    window = DirectionalButtons(size_btn=50, only_two=True)

    window.show()
    app.exec_()