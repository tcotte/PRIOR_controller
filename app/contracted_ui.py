import sys
from typing import Union

import qdarkstyle
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, QThread
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QApplication

from app.ui import XYHandler, ZHandler, DisplayCurrentValues, GeneralCommands, RealTimeCoordWorker
from grid.share_serial import SerialSingleton
from main import PriorController


class PriorMovement(QWidget):
    def __init__(self, prior: Union[PriorController, None]):
        super().__init__()
        self._x = None
        self._y = None
        self._z = None

        self.prior = prior

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        xy_widget = XYHandler(parent=self, contracted_widget=True)
        # xy_widget.setFixedSize(QSize(400, 500))
        z_widget = ZHandler(parent=self, contracted_widget=True)
        # z_widget.setFixedSize(QSize(400, 500))

        self.display_values = DisplayCurrentValues()
        self.display_values.resize(300, 100)
        # self.display_values.setFixedSize(300, 100)

        space_width = 60
        control_layout.addItem(QSpacerItem(2 * space_width, space_width, QSizePolicy.Minimum, QSizePolicy.Expanding))
        control_layout.addWidget(xy_widget)
        control_layout.addItem(QSpacerItem(space_width, space_width, QSizePolicy.Minimum, QSizePolicy.Expanding))
        control_layout.addWidget(z_widget)
        control_layout.addItem(QSpacerItem(space_width, space_width, QSizePolicy.Minimum, QSizePolicy.Expanding))

        layout.addLayout(control_layout)
        layout.addWidget(self.display_values)

        self.setLayout(layout)

    #     self.get_xy_values()
    #
    # def get_xy_values(self):
    #     self.thread = QThread()
    #     # Step 3: Create a worker object
    #     self.coord_worker = RealTimeCoordWorker(parent=self)
    #     # Step 4: Move worker to the thread
    #     self.coord_worker.moveToThread(self.thread)
    #     # Step 5: Connect signals and slots
    #     self.thread.started.connect(self.coord_worker.run)
    #     # self.worker.finished.connect(self.thread.quit)
    #     # self.worker.finished.connect(self.worker.deleteLater)
    #     self.thread.finished.connect(self.thread.deleteLater)
    #     self.coord_worker.coords.connect(self.report_xyz_values)
    #     # Step 6: Start the thread
    #     self.thread.start()
    #
    #     # Final resets
    #     # self.longRunningBtn.setEnabled(False)
    #     # self.thread.finished.connect(
    #     #     lambda: self.longRunningBtn.setEnabled(True)
    #     # )
    #     # self.thread.finished.connect(
    #     #     lambda: self.stepLabel.setText("Long-Running Step: 0")
    #     # )
    #
    # def report_xyz_values(self, coords: str) -> None:
    #     try:
    #         self.x, self.y, self.z = [int(x) for x in coords.split(",")]
    #     except:
    #         print("error with report_xyz_values function / coords value = {}".format(coords))
    #
    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     self.prior.close()
    #     self.thread.quit()

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
    window = PriorMovement(prior = SerialSingleton().serial)
    # window.x = 5000
    # window.y = 5000
    # window.z = 5000
    window.show()
    app.exec_()
