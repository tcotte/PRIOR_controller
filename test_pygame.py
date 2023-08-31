# importing libraries
from typing import Final

import cv2
import numpy as np
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random
import sys

from grid.grid_movement import GridMovement, Course

APP_SIZE = (700, 500)
GRID = (750, 500)  # width, height -> 1 pixel equals 10 µm
IMAGE_SIZE = (11, 9)  # width, height -> camera image size
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
        self.statusbar.addPermanentWidget(self.open_camera_btn)
        self.statusbar.addPermanentWidget(self.position_label, 100)
        #self.statusbar.addWidget(self.open_camera_btn)

        # adding border to the status bar

        # calling showMessage method when signal received by board
        self.board.msg2statusbar[str].connect(lambda text: self.position_label.setText(text))

        # adding board as a central widget
        self.setCentralWidget(self.board)

        # setting title to the window
        self.setWindowTitle('Lens visualisation')

        # setting geometry to the window

        # self.board.minimumSize = QSize(APP_SIZE[0] + 50, APP_SIZE[1] + 50)
        self.board.setFixedSize(QSize(APP_SIZE[0] + 100, APP_SIZE[1] + 100))
        # self.board.setGeometry(50, 50, APP_SIZE[0] + 50, APP_SIZE[1] + 50)
        # self.setGeometry(50, 50, 50 + APP_SIZE[0] + self.statusbar.width(), 50+APP_SIZE[1] + self.statusbar.size().height()*3)

        # starting the board object
        self.board.start()

        self.connect_actions()
        # showing the main window
        self.show()

    def connect_actions(self) -> None:
        self.open_camera_btn.clicked.connect(self.open_camera_window)

    def open_camera_window(self) -> None:
        if self.win is None:
            self.win = CameraWindow()
            self.win.show()


# creating a board class
# that inherits QFrame


class Board(QFrame):
    # creating signal object
    msg2statusbar = pyqtSignal(str)

    # speed of the snake
    # timer countdown time
    SPEED = 100

    # block width and height
    WIDTHINBLOCKS = IMAGE_SIZE[0]
    HEIGHTINBLOCKS = IMAGE_SIZE[1]

    # constructor
    def __init__(self, parent):
        super(Board, self).__init__(parent)

        gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(round(0 / RATIO), 15000 / RATIO),
                          y_lim=(round(0 / RATIO), 15000 / RATIO))
        gm.course = Course().V_RIGHT
        gm.recover_x = 1
        gm.recover_y = 1
        self.grid = gm.get_grid(start_pt=(round(40000 / RATIO), round(40000 / RATIO)),
                                final_pt=(round(60000 / RATIO), round(60000 / RATIO)), percentage_overlap=(0.5, 1.1))
        # self.grid = gm.get_grid(start_pt=(round(85000/RATIO), 0), final_pt=(round(114000/RATIO), round(76000/RATIO)),
        #                        step=11)
        self.bounding_rec_limits = gm.get_bounding_rec_grid(grid=self.grid)
        self.bounding_rec_visu = gm.get_bounding_rec_visu()

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

        # growing is false
        self.grow_snake = False

        # board list
        self.board = []

        # direction
        self.direction = 1

        # setting focus
        self.setFocusPolicy(Qt.StrongFocus)

        # self.paint_lames()

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
        self.msg2statusbar.emit(str(tuple([x*RATIO for x in self.grid[0]])))

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
        previous_pts = self.grid[:self.counter]
        for pt in previous_pts:
            painter.fillRect(pt[0], pt[1], self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS, color)

    def draw_current_lens(self, painter, color: QColor = QColor(0x228B22)):
        try:
            x = self.grid[self.counter][0]
            y = self.grid[self.counter][1]
            painter.fillRect(x, y, self.WIDTHINBLOCKS, self.HEIGHTINBLOCKS, color)
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
            self.increment_counter()
            self.msg2statusbar.emit(str(tuple([x*RATIO for x in self.grid[self.counter]])))
            # update the window
            self.update()


# main method
if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())
