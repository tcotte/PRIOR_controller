# importing libraries
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random
import sys

from grid.grid_movement import GridMovement, Course

APP_SIZE = (1200, 800)
GRID = (1500, 1000)  # width, height -> 1 pixel equals 10 µm
IMAGE_SIZE = (10, 10)  # width, height -> camera image size
RATIO = 250  # 1 pixel equals to 250 µm
X_LIMIT = 288000  # microscope's X limit (in µm)
Y_LIMIT = 80000  # microscope's Y limit (in µm)


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
        self.open_camera_btn = QPushButton("Camera")
        self.statusbar.addWidget(self.open_camera_btn)

        # adding border to the status bar

        # calling showMessage method when signal received by board
        self.board.msg2statusbar[str].connect(self.statusbar.showMessage)

        # adding board as a central widget
        self.setCentralWidget(self.board)

        # setting title to the window
        self.setWindowTitle('Snake game')

        # setting geometry to the window
        self.setGeometry(50, 50, 1050, 850)

        # starting the board object
        self.board.start()

        self.connect_actions()
        # showing the main window
        self.show()

    def connect_actions(self):
        self.open_camera_btn.clicked.connect(self.open_camera_window)

    def open_camera_window(self):
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
    SPEED = 1000

    # block width and height
    WIDTHINBLOCKS = IMAGE_SIZE[0]
    HEIGHTINBLOCKS = IMAGE_SIZE[1]

    # constructor
    def __init__(self, parent):
        super(Board, self).__init__(parent)

        x, y = 0, 0
        vel = 5
        step = 50
        movement = GridMovement(x, y, vel, x_lim=(0, round(X_LIMIT / RATIO)), y_lim=(0, round(Y_LIMIT / RATIO)),
                                ratio=RATIO)
        movement.course = Course().V_RIGHT
        movement.recover_x = 50

        self.grid = movement.get_grid(start_pt=(x, y), final_pt=(600, 250),
                                      step=step)
        self.bounding_rec = movement.get_bounding_rec_grid(grid=self.grid)

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

        # called drop food method
        self.drop_food()

        # setting focus
        self.setFocusPolicy(Qt.StrongFocus)

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
    def start(self):
        # msg for status bar
        # score = current len - 2
        self.msg2statusbar.emit(str(len(self.snake) - 2))

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
            x = pt[0]
            y = pt[1]
            painter.fillRect(x, y, self.square_width(), self.square_height(), color)

    def draw_current_lens(self, painter, color: QColor = QColor(0x228B22)):
        try:
            x = self.grid[self.counter][0]
            y = self.grid[self.counter][1]
            painter.fillRect(x, y, self.square_width(), self.square_height(), color)
        except IndexError:
            print("Grid finished")

    def draw_grid_contours(self, painter):
        painter.setPen(QPen(Qt.black, 1, Qt.DashDotLine))
        print(self.bounding_rec)
        rec = QRectF(self.bounding_rec[0], self.bounding_rec[1], self.bounding_rec[2] + self.square_width(),
                     self.bounding_rec[3] + self.square_height())
        painter.drawRect(rec)

    # drawing square
    def draw_square(self, painter, x, y, filled=True, color: QColor = QColor(0x228B22)):

        if filled:
            # painting rectangle
            painter.fillRect(x + 1, y + 1, self.square_width() - 2,
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

        # if left key pressed
        if key == Qt.Key_Left:
            # if direction is not right
            if self.direction != 2:
                # set direction to left
                self.direction = 1

        # if right key is pressed
        elif key == Qt.Key_Right:
            # if direction is not left
            if self.direction != 1:
                # set direction to right
                self.direction = 2

        # if down key is pressed
        elif key == Qt.Key_Down:
            # if direction is not up
            if self.direction != 4:
                # set direction to down
                self.direction = 3

        # if up key is pressed
        elif key == Qt.Key_Up:
            # if direction is not down
            if self.direction != 3:
                # set direction to up
                self.direction = 4

        elif key == Qt.Key_Q:
            QApplication.quit()

    # method to move the snake
    def move_snake(self):

        # if direction is left change its position
        if self.direction == 1:
            self.current_x_head, self.current_y_head = self.current_x_head - 1, self.current_y_head

            # if it goes beyond left wall
            if self.current_x_head:
                self.current_x_head = Board.WIDTHINBLOCKS - 1

        # if direction is right change its position
        if self.direction == 2:
            self.current_x_head, self.current_y_head = self.current_x_head + 1, self.current_y_head
            # if it goes beyond right wall
            if self.current_x_head == Board.WIDTHINBLOCKS:
                self.current_x_head = 0

        # if direction is down change its position
        if self.direction == 3:
            self.current_x_head, self.current_y_head = self.current_x_head, self.current_y_head + 1
            # if it goes beyond down wall
            if self.current_y_head == Board.HEIGHTINBLOCKS:
                self.current_y_head = 0

        # if direction is up change its position
        if self.direction == 4:
            self.current_x_head, self.current_y_head = self.current_x_head, self.current_y_head - 1
            # if it goes beyond up wall
            if self.current_y_head:
                self.current_y_head = Board.HEIGHTINBLOCKS

        # changing head position
        head = [self.current_x_head, self.current_y_head]
        # inset head in snake list
        self.snake.insert(0, head)

        # if snake grow is False
        if not self.grow_snake:
            # pop the last element
            self.snake.pop()

        else:
            # show msg in status bar
            self.msg2statusbar.emit(str(len(self.snake) - 2))
            # make grow_snake to false
            self.grow_snake = False

    def increment_counter(self):
        self.counter += 1

    # time event method
    def timerEvent(self, event):

        # checking timer id
        if event.timerId() == self.timer.timerId():
            self.increment_counter()
            print(str(self.counter))
            # update the window
            self.update()

    # method to check if snake collides itself
    def is_suicide(self):
        # traversing the snake
        for i in range(1, len(self.snake)):
            # if collision found
            if self.snake[i] == self.snake[0]:
                # show game ended msg in status bar
                self.msg2statusbar.emit(str("Game Ended"
                                            ))
                # making background color black
                self.setStyleSheet(
                    "background-color: black"
                )
                # stopping the timer
                self.timer.stop()
                # updating the window
                self.update()

    # method to check if the food cis collied
    def is_food_collision(self):

        # traversing the position of the food
        for pos in self.food:
            # if food position is similar of snake position
            if pos == self.snake[0]:
                # remove the food
                self.food.remove(pos)
                # call drop food method
                self.drop_food()
                # grow the snake
                self.grow_snake = True

    # method to drop food on screen
    def drop_food(self):
        # creating random co-ordinates
        x = random.randint(3, 58)
        y = random.randint(3, 38)

        # traversing if snake position is not equal to the
        # food position so that food do not drop on snake
        for pos in self.snake:
            # if position matches
            if pos == [x, y]:
                # call drop food method again
                self.drop_food()

        # append food location
        self.food.append([x, y])


# main method
if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())
