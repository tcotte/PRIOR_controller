import sys
from datetime import datetime
from typing import Final, Union

import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from app.ui_utils import QHLine, CustomDockWidget
from app.utils.UI.GraphicItems.arrow import Arrow
from app.utils.UI.GraphicItems.clickable_graphics_scene import ClickableGraphicsScene
from app.utils.UI.GraphicItems.cross import CrossItem
from app.utils.position import Position
from automatic_prior_detector import PriorSearcher
from camera.idscamwindow import IDSCamWindow
from grid.display import Display
from grid.grid_movement import GridMovement, Course, get_bounding_rec_grid
from grid.grid_verif_qt import GridVerification
from grid.several_grid_handler import GridsHandler, GridDefinition, transform_matrix_text2value
from grid.share_serial import Y_LIMIT, X_LIMIT
from main import PriorController
from test_prior_read_write import PriorHandler, MicroscopeHandler

SPACE_BETWEEN_SLIDES: Final = 3300
SLIDE_WIDTH: Final = 26000
SLIDE_HEIGHT: Final = 76000

OVERLAP = 60
IMAGE_SIZE = (210, 175)


class myWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.acquisition_window = None
        self._acquisition_status = False
        self._matrix_length = None
        self.grids = None
        self._x = None
        self._y = None

        self.graphics_view = Display()

        self.scene = ClickableGraphicsScene()
        self.scene.setSceneRect(-10000, -5000, 135000, Y_LIMIT + 10000)
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setBackgroundBrush(Qt.white)

        self.setCentralWidget(self.graphics_view)

        self.display()

        self.fit_view()
        self.scene.update()

        docked = CustomDockWidget("Grids setup")
        self.grids_setup = GridsHandler(parent=self)
        # self.dockedWidget.setParent(self)
        docked.setWidget(self.grids_setup)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, docked)

        ps = PriorSearcher(baudrate_list=[9600])
        self.prior = PriorController(port=ps.port, baudrate=9600, timeout=0.1)

        docked = CustomDockWidget("Grid viewer")
        self.grid_verification = GridVerification()
        # self.dockedWidget.setParent(self)
        docked.setWidget(self.grid_verification)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, docked)

        docked = CustomDockWidget("Camera display")
        self.ids_cam_window = IDSCamWindow()
        # self.dockedWidget.setParent(self)
        docked.setWidget(self.ids_cam_window)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, docked)

        self.hide_show_axis_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)

        self.timer = QBasicTimer()
        self.positions_counter = 0

        self.connect_actions()

        # Constructor
        self.matrix_length = transform_matrix_text2value(self.grids_setup.drop_down_matrix.currentText())

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.scene.clickable_status = False

    @property
    def acquisition_status(self):
        return self._acquisition_status

    @acquisition_status.setter
    def acquisition_status(self, value):
        self._acquisition_status = value
        if self._acquisition_status:
            self.timer.start(1000, self)

            self.show_acquisition_window()

        else:
            self.grids_setup.on_acquisition = value

    def show_acquisition_window(self):
        self.acquisition_window = StartAcquisitionMessageBox(nb_grids=self.get_nb_defined_grids())
        self.acquisition_window.exec_()

        self.acquisition_status = False

    def timerEvent(self, event):

        # checking timer id
        if event.timerId() == self.timer.timerId():
            print("timer event")
            points = self.get_grid_points(self.grids[0])
            new_coord = points[self.positions_counter]
            self.prior.coords = new_coord
            self.positions_counter += 1

    def get_grid_points(self, grid):
        matrix, overlap = grid.matrix_length, 100 - OVERLAP
        width_grid = int(IMAGE_SIZE[0] * (1 + matrix * (overlap / 100)))
        length_grid = int(IMAGE_SIZE[1] * (1 + matrix * (overlap / 100)))

        gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(0, X_LIMIT), y_lim=(0, Y_LIMIT))
        gm.course = Course().V_RIGHT
        grid = gm.get_grid(start_pt=grid.start_position, final_pt=(width_grid, length_grid),
                           percentage_non_overlap=(overlap / 100, overlap / 100))
        return grid

    def get_nb_defined_grids(self) -> int:
        return len(list(filter(lambda x: x is not None, self.grids)))

    @property
    def matrix_length(self):
        return self._matrix_length

    @matrix_length.setter
    def matrix_length(self, value):
        self._matrix_length = value
        self.grid_verification.grid = self.get_grid_points(grid_definition=GridDefinition(
            start_position=(0, 0), matrix_definition=value))

    @staticmethod
    def get_grid_points(grid_definition: GridDefinition):
        start_pt_x = grid_definition.start_position[0]
        start_pt_y = grid_definition.start_position[1]
        matrix = grid_definition.matrix_length
        width_grid = round(IMAGE_SIZE[0] * (1 + matrix * (OVERLAP / 100)))
        length_grid = round(IMAGE_SIZE[1] * (1 + matrix * (OVERLAP / 100)))

        gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(0, X_LIMIT), y_lim=(0, Y_LIMIT))
        gm.course = Course().V_RIGHT
        grid_points = gm.get_grid(start_pt=(start_pt_x, start_pt_y),
                                  final_pt=(start_pt_x + width_grid, start_pt_y + length_grid),
                                  percentage_non_overlap=(OVERLAP / 100, OVERLAP / 100))
        return grid_points

    def connect_actions(self):
        self.grids_setup.grids_starting_points_signal.connect(self.generate_grids)
        self.hide_show_axis_shortcut.activated.connect(self.hide_show_axis)
        self.grids_setup.change_matrix_signal.connect(lambda value: setattr(self, "matrix_length", value))
        self.grids_setup.acquisition_status_change_signal.connect(
            lambda value: setattr(self, "acquisition_status", value))
        self.scene.position_clicked_signal.connect(self.distribute_clicked_position)

    def distribute_clicked_position(self, position: Position, object_name: str) -> None:
        if object_name.startswith("grid_"):
            grid_handler = self.grids_setup.layout().itemAt(int(object_name[-1])).widget()
            grid_handler.x_input.setValue(round(position.x))
            grid_handler.y_input.setValue(round(position.y))

        elif object_name == "map":
            self.microscope_handler.go_to_absolute_position(position)

        else:
            raise f"The object name {object_name} is not supported by the software."

    def hide_show_axis(self):
        filter_axis_item = filter(lambda item: isinstance(item, QGraphicsItemGroup) and item.data(0) == "axis",
                                  self.scene.items())

        list_axis_item = list(filter_axis_item)

        filter_legend_item = filter(lambda item: isinstance(item, QGraphicsItemGroup) and
                                                 item.data(0) == "slides_legend", self.scene.items())

        if len(list_axis_item) > 0:
            axis_item = list_axis_item[0]
            legend_item = list(filter_legend_item)[0]
            visible_status = axis_item.isVisible()
            axis_item.setVisible(not visible_status)
            legend_item.setVisible(not visible_status)

    def generate_grids(self, grids):
        if self.grids is not None:
            for element in self.scene.items():
                if isinstance(element, QGraphicsRectItem):
                    if element.data(0) == "Bounding_Rect":
                        self.scene.removeItem(element)

        self.grids = grids

        for grid in grids:
            if grid is not None:
                grid_points = self.get_grid_points(grid_definition=grid)

                bounding_rect = list(get_bounding_rec_grid(grid=grid_points, img_size=IMAGE_SIZE))
                self.draw_bounding_rect_grid(bounding_rect)

    def draw_bounding_rect_grid(self, bounding_rect):
        print(bounding_rect)
        bounding_rect[2] += IMAGE_SIZE[0]
        bounding_rect[3] += IMAGE_SIZE[1]

        graphic_bounding_rect = QGraphicsRectItem(
            QRectF(QPointF(bounding_rect[0], bounding_rect[1]), QPointF(bounding_rect[2], bounding_rect[3])))
        q_pen = QPen(Qt.black, 250, Qt.DashDotLine)
        graphic_bounding_rect.setPen(q_pen)
        graphic_bounding_rect.setData(0, "Bounding_Rect")

        self.scene.addItem(graphic_bounding_rect)

    def display(self):
        self.draw_blades()
        self.draw_axis()
        self.draw_legend()

    def add_prior_cursor(self) -> None:
        self.prior_cursor = CrossItem(center_x_position=self._x, center_y_position=self._y)
        self.prior_cursor.color = QColor("#D86f12")
        self.prior_cursor.size = 2000
        self.prior_cursor.thickness = 300
        self.scene.addItem(self.prior_cursor)

    def closeEvent(self, *args, **kwargs):
        if self.microscope_handler is not None:
            self.microscope_handler.close()

    @property
    def prior(self) -> Union[None, PriorController]:
        return self._prior

    @prior.setter
    def prior(self, value):
        self._prior = value
        if isinstance(self._prior, PriorController):
            self.add_prior_cursor()

            docked = QDockWidget("Dockable")
            # self.prior.busy = True
            # self.prior.wait4available()
            self.initialize_prior()
            self.microscope_handler = MicroscopeHandler(self._prior)
            self.prior_movement = PriorHandler(microscope_handler=self.microscope_handler, parent=self)
            # self.dockedWidget.setParent(self)
            # self.prior.busy = False
            docked.setWidget(self.prior_movement)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, docked)

            self.microscope_handler.change_coord_signal.connect(self.update_positions)

    def update_positions(self, position: Position) -> None:
        self.x = position.x
        self.y = position.y
        self.z = position.z

    def initialize_prior(self):
        self._prior.acceleration = 10
        self._prior.speed = 10


    @property
    def x(self) -> Union[int, None]:
        return self._x

    @x.setter
    def x(self, value: Union[int, None]) -> None:
        self._x = round(value)
        self.prior_cursor.center_x_position = self._x
        self.prior_movement.x = self._x

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        self._y = round(value)
        self.prior_cursor.center_y_position = self._y
        self.prior_movement.y = self._y

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, value: int) -> None:
        self._z = round(value)
        self.prior_movement.z = self._z

    def draw_legend(self):
        axis_layer = QGraphicsItemGroup()
        axis_layer.setData(0, "slides_legend")

        for i in range(4):
            io = QGraphicsTextItem()
            io.setDefaultTextColor(QColor("#8C8A88"))
            q_font = QFont()
            q_font.setPixelSize(2000)
            io.setFont(q_font)
            io.setPlainText(f"SLIDE {str(i + 1)}")

            x_position = SLIDE_WIDTH * (i + 1 / 2) - io.boundingRect().width() / 2 + i * SPACE_BETWEEN_SLIDES
            io.setPos(x_position, 78000)

            axis_layer.addToGroup(io)

        self.scene.addItem(axis_layer)

    def draw_axis(self):
        axis_layer = QGraphicsItemGroup()
        axis_layer.setData(0, "axis")

        io = QGraphicsTextItem()
        io.setPos(-4000, -4000)
        q_font = QFont()
        q_font.setPixelSize(2000)
        io.setFont(q_font)
        io.setPlainText("(0, 0)")
        axis_layer.addToGroup(io)
        # self.scene.addItem(io)

        arrow_x = Arrow(source=QPointF(0, 0), destination=QPointF(120000, 0), length_width=200, arrow_width=1500,
                        arrow_height=2500)
        arrow_y = Arrow(source=QPointF(0, 0), destination=QPointF(0, Y_LIMIT + 3000), length_width=200,
                        arrow_width=1500,
                        arrow_height=2500)

        axis_layer.addToGroup(arrow_x)
        axis_layer.addToGroup(arrow_y)

        height_tick = 1000
        for i in range(4):
            x_position = SLIDE_WIDTH * (i + 1) + i * SPACE_BETWEEN_SLIDES
            x_line = QGraphicsLineItem(x_position, 0 - height_tick, x_position, 0 + height_tick)

            tick_pen = QPen(Qt.black)
            tick_pen.setCosmetic(True)
            tick_pen.setWidth(2)
            x_line.setPen(tick_pen)

            axis_layer.addToGroup(x_line)

            io = QGraphicsTextItem()
            io.setPos(x_position - 3000, -4000)
            q_font = QFont()
            q_font.setPixelSize(2000)
            io.setFont(q_font)
            io.setPlainText(f"{str(x_position)}")
            axis_layer.addToGroup(io)

        y_position = SLIDE_HEIGHT
        y_line = QGraphicsLineItem(-height_tick, SLIDE_HEIGHT, height_tick, SLIDE_HEIGHT)
        y_line.setPen(tick_pen)
        axis_layer.addToGroup(y_line)
        # self.scene.addItem(y_line)

        size_font = 2000
        io = QGraphicsTextItem()
        io.setPos(-8000, round(y_position - size_font / 2))
        q_font = QFont()
        q_font.setPixelSize(size_font)
        io.setFont(q_font)
        io.setPlainText(f"{str(y_position)}")
        axis_layer.addToGroup(io)
        # self.scene.addItem(io)

        self.scene.addItem(axis_layer)

    def draw_blades(self):
        for i in range(4):
            rec = [(SLIDE_WIDTH * i + i * SPACE_BETWEEN_SLIDES, SLIDE_WIDTH * (i + 1) + i * SPACE_BETWEEN_SLIDES),
                   (0, SLIDE_HEIGHT)]  # (x0, x1), (y0, y1)
            rec = QRectF(QPointF(rec[0][0], rec[1][0]),
                         QPointF(rec[0][1], rec[1][1]))

            blade = QGraphicsRectItem(rec)
            brush = QBrush(QColor(0, 203, 203, 40))
            blade.setBrush(brush)
            pen = QPen(Qt.black)
            pen.setWidth(25)
            blade.setPen(pen)

            self.scene.addItem(blade)

    def fit_view(self):
        rect = self.scene.sceneRect()
        self.graphics_view.fitInView(rect, Qt.KeepAspectRatioByExpanding)

        # painter.fillRect(rec, QColor(0, 203, 203, 40))
        # painter.drawRect(rec)


