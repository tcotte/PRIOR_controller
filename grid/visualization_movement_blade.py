import math
import sys
from typing import Final, Union

import qdarkstyle
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from app.contracted_ui import PriorMovement
from app.ui import RealTimeCoordWorker
from grid.display import Display
from grid.grid_movement import GridMovement, Course, get_bounding_rec_grid
from grid.several_grid_handler import GridsHandler
from grid.share_serial import SerialSingleton, Y_LIMIT, X_LIMIT
from main import PriorController

SPACE_BETWEEN_SLIDES: Final = 3300
SLIDE_WIDTH: Final = 26000
SLIDE_HEIGHT: Final = 76000

OVERLAP = 50
IMAGE_SIZE = (210, 175)


class Arrow(QGraphicsPathItem):
    #  draw an arrow like this
    #                           |\
    #                ___   _____| \
    #    length_width |   |        \  _____
    #                _|_  |_____   /    |
    #                           | /     | arrow_width
    #                           |/    __|__
    #
    #                           |<->|
    #                        arrow_height
    def __init__(self, source: QtCore.QPointF, destination: QtCore.QPointF, arrow_height, arrow_width, length_width,
                 *args, **kwargs):
        super(Arrow, self).__init__(*args, **kwargs)

        self._sourcePoint = source
        self._destinationPoint = destination

        self._arrow_height = arrow_height
        self._arrow_width = arrow_width
        self._length_width = length_width

    def boundingRect(self):
        x0 = self._sourcePoint.x()
        y0 = self._sourcePoint.y() - self._arrow_width
        x1 = self._destinationPoint.x()
        y1 = self._destinationPoint.y() + self._arrow_width
        return QtCore.QRectF(QPointF(x0, y0), QPointF(x1, y1))

    def arrowCalc(self, start_point=None, end_point=None):  # calculates the point where the arrow should be drawn

        try:
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self._sourcePoint

            if endPoint is None:
                endPoint = self._destinationPoint

            dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

            leng = math.sqrt(dx ** 2 + dy ** 2)
            normX, normY = dx / leng, dy / leng  # normalize

            # parallel vector (normX, normY)
            # perpendicular vector (perpX, perpY)
            perpX = -normY
            perpY = normX

            #           p2
            #           |\
            #    p4____p5 \
            #     |        \ endpoint
            #    p7____p6  /
            #           | /
            #           |/
            #          p3
            point2 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height + QtCore.QPointF(perpX,
                                                                                                   perpY) * self._arrow_width
            point3 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height - QtCore.QPointF(perpX,
                                                                                                   perpY) * self._arrow_width

            point4 = startPoint + QtCore.QPointF(perpX, perpY) * self._length_width
            point5 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height + QtCore.QPointF(perpX,
                                                                                                   perpY) * self._length_width
            point6 = endPoint + QtCore.QPointF(normX, normY) * self._arrow_height - QtCore.QPointF(perpX,
                                                                                                   perpY) * self._length_width
            point7 = startPoint - QtCore.QPointF(perpX, perpY) * self._length_width

            polygon = QPolygonF([point4, point5, point2, endPoint, point3, point6, point7])
            return polygon

        except (ZeroDivisionError, Exception):
            return None

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        # painter.setRenderHint(painter.Antialiasing)

        my_pen = QtGui.QPen()
        my_pen.setWidth(1)
        my_pen.setCosmetic(False)
        my_pen.setColor(QtGui.QColor(0, 0, 0, 100))
        painter.setPen(my_pen)

        painter.setBrush(QColor(0, 0, 0, 200))

        arrow_polygon = self.arrowCalc()
        if arrow_polygon is not None:
            # painter.drawPolyline(arrow_polygon)
            painter.drawPolygon(arrow_polygon)


class CrossItem(QGraphicsItem):

    def __init__(self, center_x_position: Union[int, None], center_y_position: Union[int, None]):
        super(CrossItem, self).__init__()
        if center_x_position is None:
            self._center_x_position = 0
        else:
            self._center_x_position = center_x_position

        if center_y_position is None:
            self._center_y_position = 0
        else:
            self._center_y_position = center_y_position

        self._size = 1
        self._color = QColor(Qt.black)
        self._thickness = 1

        self.setAcceptHoverEvents(False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = value

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, value: QColor) -> None:
        self._color = value

    @property
    def thickness(self) -> int:
        return self._thickness

    @thickness.setter
    def thickness(self, value: int) -> None:
        self._thickness = value

    def paint(self, painter, option, widget):
        pen = QPen(self._color)
        pen.setWidth(self._thickness)
        painter.setPen(pen)

        painter.drawLine(QPoint(round(self._center_x_position - self._size / 2), self._center_y_position),
                         QPoint(round(self._center_x_position + self._size / 2), self._center_y_position))
        painter.drawLine(QPoint(self._center_x_position, round(self._center_y_position - self._size / 2)),
                         QPoint(self._center_x_position, round(self._center_y_position + self._size / 2)))

    def boundingRect(self):
        print(QRectF(round(self._center_x_position - self._size / 2), round(self._center_y_position - self._size / 2),
                     self._size, self._size))
        return QRectF(round(self._center_x_position - self._size / 2), round(self._center_y_position - self._size / 2),
                      self._size, self._size)

    @property
    def center_x_position(self):
        return self._center_x_position

    @center_x_position.setter
    def center_x_position(self, value):
        print("x__" + str(value))
        self._center_x_position = value
        self.scene().update()
        # self.painter.update()

    @property
    def center_y_position(self):
        return self._center_y_position

    @center_y_position.setter
    def center_y_position(self, value):
        print("y__" + str(value))
        self._center_y_position = value
        self.scene().update()
        # self.painter.update()


class myWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.grids = None
        self._x = None
        self._y = None

        self.graphics_view = Display()

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-10000, -5000, 135000, Y_LIMIT + 10000)
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setBackgroundBrush(Qt.white)

        self.setCentralWidget(self.graphics_view)

        self.display()

        self.fit_view()
        self.scene.update()

        docked = QDockWidget("Dockable")
        self.grids_setup = GridsHandler(parent=self)
        # self.dockedWidget.setParent(self)
        docked.setWidget(self.grids_setup)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, docked)

        # self.prior = PriorController(port="COM15", baudrate=9600, timeout=0.1)
        self.hide_show_axis_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)

        self.connect_actions()

    def connect_actions(self):
        self.grids_setup.grid_starting_points.connect(self.generate_grids)
        self.hide_show_axis_shortcut.activated.connect(self.hide_show_axis)

    def hide_show_axis(self):
        filter_axis_item = filter(lambda item: isinstance(item, QGraphicsItemGroup) and item.data(0) == "axis",
                                  self.scene.items())
        list_axis_item = list(filter_axis_item)
        if len(list_axis_item) > 0:
            axis_item = list_axis_item[0]
            visible_status = axis_item.isVisible()
            axis_item.setVisible(not visible_status)

    def generate_grids(self, grids):
        if self.grids is not None:
            for element in self.scene.items():
                if isinstance(element, QGraphicsRectItem):
                    if element.data(0) == "Bounding_Rect":
                        self.scene.removeItem(element)

        self.grids = grids

        for grid in grids:
            start_pt_x = grid[0]
            start_pt_y = grid[1]
            matrix = grid[2]

            width_grid = int(IMAGE_SIZE[0] * (1 + matrix * (OVERLAP / 100)))
            length_grid = int(IMAGE_SIZE[1] * (1 + matrix * (OVERLAP / 100)))

            gm = GridMovement(x=0, y=0, img_size=IMAGE_SIZE, x_lim=(0, X_LIMIT), y_lim=(0, Y_LIMIT))
            gm.course = Course().V_RIGHT
            grid_points = gm.get_grid(start_pt=(start_pt_x, start_pt_y),
                                      final_pt=(start_pt_x + width_grid, start_pt_y + length_grid),
                                      percentage_non_overlap=(OVERLAP / 100, OVERLAP / 100))

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

    def add_prior_cursor(self) -> None:
        self.prior_cursor = CrossItem(center_x_position=self._x, center_y_position=self._y)
        self.prior_cursor.color = QColor(Qt.gray)
        self.prior_cursor.size = 2000
        self.prior_cursor.thickness = 300
        self.scene.addItem(self.prior_cursor)

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
            self.prior_movement = PriorMovement(self._prior)
            # self.dockedWidget.setParent(self)
            # self.prior.busy = False
            docked.setWidget(self.prior_movement)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, docked)

            self.get_xy_values()

    def get_xy_values(self):
        self.thread = QThread()
        # Step 3: Create a worker object
        self.coord_worker = RealTimeCoordWorker(parent=self)
        # Step 4: Move worker to the thread
        self.coord_worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.coord_worker.run)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.coord_worker.coords.connect(self.report_xyz_values)
        # Step 6: Start the thread
        self.thread.start()

    def report_xyz_values(self, coords: str) -> None:
        try:
            self.x, self.y, self.z = [int(x) for x in coords.split(",")]
        except:
            print("error with report_xyz_values function / coords value = {}".format(coords))

    @property
    def x(self) -> Union[int, None]:
        return self._x

    @x.setter
    def x(self, value: Union[int, None]) -> None:
        self._x = round(value)
        self.prior_cursor.center_x_position = self._x
        self.prior_movement.x = self._x
        # self.

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

        for i in range(4):
            height_tick = 1000
            x_position = SLIDE_WIDTH * (i + 1) + i * SPACE_BETWEEN_SLIDES
            x_line = QGraphicsLineItem(x_position, 0 - height_tick, x_position, 0 + height_tick)
            pen = QPen(Qt.black)
            pen.setWidth(200)
            x_line.setPen(pen)

            axis_layer.addToGroup(x_line)
            # self.scene.addItem(x_line)

            io = QGraphicsTextItem()
            io.setPos(x_position - 3000, -4000)
            q_font = QFont()
            q_font.setPixelSize(2000)
            io.setFont(q_font)
            io.setPlainText(f"{str(x_position)}")
            axis_layer.addToGroup(io)
            # self.scene.addItem(io)

        # for i in range(3):
        #     x_line = QGraphicsLineItem(SLIDE_WIDTH * (i + 1) + (i + 1) * SPACE_BETWEEN_SLIDES, position[1] - height,
        #                                SLIDE_WIDTH * (i + 1) + (i + 1) * SPACE_BETWEEN_SLIDES, position[1] + height)
        #     pen = QPen(Qt.black)
        #     pen.setWidth(200)
        #     x_line.setPen(pen)
        #     self.scene.addItem(x_line)

        y_position = SLIDE_HEIGHT
        y_line = QGraphicsLineItem(-height_tick, SLIDE_HEIGHT, height_tick, SLIDE_HEIGHT)
        pen = QPen(Qt.black)
        pen.setWidth(200)
        y_line.setPen(pen)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = myWindow()
    # window.prior = SerialSingleton().serial
    # window.x = 5000
    # window.y = 5000
    # window.z = 5000
    window.show()
    app.exec_()
