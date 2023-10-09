# importing libraries
import os
import sys
from typing import Final

import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from camera.idscamwindow import IDSCamWindow
from grid.grid_movement import GridMovement, Course
from main import PriorController

APP_SIZE = (700, 500)
GRID = (750, 500)  # width, height -> 1 pixel equals 10 µm
# GROSSISSEMENT = 40
IMAGE_SIZE = (4 * 85, 4 * 68)  # width, height -> camera image size
RATIO = 76 * 2  # 1 pixel equals to 250 µm
X_LIMIT = 288000  # microscope's X limit (in µm)
Y_LIMIT = 80000  # microscope's Y limit (in µm)

SPACE_BETWEEN_SLIDES: Final = 3300 / RATIO
SLIDE_WIDTH: Final = 26000 / RATIO
SLIDE_HEIGHT: Final = 76000 / RATIO


# creating game window
class CameraThread(QThread):
    image = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.capture = None

    def start_capture(self):
        self.capture = cv2.VideoCapture(0)

    def stop_capture(self):
        if self.capture:
            self.capture.release()
            self.capture = None

    def run(self):
        self.start_capture()
        while True:
            ret, frame = self.capture.read()
            if ret:
                self.image.emit(frame)

    def stop(self):
        self.stop_capture()
        super().stop()


class CameraWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.camera = CameraThread()
        self.camera.image.connect(self.update_image)
        self.camera.start()

    def update_image(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(image))

    def capture_photo(self):
        frame = self.camera.frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        filename, _ = QFileDialog.getSaveFileName(self, "Save Photo", "", "JPEG Image (*.jpg)")
        if filename:
            image.save(filename, "jpg")


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.win = None

        # creating a board object
        self.board = Board(self)

        # creating a status bar to show result
        self.statusbar = self.statusBar()
        self.position_label = QLabel()

        self.open_camera_btn = QPushButton("Camera")

        # self.camera_window = IDSCamWindow()
        # self.camera_window.show()
        # self.camera_window.change_white_balance(2)
        # self.camera_window.change_exp_time(16)

        # self.prior = PriorController(port="COM15", baudrate=9600, timeout=0.1)

        self.statusbar.addPermanentWidget(self.open_camera_btn)
        self.statusbar.addPermanentWidget(self.position_label, 100)
        # self.statusbar.addWidget(self.open_camera_btn)

        # adding border to the status bar

        # calling showMessage method when signal received by board
        self.board.msg2statusbar[str].connect(lambda text: self.position_label.setText(text))

        # adding board as a central widget
        self.setCentralWidget(self.board)

        # setting title to the window
        self.setWindowTitle('Lens visualisation')

        # setting geometry to the window

        self.board.setFixedSize(QSize(APP_SIZE[0] + 100, APP_SIZE[1] + 100))

        # starting the board object
        # self.board.start()

        self.connect_actions()
        # showing the main window
        self.show()

    def connect_actions(self) -> None:
        self.open_camera_btn.clicked.connect(self.open_camera_window)

    def open_camera_window(self) -> None:
        if self.win is None:
            self.win = IDSCamWindow()
            self.win.show()


# creating a board class
# that inherits QFrame


