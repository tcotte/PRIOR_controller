import os
import sys
import time

import cv2
from PyQt5.QtCore import QTimer, QBasicTimer
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout

from camera.idscamwindow import IDSCamWindow, convertQImageToMat
from main import PriorController
from sharpness.test_sharpness import variance_of_laplacian


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.list_z_positions = list(range(500, 1500, 10))
        self.folder_path = r"C:\Users\tristan_cotte\PycharmProjects\prior_controller\output_picture\test_z"
        self.counter = 0

        self.camera_window = IDSCamWindow()
        self.camera_window.change_white_balance(2)
        self.camera_window.change_exp_time(9)

        layout = QVBoxLayout()
        layout.addWidget(self.camera_window)
        self.setLayout(layout)

        self.timer = QBasicTimer()

        self.prior = PriorController(port="COM15", baudrate=9600, timeout=0.1)
        self.prior.z_controller.z_position = self.list_z_positions[0]

        self.timer.start(1000, self)

    def timerEvent(self, e) -> None:
        self.counter += 1
        if self.counter < len(self.list_z_positions):
            self.prior.z_controller.z_position = self.list_z_positions[self.counter]
            # self.camera_window.capture_photo(
            #     picture_path=os.path.join(self.folder_path, str(self.list_z_positions[self.counter]) + ".png"))
            q_img = self.camera_window.display.scene.get_image()
            np_img = convertQImageToMat(incoming_image=q_img)
            print(variance_of_laplacian(np_img))
            cv2.imwrite(os.path.join(self.folder_path, str(self.list_z_positions[self.counter]) + ".png"), np_img)
        else:
            self.timer.stop()

    #
    # def take_pictures(self):
    #
    #         self.prior.z_controller.z_position = i
            # time.sleep(1)
            # self.camera_window.capture_photo(picture_path=os.path.join(folder_path, str(i) + ".png"))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = Window()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()
