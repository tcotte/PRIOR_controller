import sys

import qdarkstyle
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QApplication, QSpinBox, QHBoxLayout, QPushButton, \
    QAbstractSpinBox, QGroupBox


class GridsHandler(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        list_matrices = [f"{x} x {x}" for x in range(5, 30, 5)]

        for i in range(4):
            formGroupBox = QGroupBox(f"Grid {str(i + 1)}")
            sub_layout = QVBoxLayout()

            position_label = QLabel("Position")
            h_layout = QHBoxLayout()
            x_input = QSpinBox()
            y_input = QSpinBox()

            for input in [x_input, y_input]:
                input.setButtonSymbols(QAbstractSpinBox.NoButtons)

            h_layout.addWidget(x_input)
            h_layout.addWidget(QLabel("x(µm)"))
            h_layout.addWidget(y_input)
            h_layout.addWidget(QLabel("y(µm)"))
            h_layout.addWidget(QPushButton("Current position"))

            drop_down = QComboBox()
            drop_down.addItems(list_matrices)

            sub_layout.addWidget(position_label)
            sub_layout.addLayout(h_layout)
            sub_layout.addWidget(QLabel("Matrix"))
            sub_layout.addWidget(drop_down)

            formGroupBox.setLayout(sub_layout)

            layout.addWidget(formGroupBox)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)
    w = GridsHandler()
    # w = DockedAcquisition()
    w.show()
    app.exec_()
