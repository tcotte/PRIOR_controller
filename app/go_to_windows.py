import sys
from typing import Union

import qdarkstyle
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QSpinBox, QVBoxLayout, QFormLayout, QLabel, QDialog, QDialogButtonBox, \
    QSpacerItem
from superqt import QLabeledSlider

from app.ui_utils import QHLine

Y_RANGE = (0, 100000)
X_RANGE = (0, 100000)
Z_RANGE = (0, 100000)


class GoToXY(QDialog):
    def __init__(self, x_position: Union[int, None], y_position: Union[int, None]):
        super().__init__()
        self._x_position = None
        self._y_position = None

        self.x_pos_sb = QSpinBox()
        self.x_pos_sb.setRange(*Y_RANGE)

        self.y_pos_sb = QSpinBox()
        self.y_pos_sb.setRange(*X_RANGE)

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Position X"), self.x_pos_sb)
        form_layout.addRow(QLabel("Position Y"), self.y_pos_sb)

        speed_label = QLabel("Speed")
        acceleration_label = QLabel("Acceleration")
        self.speed_slider = QLabeledSlider(Qt.Orientation.Horizontal)
        self.acceleration_slider = QLabeledSlider(Qt.Orientation.Horizontal)

        self.button_box = QDialogButtonBox()
        # self.button_box.addButton("Apply", QDialogButtonBox.AcceptRole)
        self.button_box.addButton(QDialogButtonBox.Ok)
        self.button_box.addButton(QDialogButtonBox.Close)

        main_layout.addLayout(form_layout)
        main_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        main_layout.addWidget(speed_label)
        main_layout.addWidget(self.speed_slider)
        main_layout.addWidget(acceleration_label)
        main_layout.addWidget(self.acceleration_slider)
        main_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        main_layout.addWidget(QHLine())
        main_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        self.connect_actions()

        # Construct
        self.x_position = x_position
        self.y_position = y_position

    def connect_actions(self) -> None:
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    @property
    def x_position(self) -> int:
        return self._x_position

    @x_position.setter
    def x_position(self, value: Union[int, None]):
        self._x_position = 0 if value is None else value
        self.x_pos_sb.setValue(self._x_position)

    @property
    def y_position(self) -> int:
        return self._y_position

    @y_position.setter
    def y_position(self, value: Union[int, None]):
        self._y_position = 0 if value is None else value
        self.y_pos_sb.setValue(self._y_position)

    # def valid(self):
    #     print("set to pos ({x}, {y})".format(x=self.x_pos_sb.value(), y=self.y_pos_sb.value()))


class GoToZ(QDialog):
    def __init__(self, z_position: Union[int, None]):
        super().__init__()
        self._z_position = None

        self.z_pos_sb = QSpinBox()
        self.z_pos_sb.setRange(*Z_RANGE)

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Position Z"), self.z_pos_sb)

        speed_label = QLabel("Speed")
        acceleration_label = QLabel("Acceleration")
        self.speed_slider = QLabeledSlider(Qt.Orientation.Horizontal)
        self.acceleration_slider = QLabeledSlider(Qt.Orientation.Horizontal)

        self.button_box = QDialogButtonBox()
        # self.button_box.addButton("Apply", QDialogButtonBox.AcceptRole)
        self.button_box.addButton(QDialogButtonBox.Ok)
        self.button_box.addButton(QDialogButtonBox.Close)

        main_layout.addLayout(form_layout)
        main_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        main_layout.addWidget(speed_label)
        main_layout.addWidget(self.speed_slider)
        main_layout.addWidget(acceleration_label)
        main_layout.addWidget(self.acceleration_slider)
        main_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        main_layout.addWidget(QHLine())
        main_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        self.connect_actions()

        # Construct
        self.z_position = z_position

    def connect_actions(self) -> None:
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    @property
    def z_position(self) -> int:
        return self._z_position

    @z_position.setter
    def z_position(self, value: Union[int, None]) -> None:
        self._z_position = 0 if value is None else value
        self.z_pos_sb.setValue(self._z_position)

    def valid(self):
        print("set to pos ({z})".format(z=self.z_pos_sb.value()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = GoToXY(x_position=1000, y_position=30000)
    # window.z = 12000000
    window.show()
    app.exec_()