class StartAcquisitionMessageBox(QDialog):
    acquisition_status_signal = pyqtSignal(bool)

    def __init__(self, nb_grids: int):
        super().__init__()
        layout = QVBoxLayout()

        self._nb_grids = nb_grids
        self._nb_completed_grids = 0
        self._progression = 0
        self._acquisition_status = False
        self._acquisition_possibility = False

        self.abort_btn = QPushButton("Abort")
        self.abort_btn.setFixedSize(QSize(50, 22))

        h_layout = QHBoxLayout()
        self.hour_label = QLabel("---")
        h_layout.addWidget(QLabel("Start hour:"))
        h_layout.addWidget(self.hour_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")

        layout.addLayout(h_layout)
        layout.addItem(QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(QLabel(f"{self._nb_completed_grids} / {self._nb_grids}"))

        layout.addLayout(progress_layout)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout.addItem(QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        layout.addWidget(QHLine())
        layout.addItem(QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        layout.addWidget(self.abort_btn, alignment=QtCore.Qt.AlignRight)

        self.setLayout(layout)

        self.connect_actions()
        self.display()

        # Constructor
        self.acquisition_status = True

    @property
    def acquisition_possibility(self):
        return self._acquisition_possibility

    @acquisition_possibility.setter
    def acquisition_possibility(self, value):
        self._acquisition_possibility = value

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
            self.hour_label.setText(self.get_current_hour())
        else:
            self.hour_label.setText("---")
        self.acquisition_status_signal.emit(value)

    @staticmethod
    def get_current_hour():
        datetime_now = datetime.now()
        return datetime_now.strftime("%H:%M:%S")

    def connect_actions(self):
        self.abort_btn.clicked.connect(self.show_close_confirmation_box)
        # self.start_acquisition_btn.clicked.connect(lambda: setattr(self, "acquisition_status",
        #                                                            not self._acquisition_status))

    def show_close_confirmation_box(self):
        confirmation_close_box = QMessageBox()
        confirmation_close_box.setIcon(QMessageBox.Warning)
        confirmation_close_box.setText("Are you sure you want to stop this acquisition ?")
        confirmation_close_box.setWindowTitle("Stop acquisition confirmation")
        confirmation_close_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returned_value = confirmation_close_box.exec()
        if returned_value == QMessageBox.Ok:
            confirmation_close_box.close()
            self.close()
        else:
            confirmation_close_box.close()

    def display(self):
        self.setStyleSheet("#ProgressBar { min-height: 18px; max-height: 18px; border-radius: 8px; }")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    # window = StartAcquisitionMessageBox(nb_grids=1)
    window = myWindow()
    window.showMaximized()
    # window.prior = SerialSingleton().serial
    # window.x = 5000
    # window.y = 5000
    # window.z = 5000
    window.show()
    app.exec_()
