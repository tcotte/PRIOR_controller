import datetime
import sys
import time
import typing

import cv2
import numpy as np
import qdarkstyle
import qimage2ndarray
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QRectF
from PyQt5.QtGui import QPixmap, QPen, QPainter, QBrush, QColor, QKeySequence
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QGraphicsPixmapItem, QGraphicsRectItem, \
    QWidget, QHBoxLayout, QDockWidget, QVBoxLayout, QPushButton, QMainWindow, QButtonGroup, QRadioButton, QLabel, \
    QSpinBox, QMessageBox, QShortcut, QProgressBar

from grid.display import Display
from grid.grid_movement import Course, GridMovement, get_bounding_rec_grid
from grid.verification_grid import draw_square_contours

IMAGE_SIZE: typing.Final = (4 * 85, 4 * 68)


class DockedForm(QWidget):
    new_grid_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        matrix_choice_label = QLabel("Matrix choice :")
        self.layout.addWidget(matrix_choice_label)

        self.matrix_group = QButtonGroup()
        for i in range(5, 30, 5):
            radio_button = QRadioButton(f"{str(i)} x {str(i)}")
            # self.matrix_group.setId(radio_button, i)
            self.matrix_group.addButton(radio_button, id=i)
            self.layout.addWidget(radio_button, alignment=Qt.AlignTop)

        overlap_layout = QHBoxLayout()

        overlap_label = QLabel("Overlap (%) :")
        self.overlap_sp = QSpinBox()
        self.overlap_sp.setRange(10, 100)
        self.overlap_sp.setValue(50)

        overlap_layout.addWidget(overlap_label)
        overlap_layout.addWidget(self.overlap_sp)

        self.layout.addLayout(overlap_layout)

        self.validate_btn = QPushButton("Ok")
        self.layout.addWidget(self.validate_btn)
        self.setLayout(self.layout)

        self.connect_actions()
        self.display()

    def connect_actions(self):
        self.validate_btn.clicked.connect(self.set_new_grid)

    def display(self):
        self.setStyleSheet("QRadioButton { margin-left: 30px; }")
        # self.setStyleSheet("QSpinBox { margin-top: 50px; margin-bottom: 50px;}")

    def set_new_grid(self):
        if self.matrix_group.checkedId() != -1:
            self.new_grid_signal.emit({"matrix": self.matrix_group.checkedId(), "overlap": self.overlap_sp.value()})
        else:
            QMessageBox.warning(self, 'Warning', 'Please select one matrix before create the grid.')


class MainWindow(QMainWindow):
    generated_grid_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.win = Window(self)
        self.setCentralWidget(self.win)

        self._acquisition_status = False
        self._progression = 0

        self.docked = QDockWidget("Grid generation", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docked)
        self.grid_generator = DockedForm()
        self.docked.setWidget(self.grid_generator)

        acquisition_docked = QDockWidget("Acquisition", self)
        self.addDockWidget(Qt.RightDockWidgetArea, acquisition_docked)
        self.acquisition_docked = DockedAcquisition()
        acquisition_docked.setWidget(self.acquisition_docked)

        self.setWindowTitle("Grid")

        self.run_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)

        # helpToolBar = QToolBar("Help", self)
        # self.addToolBar(Qt.TopToolBarArea, helpToolBar)

        self.connect_actions()

    def connect_actions(self):
        self.grid_generator.new_grid_signal.connect(self.generate_grid)
        self.grid_generator.new_grid_signal.connect(
            lambda: setattr(self.acquisition_docked, "acquisition_possibility", True))
        self.acquisition_docked.acquisition_status_signal.connect(
            lambda state: setattr(self, "acquisition_status", state))
        # self.run_shortcut.activated.connect(self.run_lens_movement)

    @property
    def progression(self):
        return self._progression

    @progression.setter
    def progression(self, value):
        self._progression = value
        self.acquisition_docked.progression = self._progression

    @property
    def acquisition_status(self):
        return self._acquisition_status

    @acquisition_status.setter
    def acquisition_status(self, value):
        self._acquisition_status = value
        if value:
            self.run_lens_movement()

    def run_lens_movement(self):
        self.win.runLongTask()

    def generate_grid(self, dict_values):
        matrix, overlap = dict_values["matrix"], 100-dict_values["overlap"]
        width_grid = int(IMAGE_SIZE[0] * (1 + matrix * (overlap / 100)))
        length_grid = int(IMAGE_SIZE[1] * (1 + matrix * (overlap / 100)))

        gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(0, 80000), y_lim=(0, 80000))
        gm.course = Course().V_RIGHT
        grid = gm.get_grid(start_pt=(0, 0), final_pt=(width_grid, length_grid),
                           percentage_non_overlap=(overlap / 100, overlap / 100))
        self.generated_grid_signal.emit(grid)


