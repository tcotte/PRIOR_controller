import sys

import qdarkstyle
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QPushButton


class EmergencyButton(QWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.button = QPushButton("")
        self.button.setMinimumSize(100, 100)
        self.button.setStyleSheet(
            """
            QPushButton {
                border-image: url('../../Icons/emergency_stop.png');
                background-color: None;
            }
            
            QPushButton:hover {
                border-image: url('../../Icons/emergency_stop_hover.png');
            }
            
            QPushButton:pressed {
                border-image: url('../../Icons/emergency_stop_pressed.png');
            }
            """
        )

        layout = QHBoxLayout()
        layout.addWidget(self.button)

        self.setLayout(layout)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        self.button.setFixedSize(min(int(self.width()*0.7), int(self.height()*0.7)), min(int(self.width()*0.7), int(self.height()*0.7)))

    def connectActionOnClick(self, func):
        self.button.clicked.connect(func)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    w = EmergencyButton()
    w.show()
    app.exec_()
