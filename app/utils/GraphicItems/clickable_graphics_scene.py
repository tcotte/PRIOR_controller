from typing import Final

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui_utils import get_map_cursor
from app.utils.position import Position

SPACE_BETWEEN_SLIDES: Final = 3300
SLIDE_WIDTH: Final = 26000
SLIDE_HEIGHT: Final = 76000

OVERLAP = 90
IMAGE_SIZE = (210, 175)


class ClickableGraphicsScene(QGraphicsScene):
    position_clicked_signal = pyqtSignal(object, str)

    def __init__(self):
        super(ClickableGraphicsScene, self).__init__()
        self._clickable_status = False
        self.position_widget = None

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self._clickable_status:
            self.position_clicked_signal.emit(Position.fromQPointF(point=event.scenePos()), self.position_widget)
            self.clickable_status = False

        return super().mousePressEvent(event)

    @property
    def clickable_status(self) -> bool:
        return self._clickable_status

    @clickable_status.setter
    def clickable_status(self, value: bool) -> None:
        self._clickable_status = value

        if value:
            QApplication.setOverrideCursor(get_map_cursor())
            self.position_widget = self.sender().objectName()
        else:
            QApplication.restoreOverrideCursor()