class Window(QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.scene = QGraphicsScene()
        self.view = Display()
        self.view.setScene(self.scene)
        # self.view.setMinimumWidth(600)
        # self.view.setMinimumWidth(500)
        # self.draw_lens()

        # gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(0, 5000), y_lim=(0, 5000))
        # gm.course = Course().V_RIGHT
        #
        # overlap = 50
        # matrix = 5
        # width_grid = int(IMAGE_SIZE[0] * (1 + matrix * (overlap / 100)))
        # length_grid = int(IMAGE_SIZE[1] * (1 + matrix * (overlap / 100)))
        #
        # self.grid = gm.get_grid(start_pt=(0, 0), final_pt=(width_grid, length_grid),
        #                         percentage_overlap=(overlap / 100, overlap / 100))
        # bounding_rec = list(gm.get_bounding_rec_grid(self.grid))
        self.grid = None

        # self.draw_grid(bounding_rec)

        # self.move_rectangle()

        # self.scene.setSceneRect()
        self.view.setRenderHint(QPainter.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.view)

        self.setLayout(hbox)

        # self.runLongTask()
        self.connect_actions()

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, value):
        self._grid = value
        if self._grid is not None:
            bounding_rect = list(get_bounding_rec_grid(grid=self._grid, img_size=IMAGE_SIZE))
            self.draw_grid(bounding_rect)
            self.draw_lens()
            self.move_rectangle(counter=0)
            self.scene.setSceneRect(0, 0, bounding_rect[2], bounding_rect[3])
            self.fitView()
            self.scene.update()

    def connect_actions(self):
        if hasattr(self.parent, "generated_grid_signal"):
            self.parent.generated_grid_signal.connect(lambda value: setattr(self, "grid", value))

    def draw_grid(self, bounding_rect):
        bounding_rect[2] += IMAGE_SIZE[0]
        bounding_rect[3] += IMAGE_SIZE[1]
        print(bounding_rect)

        m = np.ones((bounding_rect[3] + 1, bounding_rect[2] + 1, 3), dtype=np.uint8) * 255

        for point in self.grid:
            sub_img = m[point[1]:point[1] + IMAGE_SIZE[1], point[0]:point[0] + IMAGE_SIZE[0]]
            white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 10

            alpha = 0.9
            res = cv2.addWeighted(sub_img, alpha, white_rect, 1 - alpha, 0)

            # Putting the image back to its position
            m[point[1]:point[1] + IMAGE_SIZE[1], point[0]:point[0] + IMAGE_SIZE[0]] = res

            m = draw_square_contours(IMAGE_SIZE, point, m, thickness=int(np.floor(np.sqrt(bounding_rect[2]) / 15)))

        image = m.astype(int)
        q_img = qimage2ndarray.array2qimage(image)
        item = QGraphicsPixmapItem(QPixmap.fromImage(q_img))

        self.replace_pixmap_in_scene(new_pixmap_item=item)

        # self.fitView()
        self.scene.update()

    def replace_pixmap_in_scene(self, new_pixmap_item):
        for item in self.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                self.scene.removeItem(item)
                del (item)

        self.scene.addItem(new_pixmap_item)

    def draw_lens(self):
        for item in self.scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.scene.removeItem(item)
                del (item)

        self.rect = GraphicsLensItem(QRectF(0, 0, IMAGE_SIZE[0], IMAGE_SIZE[1]), name="current")

        self.scene.addItem(self.rect)

    def fitView(self):
        rect = self.scene.sceneRect()
        print(rect)
        self.view.fitInView(rect, Qt.KeepAspectRatioByExpanding)

    def runLongTask(self):
        self.thread = QThread()
        self.worker = Worker(nb_steps=len(self.grid))
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.finished_acquisition)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.move_rectangle)
        self.thread.start()

    def finished_acquisition(self) -> None:
        self.parent.progression = 100

    def move_rectangle(self, counter: int):
        self.parent.progression = round((counter / len(self._grid) * 100))

        if counter != 0:
            new_rectangle = GraphicsLensItem(
                QRectF(self._grid[counter - 1][0], self._grid[counter - 1][1], IMAGE_SIZE[0], IMAGE_SIZE[1]), name="old")

            self.scene.addItem(new_rectangle)
        self.rect.setPos(self._grid[counter][0], self._grid[counter][1])
        self.scene.update()