class Board(QFrame):
    # creating signal object
    msg2statusbar = pyqtSignal(str)

    # speed of the snake
    # timer countdown time
    SPEED = 1000

    # block width and height
    WIDTHINBLOCKS = IMAGE_SIZE[0] / RATIO
    HEIGHTINBLOCKS = IMAGE_SIZE[1] / RATIO

    # constructor
    def __init__(self, parent):
        super(Board, self).__init__(parent)

        self.current_folder = None
        self.sharpness_values = []
        # gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(round(0 / RATIO), 15000 / RATIO),
        #                   y_lim=(round(0 / RATIO), 15000 / RATIO))
        gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(0, 2000), y_lim=(0, 2000))
        gm.course = Course().V_RIGHT
        # gm.recover_x = 1
        # gm.recover_y = 1
        # self.grid = gm.get_grid(start_pt=(round(0 / RATIO), round(0 / RATIO)),
        #                         final_pt=(round(2e3 / RATIO), round(2e3 / RATIO)), percentage_overlap=(0.1, 0.2))
        self.grid = gm.get_grid(start_pt=(0, 0), final_pt=(2000, 2000), percentage_non_overlap=(0.5, 0.5))
        print(self.grid)

        self.bounding_rec_limits = [int(round(x / RATIO)) for x in gm.get_bounding_rec_grid(grid=self.grid)]
        print(self.bounding_rec_limits)
        self.bounding_rec_visu = [round(x / RATIO) for x in gm.get_bounding_rec_visu()]

        self.z_min = 0
        self.z_max = 300
        self.z_step = 5
        self.nb_z_steps = (self.z_max - self.z_min) / self.z_step
        # Avoid division by 0
        if self.nb_z_steps == 0:
            self.nb_z_steps = 1

        self.counter = 0

        # creating a timer
        self.timer = QBasicTimer()

        # snake
        self.current_lens = []
        self.snake = [[5, 10], [5, 11]]

        # current head x head
        self.current_x_head = self.snake[0][0]
        # current y head
        self.current_y_head = self.snake[0][1]

        # food list
        self.food = []

        # board list
        self.board = []

        # direction
        self.direction = 1

        # setting focus
        self.setFocusPolicy(Qt.StrongFocus)

        # self.paint_lames()

        # self.sc

    def paint_slides(self, painter: QPainter) -> None:
        """
        Paint slides on board
        :param painter: Qt painter
        """

        painter.setPen(QPen(Qt.gray, 1, Qt.DashDotDotLine))

        for i in range(4):
            rec = [(SLIDE_WIDTH * i + i * SPACE_BETWEEN_SLIDES, SLIDE_WIDTH * (i + 1) + i * SPACE_BETWEEN_SLIDES),
                   (0, SLIDE_HEIGHT)]  # (x0, x1), (y0, y1)
            rec = QRectF(QPointF(rec[0][0], rec[1][0]),
                         QPointF(rec[0][1], rec[1][1]))

            painter.fillRect(rec, QColor(0, 203, 203, 40))
            painter.drawRect(rec)

    # square width method
    def square_width(self):
        return self.contentsRect().width() / Board.WIDTHINBLOCKS

    # square height
    def square_height(self):
        return self.contentsRect().height() / Board.HEIGHTINBLOCKS

    def grid_width(self):
        return self.contentsRect().width() / self.x_lim

    def grid_height(self):
        return self.contentsRect().height() / self.y_lim

    # start method
    def start(self) -> None:
        """
        Init the timer
        """
        # msg for status bar
        # score = current len - 2
        self.msg2statusbar.emit(str(tuple([x for x in self.grid[0]])))
        self.parent().prior.coords = tuple([x for x in self.grid[0]])

        # self.msg2statusbar.emit(str(tuple([x * RATIO for x in self.grid[0]])))
        # self.parent().prior.coords = tuple([x * RATIO for x in self.grid[0]])

        # starting timer
        self.timer.start(Board.SPEED, self)

    # paint event
    def paintEvent(self, event):

        # creating painter object
        painter = QPainter(self)

        # getting rectangle
        rect = self.contentsRect()

        # board top
        boardtop = rect.bottom() - Board.HEIGHTINBLOCKS * self.square_height()

        self.paint_slides(painter)

        # drawing snake
        for pos in self.snake:
            self.draw_square(painter, rect.left() + pos[0] * self.square_width(),
                             boardtop + pos[1] * self.square_height())

        # drawing food
        for pos in self.food:
            self.draw_square(painter, rect.left() + pos[0] * self.square_width(),
                             boardtop + pos[1] * self.square_height())

        # self.draw_square(painter, self.counter, 0, color=QColor(240, 128, 128))
        self.draw_previous_lenses(painter)
        self.draw_current_lens(painter, color=QColor(240, 128, 128))

        self.draw_grid_contours(painter)

    def draw_previous_lenses(self, painter, color: QColor = QColor(0x228B22)):
        previous_pts = self.grid[:int(np.floor(self.counter / self.nb_z_steps))]
        for pt in previous_pts:
            painter.fillRect(pt[0] / RATIO, pt[1] / RATIO, self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS, color)

    def draw_current_lens(self, painter, color: QColor = QColor(0x228B22)):
        try:
            x, y = self.grid[int(np.floor(self.counter / self.nb_z_steps))]
            print(x, y)
            painter.fillRect(x / RATIO, y / RATIO, self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS, color)
        except IndexError:
            self.msg2statusbar.emit(str("Grid Finished"
                                        ))
            print("Grid finished")
            self.timer.stop()

    def draw_grid_contours(self, painter):
        painter.setPen(QPen(Qt.black, 2, Qt.DashDotLine))

        rec = QRectF(QPointF(self.bounding_rec_visu[0], self.bounding_rec_visu[1]), QPointF(self.bounding_rec_visu[2],
                                                                                            self.bounding_rec_visu[3]))
        painter.drawRect(rec)

    # drawing square
    def draw_square(self, painter, x, y, filled=True, color: QColor = QColor(0x228B22)):

        if filled:
            # painting rectangle
            painter.fillRect(x, y, self.square_width() - 2,
                             self.square_height() - 2, color)
        else:
            painter.setPen(QPen(Qt.black, 1, Qt.DashDotLine))
            rec = QRectF(10.0, 20.0, 200, 200)
            painter.drawRect(rec)
            # painter.fillRect(rect, QBrush(QColor(128, 128, 255, 128)));

    # key press event
    def keyPressEvent(self, event):

        # getting key pressed
        key = event.key()

        if key == Qt.Key_Q:
            QApplication.quit()

    def increment_counter(self):
        self.counter += 1

    # time event method
    def timerEvent(self, event):

        # checking timer id
        if event.timerId() == self.timer.timerId():
            if self.counter % self.nb_z_steps == 0:
                self.parent().prior.coords = tuple([x for x in self.grid[
                    int(np.floor(self.counter / self.nb_z_steps))]])
                self.current_folder = os.path.join("output_picture/grid x40",
                                                   str(self.parent().prior.x_position) + "_" + str(
                                                       self.parent().prior.y_position))
                if not os.path.exists(self.current_folder):
                    os.mkdir(self.current_folder)
                self.parent().prior.z_controller.z_position = 0


            # update the window
            else:
                self.parent().prior.z_controller.z_position = (self.counter * self.z_step) % (self.z_max - self.z_min)

            self.msg2statusbar.emit(str(self.parent().prior.coords))
            self.parent().camera_window.capture_jpg(
                picture_path=os.path.join(self.current_folder,
                                          str(self.parent().prior.z_controller.z_position) + ".jpg"))

            self.increment_counter()
            self.update()


# main method
if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())
