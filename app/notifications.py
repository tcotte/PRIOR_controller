import os
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import Qt


class Notification(QtWidgets.QMessageBox):
    def __init__(self, message: str):
        super().__init__()
        QApplication.restoreOverrideCursor()
        self.type = type
        self.message = message
        self.setText(self.message)

        self.setWindowIcon(QIcon(os.path.join(Path(__file__).parent.parent, "Logos/Visual_AI.ico")))


class Error(Notification):
    def __init__(self, message):
        super().__init__(message)
        self.setWindowTitle('Error')
        self.setIcon(QMessageBox.Critical)

        self.exec_()


class Success(Notification):
    def __init__(self, message):
        super().__init__(message)
        self.setWindowTitle('Success')
        check_pix = QPixmap(os.path.join(Path(__file__).parent.parent, "Logos/check-mark.png"))
        self.setIconPixmap(check_pix.scaled(30, 30, Qt.KeepAspectRatio))

        self.exec_()


class Warn(Notification):
    def __init__(self, message):
        super().__init__(message)
        self.setWindowTitle('Warning')
        self.setIcon(QMessageBox.Warning)

        self.exec_()
