import sys

import qdarkstyle
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel


class Window(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.btn = QPushButton()
        label = QLabel("<span class='front' style='padding: 12px 42px; border-radius: 12px; "
                       "font-size: 1.25rem; background-color: rgb(188, 0, 138); color: white;'>Emergency Button</span>", self.btn)
        layout.addWidget(self.btn)
        self.setLayout(layout)

        self.display()

    def display(self):
        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgb(138, 0, 128);
                border-radius: 12px;
                border: none;
                padding: 0;
                cursor: pointer;
                outline-offset: 4px;
            }
            """
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = Window()
    # window.z = 12000000
    window.show()
    app.exec_()