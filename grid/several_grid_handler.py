import sys
from typing import Final, Tuple, Union, List

import qdarkstyle
import qtawesome as qta
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QApplication, QSpinBox, QHBoxLayout, QPushButton, \
    QAbstractSpinBox, QGroupBox, QMessageBox, QWidgetItem, QLayout

from app.LogoSGS import Logo
from grid.share_serial import X_LIMIT, Y_LIMIT

SPACE_BETWEEN_SLIDES: Final = 3300
SLIDE_WIDTH: Final = 26000
SLIDE_HEIGHT: Final = 76000


def transform_matrix_text2value(matrix_text: str) -> int:
    return int(matrix_text.split(" x ")[0])


class GridDefinition(object):
    def __init__(self, start_position: Tuple[int, int], matrix_definition: Union[str, int]):
        self.start_position = start_position

        self.matrix_length = matrix_definition

    @property
    def matrix_length(self) -> int:
        return self._matrix_length

    @matrix_length.setter
    def matrix_length(self, value):
        if isinstance(value, str):
            self._matrix_length = transform_matrix_text2value(value)
        else:
            self._matrix_length = value


class ValidPushButton(QPushButton):
    def __init__(self):
        super().__init__()

        self._hovered = False
        self._validate = False

        # valid_icon = qta.icon("fa5s.check", color='green')
        # self.setIcon(valid_icon)

    @property
    def validate(self):
        return self._validate

    @validate.setter
    def validate(self, value):
        self._validate = value
        self.setEnabled(not value)
        valid_icon = qta.icon("fa5s.check", color='green')
        self.setIcon(valid_icon)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        if self._validate:
            self.setStyleSheet("border: 1px solid gray;")
        else:
            if not self._hovered:
                self.setStyleSheet(
                    "background-color: rgba(255, 255, 255, 0); border: 1px solid green; ")
            else:
                self.setStyleSheet(
                    "border: 1px solid white; ")
        super(ValidPushButton, self).paintEvent(a0)

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        if not self._validate:
            self._hovered = True
            # valid_icon = qta.icon("fa5s.check", color='white')
            # self.setIcon(valid_icon)
            self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(a0)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        if not self._validate:
            # self._hovered = False
            # valid_icon = qta.icon("fa5s.check", color='green')
            # self.setIcon(valid_icon)
            self.unsetCursor()
            self.restore_default_style()
        super().leaveEvent(a0)

    def restore_default_style(self) -> None:
        # valid_icon = qta.icon("fa5s.check", color='green')
        # self.setIcon(valid_icon)
        self.setIcon(QIcon())
        self._hovered = False


class GridStartPosition(QGroupBox):
    start_position_grid_signal = pyqtSignal(object)

    def __init__(self, title: str, nb_position: int, parent=None):
        super().__init__(parent)
        self.nb_position = nb_position
        self.setTitle(title + f" {str(nb_position)}")

        self._x_slide_range = range(
            SLIDE_WIDTH * (self.nb_position - 1) + (self.nb_position - 1) * SPACE_BETWEEN_SLIDES,
            SLIDE_WIDTH * self.nb_position + (self.nb_position - 1) * SPACE_BETWEEN_SLIDES)
        self._y_slide_range = range(0, Y_LIMIT)

        layout = QVBoxLayout()

        position_label = QLabel("Start position")
        h_layout = QHBoxLayout()
        self.x_input = QSpinBox()
        self.x_input.setObjectName(f"{str(nb_position)}")
        self.x_input.setRange(-X_LIMIT, X_LIMIT)

        self.y_input = QSpinBox()
        self.y_input.setRange(-Y_LIMIT, Y_LIMIT)

        for input in [self.x_input, self.y_input]:
            input.setButtonSymbols(QAbstractSpinBox.NoButtons)

        h_layout.addWidget(self.x_input)
        h_layout.addWidget(QLabel("x(µm)"))
        h_layout.addWidget(self.y_input)
        h_layout.addWidget(QLabel("y(µm)"))

        current_position_icon = qta.icon('ph.crosshair', color='white')
        self.current_position_btn = QPushButton(current_position_icon, "")
        self.current_position_btn.setIconSize(QtCore.QSize(20, 20))
        self.current_position_btn.setFixedHeight(22)
        self.current_position_btn.setObjectName(f"{str(nb_position)}")
        self.current_position_btn.setToolTip("Set current microscope position as start position")

        map_icon = qta.icon('mdi.map-marker', color="white")
        self.map_position_btn = QPushButton(map_icon, "")
        self.map_position_btn.setIconSize(QtCore.QSize(20, 20))
        self.map_position_btn.setFixedHeight(22)
        self.map_position_btn.setObjectName(f"grid_{str(nb_position)}")
        self.map_position_btn.setToolTip("Click on the map and set the clicked position as start position")


        self.validation_btn = ValidPushButton()
        self.validation_btn.setFixedSize(QSize(22, 22))
        self.validation_btn.setToolTip("Validate the start position of the grid")

        h_layout.addWidget(self.current_position_btn)
        h_layout.addWidget(self.map_position_btn)
        h_layout.addWidget(self.validation_btn)


        layout.addWidget(position_label)
        layout.addLayout(h_layout)

        self.setLayout(layout)

        self.connect_actions()

        self.scene = self.parent().parent().scene

    def connect_actions(self):
        self.x_input.textChanged.connect(self.cancel_validation)
        self.y_input.textChanged.connect(self.cancel_validation)
        self.current_position_btn.clicked.connect(self.on_click)
        self.validation_btn.clicked.connect(self.valid_position)
        self.map_position_btn.clicked.connect(self.set_position_on_scene)

    def set_position_on_scene(self):
        self.scene.clickable_status = True

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.scene.clickable_status = False

    def valid_position(self):
        if self.x_input.value() in self._x_slide_range and self.y_input.value() in self._y_slide_range:
            self.start_position_grid_signal.emit((self.x_input.value(), self.y_input.value()))
            self.validation_btn.validate = True

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Error in grid start position")
            msg.setInformativeText("The grid start position has to lie on the correspondant slide !")
            msg.setWindowTitle("Warning")
            msg.exec_()

    def on_click(self):
        self.x_input.setValue(self.parent().parent().parent().x)
        self.y_input.setValue(self.parent().parent().parent().y)

    def cancel_validation(self, e):
        if self.validation_btn.validate:
            self.validation_btn.validate = False
            self.validation_btn.restore_default_style()
            self.start_position_grid_signal.emit((None, None))

    def setEnabled(self, a0: bool) -> None:
        if a0:
            self.validation_btn.validate = False
            self.validation_btn.restore_default_style()
        else:
            self.validation_btn.validate = True
        super(GridStartPosition, self).setEnabled(a0)


