import sys
import threading
import typing
from time import sleep

import qdarkstyle
import qtawesome as qta
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QSize, Qt, QObject, pyqtSignal, QThread, QRect
from PyQt5.QtGui import QFont, QKeyEvent, QFontMetrics
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLCDNumber, \
    QLabel, QFrame, QSizePolicy, QLayout, QSpacerItem, QFormLayout, QPushButton
from qtwidgets import AnimatedToggle
from superqt import QLabeledSlider

from app.go_to_windows import GoToXY, GoToZ
from app.ui_utils import QHLine, AnimatedOnHoverButton, TitleSectionLabel, FormLabel, LongClickButton
from main import PriorController

lock = threading.Lock()


#
# def locked_command(command) -> None:
#     lock.acquire(blocking=True)
#     command()
#     lock.release()


def locked_thread(function):
    def wrapper(*args, **kwargs):
        lock.acquire(blocking=True)
        function(*args, **kwargs)
        lock.release()

    return wrapper


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

        self.setMinimumSize(QSize(200, 200))

        self.setLayout(layout_button_holder)

        self.display()

        self.connect_actions()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        # create square size
        # if using only self.width() or self.height() without trimming the values, the window will endlessly resize itself
        print(self.size())
        size = QSize(min(int(self.width() / 1.5), int(self.height() / 1.5)),
                     min(int(self.width() / 1.5), int(self.height() / 1.5)))
        # buttons sizes
        btn_size = QSize(min(int(size.width() / 4), int(size.height() / 4)),
                         min(int(size.width() / 4), int(size.height() / 4)))
        self.button_holder.setFixedSize(size)
        self.resize_buttons(btn_size)

    def resize_buttons(self, size=None):
        print(size)
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
            """ % str(int(self.iconSize().width() / 2))
        )


class XYHandler(QWidget):
    def __init__(self, parent, contracted_widget: bool = False):
        super().__init__(parent)

        self.contracted_widget = contracted_widget

        # arrows
        # speed
        # acceleration
        self.main_window = parent
        self.prior = self.main_window.prior

        # self.position_window = GoTo(x_position=None, y_position=None)
        self.xy_directions = DirectionalButtons(size_btn=50)
        self.xy_directions.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        title_label = TitleSectionLabel("XY Axis")
        # font = QFont('MS UI Gothic', 30)
        # font.setBold(True)

        layout_btn = QHBoxLayout()
        hspacer = QSpacerItem(100, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.go_to_btn = AnimatedOnHoverButton("GO TO", duration=300)

        self.home_btn = AnimatedOnHoverButton("HOME", duration=300)

        layout_btn.addWidget(self.go_to_btn)
        layout_btn.addItem(hspacer)
        layout_btn.addWidget(self.home_btn)

        speed_label = FormLabel("Speed (mm/s)")
        acceleration_label = FormLabel("Acceleration")

        self.speed_slider = QLabeledSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(0, 8)
        self.acceleration_slider = QLabeledSlider(Qt.Orientation.Horizontal)

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.xy_directions)
        h_layout.addWidget(title_label, alignment=Qt.AlignTop | Qt.AlignRight)
        layout.addLayout(h_layout)
        layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(layout_btn)
        if not self.contracted_widget:
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
            layout.addWidget(QHLine())
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
            layout.addWidget(speed_label)
            layout.addWidget(self.speed_slider)
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
            layout.addWidget(acceleration_label)
            layout.addWidget(self.acceleration_slider)
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        self.connect_actions()
        self.display()

        # Construct
        self.acceleration_slider.setValue(self.main_window.prior.acceleration)
        self.speed_slider.setValue(self.convert_prior_speed_2_mms(self.main_window.prior.speed))

    def convert_prior_speed_2_mms(self, value_ps):
        ratio_ps_mms = 100 / 8
        return value_ps / ratio_ps_mms

    def convert_mms_2_prior_speed(self, value_mms):
        ratio_ps_mms = 100 / 8
        return value_mms * ratio_ps_mms

    def connect_actions(self) -> None:
        self.go_to_btn.clicked.connect(self.open_absolute_position_window)
        self.acceleration_slider.valueChanged.connect(self.change_acceleration)

        # self.speed_slider.valueChanged.connect(lambda value: locked_thread(function=setattr(self.prior, 'speed', value)))
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.home_btn.clicked.connect(self.go2home)

        for i in [self.xy_directions.up_button, self.xy_directions.left_button, self.xy_directions.right_button,
                  self.xy_directions.down_button]:
            i.click.connect(self.click_xy)

    def go2home(self):
        lock.acquire(blocking=True)
        self.prior.set_index_stage()
        lock.release()

    @locked_thread
    def change_speed(self, value):
        setattr(self.prior, 'speed', self.convert_mms_2_prior_speed(value))

    @locked_thread
    def change_acceleration(self, value):
        setattr(self.prior, 'acceleration', value)

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

    @locked_thread
    def go2relative_position(self, position):
        self.prior.set_relative_position_steps(*position)

    def open_absolute_position_window(self) -> None:
        dlg = GoToXY(x_position=self.main_window.x, y_position=self.main_window.y, parent=self)
        result = dlg.exec_()

        if result == 0:
            print("quit")
        else:
            self.set_absolute_coords((dlg.x_pos_sb.value(), dlg.y_pos_sb.value()))

    @locked_thread
    def set_absolute_coords(self, position: typing.Tuple) -> None:

        setattr(self.prior, 'coords', position)

    def display(self):
        print("display")


class ZHandler(QWidget):
    def __init__(self, parent, contracted_widget: bool = False):
        super().__init__(parent)
        self.contracted_widget = contracted_widget

        # arrows
        # speed
        # acceleration
        self.main_window = parent
        self.prior = self.main_window.prior

        title_label = TitleSectionLabel("Z Axis")

        self.z_direction = DirectionalButtons(size_btn=50, only_two=True)
        self.z_direction.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_btn = QHBoxLayout()
        hspacer = QSpacerItem(100, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.go_to_btn = AnimatedOnHoverButton("GO TO", duration=300)

        self.home_btn = AnimatedOnHoverButton("HOME", duration=300)

        layout_btn.addWidget(self.go_to_btn)
        layout_btn.addItem(hspacer)
        layout_btn.addWidget(self.home_btn)

        speed_label = FormLabel("Speed")
        acceleration_label = FormLabel("Acceleration")

        self.speed_slider = QLabeledSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(4, 100)
        self.acceleration_slider = QLabeledSlider(Qt.Orientation.Horizontal)
        self.acceleration_slider.setRange(4, 100)

        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.z_direction)
        h_layout.addWidget(title_label, alignment=Qt.AlignRight | Qt.AlignTop)
        layout.addLayout(h_layout)
        layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(layout_btn)
        if not self.contracted_widget:
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
            layout.addWidget(QHLine())
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
            layout.addWidget(speed_label)
            layout.addWidget(self.speed_slider)
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))
            layout.addWidget(acceleration_label)
            layout.addWidget(self.acceleration_slider)
            layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        self.connect_actions()
        self.display()

        # Construct
        # self.acceleration_slider.setValue(self.prior.z_controller.acceleration)
        # self.speed_slider.setValue(self.prior.z_controller.speed)

    def connect_actions(self) -> None:
        self.go_to_btn.clicked.connect(self.open_absolute_position_window)
        self.acceleration_slider.valueChanged.connect(lambda x: setattr(self.prior.z_controller, 'acceleration', x))
        self.speed_slider.valueChanged.connect(lambda x: setattr(self.prior.z_controller, 'speed', x))

        for i in [self.z_direction.up_button, self.z_direction.down_button]:
            i.click.connect(self.click_z)

    def click_z(self):
        step = 50
        direction = self.z_direction.sender().objectName()

        # UP
        if getattr(Directions, direction.upper()) == 3:
            self.prior.z_controller.move_relative_up(value=step)
        # DOWN
        elif getattr(Directions, direction.upper()) == 4:
            self.prior.z_controller.move_relative_down(value=step)
        else:
            raise f"The direction {direction.upper()} is not taken in charge on the Z axis'"

    def open_absolute_position_window(self) -> None:
        dlg = GoToZ(z_position=self.main_window.z, parent=self)

        result = dlg.exec_()

        if result == 0:
            print("quit")
        else:
            self.set_absolute_coords(dlg.z_pos_sb.value())

    @locked_thread
    def set_absolute_coords(self, position: typing.Tuple) -> None:

        setattr(self.prior.z_controller, 'z_position', position)

    def display(self):
        pass


class GeneralCommands(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.main_window = parent
        self.prior = self.main_window.prior

        layout = QVBoxLayout()

        form_widget = QWidget()
        form_layout = QFormLayout()
        self.joystick_utilisation_cb = AnimatedToggle()
        self.joystick_utilisation_cb.setFixedSize(QSize(70, 40))

        form_layout.addRow(FormLabel("Joystick utilisation"), self.joystick_utilisation_cb)
        form_widget.setLayout(form_layout)

        self.emergency_btn = AnimatedOnHoverButton("EMERGENCY STOP", font_color=QtGui.QColor(255, 0, 0),
                                                   background_color=QtGui.QColor(255, 255, 255))
        self.emergency_btn.setFixedWidth(300)

        self.back2home_btn = QPushButton("Back 2 Home")
        self.define_as_home_btn = QPushButton("Set as Home")

        layout.addWidget(TitleSectionLabel("General commands"), alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(form_widget, alignment=Qt.AlignCenter)

        layout.addWidget(self.back2home_btn, alignment=Qt.AlignBottom | Qt.AlignCenter)
        layout.addWidget(self.define_as_home_btn, alignment=Qt.AlignBottom | Qt.AlignCenter)

        layout.addWidget(self.emergency_btn, alignment=Qt.AlignBottom | Qt.AlignCenter)

        self.setLayout(layout)

        self.connect_actions()

        # Construct
        self.joystick_utilisation_cb.setChecked(self.prior.active_joystick)

    def connect_actions(self):
        self.emergency_btn.clicked.connect(self.main_window.prior.emergency_stop)
        self.joystick_utilisation_cb.stateChanged.connect(lambda value: setattr(self.prior, "active_joystick", value))
        self.define_as_home_btn.clicked.connect(self.prior.set_position_as_home)
        self.back2home_btn.clicked.connect(self.prior.return2home)


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
        # self.setMaximumHeight(150)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # print(self.size())
        super().resizeEvent(a0)
        self.x_dv.resize(self.size())
        self.y_dv.resize(self.size())
        self.z_dv.resize(self.size())


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
        self.value_qlcd.setFixedWidth(150)

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
            if self.prev_parent_size.width() == a0.width():
                resize_x = False
            if self.prev_parent_size.height() == a0.height():
                resize_y = False

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
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)

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


class RealTimeCoordWorker(QObject):
    coords = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__()
        # self.prior = parent.prior
        self.parent = parent
        self.delay_refresh = 0.5

    def run(self):
        """Long-running task."""
        while True:
            # print(self.parent.prior.busy)
            if not self.parent.prior.busy:
                sleep(self.delay_refresh)
                # print(self.prior.coords)
                lock.acquire(blocking=True)
                self.coords.emit(self.parent.prior.coords)
                lock.release()
        # self.finished.emit()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self._x = None
        self._y = None
        self._z = None

        self.prior = PriorController(port="COM15", baudrate=9600, timeout=0.05)

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        xy_widget = XYHandler(parent=self)
        xy_widget.setFixedSize(QSize(400, 500))
        z_widget = ZHandler(parent=self)
        z_widget.setFixedSize(QSize(400, 500))

        self.display_values = DisplayCurrentValues()

        space_width = 60
        control_layout.addItem(QSpacerItem(2 * space_width, space_width, QSizePolicy.Minimum, QSizePolicy.Expanding))
        control_layout.addWidget(xy_widget)
        control_layout.addItem(QSpacerItem(space_width, space_width, QSizePolicy.Minimum, QSizePolicy.Expanding))
        control_layout.addWidget(z_widget)
        control_layout.addItem(QSpacerItem(space_width, space_width, QSizePolicy.Minimum, QSizePolicy.Expanding))
        control_layout.addWidget(GeneralCommands(parent=self))
        control_layout.addItem(QSpacerItem(2 * space_width, space_width, QSizePolicy.Minimum, QSizePolicy.Expanding))

        layout.addLayout(control_layout)
        layout.addWidget(self.display_values)

        self.setLayout(layout)

        self.get_xy_values()

    def get_xy_values(self):
        self.thread = QThread()
        # Step 3: Create a worker object
        self.coord_worker = RealTimeCoordWorker(parent=self)
        # Step 4: Move worker to the thread
        self.coord_worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.coord_worker.run)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.coord_worker.coords.connect(self.report_xyz_values)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        # self.longRunningBtn.setEnabled(False)
        # self.thread.finished.connect(
        #     lambda: self.longRunningBtn.setEnabled(True)
        # )
        # self.thread.finished.connect(
        #     lambda: self.stepLabel.setText("Long-Running Step: 0")
        # )

    def report_xyz_values(self, coords: str) -> None:
        try:
            self.x, self.y, self.z = [int(x) for x in coords.split(",")]
        except:
            print("error with report_xyz_values function / coords value = {}".format(coords))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.prior.close()
        self.thread.quit()

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
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = DisplayCurrentValues()
    window.show()
    app.exec_()
