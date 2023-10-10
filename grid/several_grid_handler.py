import sys
from typing import List, Tuple

import qdarkstyle
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QApplication, QSpinBox, QHBoxLayout, QPushButton, \
    QAbstractSpinBox, QGroupBox

from grid.share_serial import X_LIMIT, Y_LIMIT


class GridStartPosition(QGroupBox):
    def __init__(self, title: str, nb_position: int, parent=None):
        super().__init__()
        self.nb_position = nb_position
        self.setTitle(title + f" {str(nb_position)}")

        layout = QVBoxLayout()

        position_label = QLabel("Position")
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

        self.current_position_btn = QPushButton("Current position")
        self.current_position_btn.setObjectName(f"{str(nb_position)}")
        h_layout.addWidget(self.current_position_btn)



        layout.addWidget(position_label)
        layout.addLayout(h_layout)

        self.setLayout(layout)

        self.connect_actions()

    def connect_actions(self):
        self.current_position_btn.clicked.connect(self.on_click)

    def on_click(self):
        self.x_input.setValue(self.parent().parent().parent().x)
        self.y_input.setValue(self.parent().parent().parent().y)
        print("ok")

class GridsHandler(QWidget):
    grid_starting_points = pyqtSignal(object)

    def __init__(self, parent=None):
        # self.parent = parent
        super().__init__()
        layout = QVBoxLayout()

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

    def connect_actions(self):
        self.start_btn.clicked.connect(self.generate_grid)

    def generate_grid(self):
        print("gen")
        # bounding_rect = list(get_bounding_rec_grid(grid=self._grid, img_size=IMAGE_SIZE))
        # for i in range(4):
        list_grid = []
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, GridStartPosition):
                # print(widget.nb_position)
                # print(widget.x_input.value(), widget.y_input.value())
                if widget.x_input.value() != 0 or widget.y_input.value() != 0:
                    list_grid.append((widget.x_input.value(), widget.y_input.value(),
                                      self.transform_matrix_text2value(self.drop_down_matrix.currentText())))

        self.grid_starting_points.emit(list_grid)

    @staticmethod
    def transform_matrix_text2value(matrix_text: str) -> int:
        return int(matrix_text.split(" x ")[0])






if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)
    w = GridsHandler()
    # w = DockedAcquisition()
    w.show()
    app.exec_()