class GridsHandler(QWidget):
    grids_starting_points_signal = pyqtSignal(object)
    change_matrix_signal = pyqtSignal(int)
    acquisition_status_change_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        # self.parent = parent
        super().__init__(parent)
        self._on_acquisition = False

        layout = QVBoxLayout()
        logo = Logo()
        logo.setFixedSize(QSize(200, 100))
        layout.addWidget(logo, alignment=Qt.AlignCenter)

        for i in range(4):
            form_group_box = GridStartPosition(title="Grid", nb_position=i + 1, parent=self)
            # formGroupBox = QGroupBox(f"Grid {str(i + 1)}")

            layout.addWidget(form_group_box)

            # self.current_position_btn.clicked.connect(self.on_click)

        h_layout = QHBoxLayout()

        h_layout.addWidget(QLabel("Matrix"))
        self.drop_down_matrix = QComboBox()
        list_matrices = [f"{x} x {x}" for x in range(5, 200, 5)]
        self.drop_down_matrix.addItems(list_matrices)
        h_layout.addWidget(self.drop_down_matrix)

        layout.addLayout(h_layout)

        self.start_btn = QPushButton("Start")
        layout.addWidget(self.start_btn)

        self.setLayout(layout)

        self.connect_actions()

        # Constructor
        self.grids_starting_points = [None] * 4

    def connect_actions(self):
        self.drop_down_matrix.currentTextChanged.connect(self.change_matrix)

        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, GridStartPosition):
                widget.start_position_grid_signal.connect(self.generate_one_grid)

        self.start_btn.clicked.connect(lambda: setattr(self, "on_acquisition", True))

    @property
    def on_acquisition(self):
        return self._on_acquisition

    @on_acquisition.setter
    def on_acquisition(self, value):
        self._on_acquisition = value
        self.toggle_enable_lawhole_layout(layout=self.layout(), status=not value)
        if self._on_acquisition:
            self.acquisition_status_change_signal.emit(value)

    @staticmethod
    def toggle_enable_lawhole_layout(layout: QLayout, status: bool) -> None:
        for widget_index in range(layout.count()):
            element = layout.itemAt(widget_index)
            if isinstance(element, QWidgetItem):
                widget = element.widget()
                widget.setEnabled(status)
            elif isinstance(element, QLayout):
                layout = element.layout()
                for index in range(layout.count()):
                    layout.itemAt(index).widget().setEnabled(status)

    def generate_one_grid(self, value: Union[Tuple[int, int], None]):
        nb_grid = self.sender().nb_position
        if value != (None, None):
            self.grids_starting_points[nb_grid - 1] = GridDefinition(start_position=value,
                                                                     matrix_definition=self.drop_down_matrix.currentText())
        else:
            self.grids_starting_points[nb_grid - 1] = None

        self.refresh_possibility_start_acquisition()
        self.grids_starting_points_signal.emit(self._grids_starting_points)

    def change_matrix(self, value):
        self.change_matrix_signal.emit(transform_matrix_text2value(value))
        for grid in self.grids_starting_points:
            if grid is not None:
                grid.matrix_length = value
        self.grids_starting_points_signal.emit(self._grids_starting_points)

    @property
    def grids_starting_points(self):
        return self._grids_starting_points

    @grids_starting_points.setter
    def grids_starting_points(self, value: List[Union[None, GridDefinition]]):
        self._grids_starting_points = value
        self.grids_starting_points_signal.emit(self._grids_starting_points)

    def refresh_possibility_start_acquisition(self):
        if all(v is None for v in self._grids_starting_points):
            self.start_btn.setEnabled(False)
        else:
            self.start_btn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)
    w = GridsHandler()
    # w = QMainWindow()
    # layout = QHBoxLayout()
    # layout.addWidget(ValidPushButton())
    # w.setCentralWidget(ValidPushButton())
    # w = DockedAcquisition()
    w.show()
    app.exec_()
