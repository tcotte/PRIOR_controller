import sys
import threading
import time
import typing
from typing import Union
import qtawesome as qta
import qdarkstyle
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QSize
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QPushButton, QFormLayout, QSpacerItem
from qtwidgets import AnimatedToggle
from serial import SerialTimeoutException

from app.go_to_windows import GoToXY, GoToPosition
from app.ui import DisplayCurrentValues, DirectionalButtons, Directions, GeneralCommands
from app.ui_utils import TitleSectionLabel, FormLabel, AnimatedOnHoverButton, MapButton
from app.utils.position import Position

from main import PriorController

connected = False

port = 'COM15'  # replace this with your port

baud = 9600  # Baud rate


class MicroscopeHandler(QObject):
    change_coord_signal = pyqtSignal(object)
    reach_position_signal = pyqtSignal()

    def __init__(self, prior, parent=None):
        super().__init__(parent)
        self._current_coords = None
        self.prior = prior
        self._is_running = True
        self._position_reached = True

        read_position_thread = threading.Thread(target=self.read_prior_position)
        # self.write_thread = threading.Thread(target=self.write_to_port, args=(self.prior, Position(10, 20), 2))

        read_position_thread.start()

        # self.write_thread.start()

    def close(self):
        self._is_running = False

    def read_prior_position(self, delay: float = 0.1):
        while self._is_running:
            try:
                self.prior.write_cmd("P")
            except SerialTimeoutException:
                print("Can\'t write due to timeout")

            while self.prior.in_waiting > 0:  # Wait for response
                reading = self.prior.read_until(b"\r").decode().strip()

                # if reading.endswith('<R>\n'):
                self.handle_data(reading)

                break

            # time.sleep(0.5)
            time.sleep(delay)

    def return2home(self):
        thread_return2home = threading.Thread(target=self.return2home_with_thread)
        thread_return2home.start()

    def return2home_with_thread(self):
        while True:
            if self.prior.in_waiting > 0 and self._position_reached:
                # # print("set position")
                cmd = "M"
                self.prior.write_cmd(cmd)

                break

    def move_relative_z(self, value, delay=0):
        if value <= 0:
            cmd = "D, {z}".format(z=value)
        else:
            cmd = "U, {z}".format(z=value)

        while True:
            if self.prior.in_waiting > 0 and self._position_reached:
                self.prior.write_cmd(cmd)
                self._position_reached = False

                time.sleep(delay)  # wait for a bit for data to be sent
                self.reach_position_signal.emit()
                break

    def go_to_relative_position_z(self, z):
        thread_goto = threading.Thread(target=self.move_relative_z, args=(z, 0))
        thread_goto.start()

    def go_to_absolute_position(self, position: Position):
        thread_goto = threading.Thread(target=self.write_to_port, args=(position, 0))
        thread_goto.start()

    def go_to_relative_position_xy(self, x=0, y=0):
        print("gooooooo to")
        thread_goto = threading.Thread(target=self.write_to_relative, args=(x, y, 0))
        thread_goto.start()

    def write_to_port(self, position: Position, delay=2):
        x = position.x
        y = position.y
        z = position.z

        while True:
            if self.prior.in_waiting > 0 and self._position_reached:
                # # print("set position")
                if z is not None:
                    cmd = "G, {x}, {y}, {z}".format(x=x, y=y, z=z)
                else:
                    cmd = "G, {x}, {y}".format(x=x, y=y)
                self.prior.write_cmd(cmd)
                self._position_reached = False

                time.sleep(delay)  # wait for a bit for data to be sent
                self.reach_position_signal.emit()
                break

    def write_to_relative(self, x, y, delay=2):
        while True:
            if self.prior.in_waiting > 0 and self._position_reached:
                # # print("set position")
                cmd = "GR, {x}, {y}".format(x=x, y=y)
                self.prior.write_cmd(cmd)
                self._position_reached = False

                time.sleep(delay)  # wait for a bit for data to be sent
                self.reach_position_signal.emit()
                break

    def handle_data(self, data):
        print("---", data)

        if data == "R":
            self._position_reached = True
            print("position reached")

        else:
            try:
                x, y, z = [int(i) for i in data.split(",")]
                # print(f"{x}x, {y}y, {z}z")
                self.current_coords = (x, y, z)
            except Exception as e:
                print(str(e))

    @property
    def current_coords(self) -> Position:
        return self._current_coords

    @current_coords.setter
    def current_coords(self, value):
        self._current_coords = Position(*value)
        self.change_coord_signal.emit(self._current_coords)


