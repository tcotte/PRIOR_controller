import sys

import qdarkstyle
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QHBoxLayout


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        l = QHBoxLayout()
        self.pushButton = LongClickButton("a")
        l.addWidget(self.pushButton)
        self.setLayout(l)

        self.m_longClickTimer = QTimer(self)
        self.m_longClickTimer.setSingleShot(True)

        self.pushButton.click.connect(lambda : print("psuh"))
        # self.pushButton.pressed(self.get_nb_clicks)
        # self.pushButton.pressed.connect(lambda: self.m_longClickTimer.start(2000))
        # self.pushButton.released.connect(self.released)
        # self.m_longClickTimer.timeout.connect(self.longClickTimeout)

    # def released(self):
    #     if self.m_longClickTimer.isActive():
    #         print("clicked")
    #         self.m_longClickTimer.stop()
    #
    # def get_nb_clicks(self):
    #     while True:
    #         self.m_longClickTimer.start(2000)
    #
    #
    # def longClickTimeout(self):
    #     print("long clicked")

class LongClickButton(QPushButton):
    click = pyqtSignal()
    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.auto_repeat_interval = 100
        self.setAutoRepeat(True)
        # self.setAutoRepeatDelay(100)
        self.setAutoRepeatInterval(self.auto_repeat_interval)
        self.clicked.connect(self.handleClicked)
        self._state = 0

    def handleClicked(self):
        if self.isDown():
            if self._state == 0:
                self._state = 1
                self.setAutoRepeatInterval(self.auto_repeat_interval)
                self.click.emit()
            else:
                self.click.emit()
        elif self._state == 1:
            self._state = 0
            self.setAutoRepeatInterval(self.auto_repeat_interval)
        else:
            self.click.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    w = Widget()
    # window.z = 12000000
    w.show()
    app.exec_()