class GraphicsLensItem(QGraphicsRectItem):
    def __init__(self, rect, name: str = "item", *args, **kwargs):
        super().__init__(rect, *args, **kwargs)
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        if self._name == "old":
            brush = QBrush(QColor(0, 128, 0, 30))
            self.setBrush(brush)

            # Define the pen (line)
            pen = QPen(Qt.transparent)
            pen.setWidth(1)
            self.setPen(pen)

        elif self._name == "current":
            brush = QBrush(QColor(128, 0, 0, 30))
            self.setBrush(brush)

            # Define the pen (line)
            pen = QPen(Qt.darkRed)
            pen.setWidth(5)
            self.setPen(pen)


class DockedAcquisition(QWidget):
    acquisition_status_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self._progression = 0
        self._acquisition_status = False
        self._acquisition_possibility = False

        self.start_acquisition_btn = QPushButton("Start")
        self.start_acquisition_btn.setEnabled(self._acquisition_possibility)

        h_layout = QHBoxLayout()
        self.hour_label = QLabel("---")
        h_layout.addWidget(QLabel("Start hour:"))
        h_layout.addWidget(self.hour_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")

        layout.addWidget(self.start_acquisition_btn)
        layout.addLayout(h_layout)
        layout.addWidget(self.progress_bar)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.setLayout(layout)

        self.connect_actions()
        self.display()

    @property
    def acquisition_possibility(self):
        return self._acquisition_possibility

    @acquisition_possibility.setter
    def acquisition_possibility(self, value):
        self._acquisition_possibility = value
        self.start_acquisition_btn.setEnabled(value)

    @property
    def progression(self):
        return self._progression

    @progression.setter
    def progression(self, value):
        self._progression = value
        self.progress_bar.setValue(self._progression)

    @property
    def acquisition_status(self) -> bool:
        return self._acquisition_status

    @acquisition_status.setter
    def acquisition_status(self, value: bool):
        self._acquisition_status = value
        if value:
            self.start_acquisition_btn.setText("Stop")
            self.hour_label.setText(self.get_current_hour())
        else:
            self.start_acquisition_btn.setText("Start")
            self.hour_label.setText("---")
        self.acquisition_status_signal.emit(value)

    @staticmethod
    def get_current_hour():
        datetime_now = datetime.datetime.now()
        return datetime_now.strftime("%H:%M:%S")

    def connect_actions(self):
        self.start_acquisition_btn.clicked.connect(lambda: setattr(self, "acquisition_status",
                                                                   not self._acquisition_status))

    def display(self):
        self.setStyleSheet("#ProgressBar { min-height: 18px; max-height: 18px; border-radius: 8px; }")


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, nb_steps: int = 0):
        super().__init__()
        self.nb_steps = nb_steps

    @property
    def nb_steps(self):
        return self._nb_steps

    @nb_steps.setter
    def nb_steps(self, value):
        self._nb_steps = value

    def run(self):
        """Long-running task."""
        for i in range(self._nb_steps):
            time.sleep(1)
            self.progress.emit(i)
        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)
    w = MainWindow()
    # w = DockedAcquisition()
    w.show()
    app.exec_()

    # for pt in grid:
    #     print("ok")
    #     rect.setPos(pt[0], pt[1])
    #     time.sleep(1)