class GlobalCommands(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = self.parent()
        self.microscope_handler = self.main_window.microscope_handler
        self.prior = self.microscope_handler.prior

        layout = QVBoxLayout()

        form_widget = QWidget()
        form_layout = QFormLayout()
        self.joystick_utilisation_cb = AnimatedToggle()
        self.joystick_utilisation_cb.setFixedSize(QSize(70, 40))

        form_layout.addRow(FormLabel("Joystick utilisation"), self.joystick_utilisation_cb)
        form_widget.setLayout(form_layout)

        self.emergency_btn = AnimatedOnHoverButton("EMERGENCY STOP")
        self.emergency_btn.font_color = QtGui.QColor(255, 0, 0)
        self.emergency_btn.background_color = QtGui.QColor(255, 255, 255)
        self.emergency_btn.setFixedWidth(300)

        define_position_widget = QWidget()
        define_position_layout = QHBoxLayout()
        self.back2home_btn = AnimatedOnHoverButton("HOME")
        self.back2home_btn.duration = 300
        self.back2home_btn.setFixedSize(QSize(130, 60))
        self.go_to_btn = AnimatedOnHoverButton("GO TO")
        self.go_to_btn.duration = 300

        self.go_to_btn.setFixedSize(QSize(130, 60))

        # fa5_icon = qta.icon('mdi.map-marker', color="white", color_active="black")

        self.map_btn = MapButton()
        self.map_btn.setObjectName("map")
        # "color-selected", QColor(10, 10, 10)
        self.map_btn.setIconSize(QtCore.QSize(32, 32))
        # self.map_btn = AnimatedOnHoverButton("MAP", duration=300)
        self.map_btn.setFixedSize(QSize(70, 60))

        define_position_layout.addWidget(self.go_to_btn)
        define_position_layout.addWidget(self.map_btn)
        define_position_layout.addWidget(self.back2home_btn)

        define_position_widget.setLayout(define_position_layout)


        # self.define_as_home_btn = QPushButton("Set as Home")

        layout.addWidget(TitleSectionLabel("General commands"), alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(form_widget, alignment=Qt.AlignCenter)

        # layout.addWidget(self.back2home_btn, alignment=Qt.AlignBottom | Qt.AlignCenter)
        # layout.addWidget(self.define_as_home_btn, alignment=Qt.AlignBottom | Qt.AlignCenter)
        # layout.addLayout(define_position_layout)
        layout.addWidget(define_position_widget)
        layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        layout.addWidget(self.emergency_btn, alignment=Qt.AlignBottom | Qt.AlignCenter)

        self.setLayout(layout)

        self.connect_actions()

        # Construct
        self.joystick_utilisation_cb.setChecked(self.prior.active_joystick)

    def connect_actions(self):
        self.emergency_btn.clicked.connect(self.prior.emergency_stop)
        self.joystick_utilisation_cb.stateChanged.connect(lambda value: setattr(self.prior, "active_joystick", value))
        # self.define_as_home_btn.clicked.connect(self.prior.set_position_as_home)
        self.back2home_btn.clicked.connect(self.microscope_handler.return2home)
        self.go_to_btn.clicked.connect(self.open_absolute_position_window)

        self.map_btn.clicked.connect(self.set_position_on_scene)

    def set_position_on_scene(self):
        self.parent().parent().parent().scene.clickable_status = True

    def open_absolute_position_window(self) -> None:
        # TODO
        dlg = GoToPosition(x_position=self.parent()._x, y_position=self.parent()._y, z_position=self.parent()._z,
                           parent=self)
        result = dlg.exec_()

        if result == 0:
            pass
        else:
            self.set_absolute_coords((dlg.x_pos_sb.value(), dlg.y_pos_sb.value(), dlg.z_pos_sb.value()))

    def set_absolute_coords(self, position: typing.Tuple) -> None:
        self.microscope_handler.go_to_absolute_position(Position(*position))


class PriorHandler(QWidget):
    def __init__(self, microscope_handler: MicroscopeHandler, parent=None):
        super().__init__(parent)
        self._x = None
        self._y = None
        self._z = None

        # self.prior = prior
        # self.microscope_handler = MicroscopeHandler(self.prior, parent=self)
        self.microscope_handler = microscope_handler

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()

        xy_layout = QVBoxLayout()
        self.xy_directions = DirectionalButtons(size_btn=50)
        # self.xy_directions.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        title_xy_label = TitleSectionLabel("XY Axis")
        xy_layout.addWidget(title_xy_label)
        xy_layout.addWidget(self.xy_directions, alignment=Qt.AlignLeft)
        control_layout.addLayout(xy_layout)

        z_layout = QVBoxLayout()
        self.z_directions = DirectionalButtons(size_btn=50, only_two=True)
        # self.xy_directions.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        title_z_label = TitleSectionLabel("Z Axis")
        z_layout.addWidget(title_z_label)
        z_layout.addWidget(self.z_directions, alignment=Qt.AlignLeft)
        control_layout.addLayout(z_layout)

        control_layout.addWidget(GlobalCommands(parent=self))

        layout.addLayout(control_layout)

        # xy_widget = XYHandler(parent=self, contracted_widget=True)
        # xy_widget.xy_directions.resize(QSize(200, 200))
        # # xy_widget.setFixedSize(QSize(400, 500))
        # z_widget = ZHandler(parent=self, contracted_widget=True)
        # z_widget.setFixedSize(QSize(400, 500))

        self.display_values = DisplayCurrentValues()
        self.display_values.resize(200, 100)

        layout.addWidget(self.display_values)

        self.setLayout(layout)

        self.connect_actions()

        # self.resize(QSize(500, 300))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.microscope_handler.close()

    def click_xy(self):
        step = 50
        direction = self.xy_directions.sender().objectName()
        if getattr(Directions, direction.upper()) == 1:
            relative_position = [-step, 0]
            # locked_command(self.prior.set_relative_position_steps(x=-step, y=0))
        elif getattr(Directions, direction.upper()) == 2:
            relative_position = [step, 0]
            # locked_command(self.prior.set_relative_position_steps(x=step, y=0))
        elif getattr(Directions, direction.upper()) == 3:
            relative_position = [0, step]
            # locked_command(self.prior.set_relative_position_steps(x=0, y=step))

        elif getattr(Directions, direction.upper()) == 4:
            relative_position = [0, -step]
            # locked_command(self.prior.set_relative_position_steps(x=0, y=-step))
        else:
            raise "The direction {} is not supported by this program".format(direction)

        self.go2relative_position(relative_position)

    def go2relative_position(self, position):
        self.microscope_handler.go_to_relative_position_xy(x=position[0], y=position[1])

    def connect_actions(self):
        # self.microscope_handler.change_coord_signal.connect(self.microscope_value_update)

        for i in [self.xy_directions.up_button, self.xy_directions.left_button, self.xy_directions.right_button,
                  self.xy_directions.down_button]:
            i.click.connect(self.click_xy)

        for j in [self.z_directions.up_button, self.z_directions.down_button]:
            j.click.connect(self.click_z)

    def click_z(self):
        step = 50
        direction = self.z_directions.sender().objectName()

        # UP
        if getattr(Directions, direction.upper()) == 3:
            relative_z = step
        # DOWN
        elif getattr(Directions, direction.upper()) == 4:
            relative_z = -step
        else:
            raise f"The direction {direction.upper()} is not taken in charge on the Z axis'"

        self.microscope_handler.go_to_relative_position_z(z=relative_z)

    def microscope_value_update(self, value):
        print("update")
        self.x = value.x
        self.y = value.y
        self.z = value.z

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = round(value)
        self.display_values.x = self._x

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = round(value)
        self.display_values.y = self._y

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = round(value)
        self.display_values.z = self._z


if __name__ == "__main__":
    # self.prior.write_cmd("COMP, 1")
    # self.prior.write_cmd("COMP")
    ser = PriorController(port="COM15", baudrate=9600, timeout=0.1)
    ser.acceleration = 10
    ser.speed = 10
    ser.write_cmd("COMP, 1")
    microscope_handler = MicroscopeHandler(ser)

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = PriorHandler(microscope_handler=microscope_handler)
    window.show()
    app.exec_()
