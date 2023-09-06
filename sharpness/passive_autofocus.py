import os
import sys

import numpy as np
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from matplotlib import pyplot as plt

from camera.idscamwindow import IDSCamWindow, convertQImageToMat
from main import PriorController
from sharpness.local_extremas import plot_sharpness_depending_on_z
from sharpness.test_sharpness import variance_of_laplacian, variance_of_sobel

focal_length = 200000  # focal length of lens (µm)
s_min = 1 * focal_length
s_max = 1.1 * focal_length

delta = round((s_max - s_min) / 200)
n = round((s_max - s_min) / delta)

# LENS
h = 30e3  # maximum diamater (µm)
afov = 2 * np.arctan(h / 2 * focal_length)  # Angular Field of View (degrees)
d_fov = 0.63e3  # field of view (µm)
working_distance = d_fov / (2 * np.arctan(afov / 2))

z_min = 0
z_max = 500

sharpness_algorithm = 'sobel'

if __name__ == "__main__":
    class Window(QWidget):
        def __init__(self):
            super().__init__()

            self.list_z_positions = list(range(z_min, z_max, 5))
            self.list_sharpness_values = []

            self.counter = 0

            self.camera_window = IDSCamWindow()
            self.camera_window.change_white_balance(2)
            self.camera_window.change_exp_time(50)

            layout = QVBoxLayout()
            layout.addWidget(self.camera_window)
            self.setLayout(layout)

            self.timer = QBasicTimer()

            self.prior = PriorController(port="COM15", baudrate=9600, timeout=0.1)
            self.prior.z_controller.z_position = self.list_z_positions[0]

            self.folder_path = os.path.join(r"C:\Users\tristan_cotte\PycharmProjects\prior_controller\output_picture\test_z_x40",
                                            str(self.prior.x_position) + "_" + str(self.prior.y_position))
            os.mkdir(self.folder_path)

            self.timer.start(1000, self)

        def timerEvent(self, e) -> None:

            if self.counter < len(self.list_z_positions):
                self.prior.z_controller.z_position = self.list_z_positions[self.counter]
                self.camera_window.capture_png(
                    picture_path=os.path.join(self.folder_path, str(self.list_z_positions[self.counter]) + ".png"))
                q_img = self.camera_window.display.scene.get_image()
                np_img = convertQImageToMat(incoming_image=q_img)

                if sharpness_algorithm == 'sobel':
                    img_sharpness = variance_of_sobel(np_img)
                else:
                    img_sharpness = variance_of_laplacian(np_img)

                self.list_sharpness_values.append(img_sharpness)

            else:
                with open(os.path.join(self.folder_path, 'sobel_values.txt'), 'w+') as f:
                    for line in self.list_sharpness_values:
                        f.write(str(line))
                        f.write('\n')
                f.close()

                plot_sharpness_depending_on_z(sharpness_array=np.array(self.list_sharpness_values),
                                              z_positions=self.list_z_positions, order=3)
                self.timer.stop()

            self.counter += 1


    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = Window()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()
