import functools
from pathlib import Path
from typing import Union

import qtawesome as qta
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QPainter
from PyQt5.QtWidgets import QFrame, QLabel, QDockWidget, QStyle, QWidget
from PyQt5.QtWidgets import QPushButton, QApplication, QToolButton


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        """
        Gray horizontal line which can be insert in layout.
        """
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: gray")
        self.setFixedHeight(1)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        """
        Gray horizontal line which can be insert in layout.
        """
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: gray")
        self.setFixedHeight(1)


class AnimatedOnHoverButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._background_color = QtGui.QColor("#19232D")
        self._font_color = QtGui.QColor("white")
        self._duration = 300

        self.display()

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    @property
    def font_color(self):
        return self._font_color

    @font_color.setter
    def font_color(self, value):
        self._font_color = value
        self.display()

    @property
    def background_color(self):
        return self.background_color

    @background_color.setter
    def background_color(self, value):
        self._background_color = value
        self.display()

    def display(self):
        self.style_sheet = """
                            display: block;
                            text-decoration: none;
                            border-radius: 4px;
                            padding: 20px 30px;

                            color: %s;
                            border: 2px solid %s;
                            text-align: center;

                            text-decoration: none;
                            border-radius: 20px;


                            background-color: %s;
                            font-family: Arial, sans-serif;
                            font-weight: bold;
                            font-size: 14px;
                            """ % (self._font_color.name(), self._font_color.name(), self._background_color.name())

        self.setStyleSheet(self.style_sheet)

    def helper_function(self, color, other_color):
        self.setStyleSheet(
            self.style_sheet + "background-color: {bckgd};  color: {font};".format(bckgd=other_color.name(),
                                                                                   font=color.name()))

    def apply_color_animation(self, start_color, end_color, duration=1000):
        anim = QtCore.QVariantAnimation(
            self,
            duration=duration,
            startValue=start_color,
            endValue=end_color,
            loopCount=1,
        )
        anim.valueChanged.connect(functools.partial(self.helper_function, start_color))
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.apply_color_animation(
            start_color=self._background_color,
            end_color=self._font_color,
            duration=self._duration
        )
        super().enterEvent(a0)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self.apply_color_animation(
            start_color=self._font_color,
            end_color=self._background_color,
            duration=self._duration
        )
        super().leaveEvent(a0)


class MapButton(AnimatedOnHoverButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        map_icon = qta.icon('mdi.map-marker', color=self._font_color)
        self.setIcon(map_icon)

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        map_icon = qta.icon('mdi.map-marker', color=self._background_color)
        self.setIcon(map_icon)
        super().enterEvent(a0)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        map_icon = qta.icon('mdi.map-marker', color=self._font_color)
        self.setIcon(map_icon)
        super().leaveEvent(a0)


class TitleSectionLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            color: #b5bac9; 
            font-size: 37px; 
            font-weight: lighter; 
            font-family: system-ui; 
            margin-right: 20px;
            """)


class FormLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            color: white; 
            font-size: 15px; 
            font-weight: lighter; 
            font-family: system-ui; 
            text-transform: uppercase;
            """)


class LongClickButton(QPushButton):
    click = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.auto_repeat_interval = 100
        self.setAutoRepeat(True)
        # self.setAutoRepeatDelay(100)
        self.setAutoRepeatInterval(self.auto_repeat_interval)
        self.clicked.connect(self.handleClicked)
        self._state = 0

    def handleClicked(self):
        if self.isDown():
            if self._state == 0:
                self._state = 1
                self.setAutoRepeatInterval(self.auto_repeat_interval)
                self.click.emit()
            else:
                self.click.emit()
        elif self._state == 1:
            self._state = 0
            self.setAutoRepeatInterval(self.auto_repeat_interval)
        else:
            self.click.emit()


class HideShowButton(QToolButton):
    """
    Custom eye button which indicates if a related object (that could be QGraphicsItem) is shown or hidden.
    """
    isclicked = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._show = True  # show mode
        self.display()

        self.clicked.connect(self.on_clicked)

    def on_clicked(self) -> None:
        """
        Change appearance on click (toggle hide/view displayed) and emit a signal
        """
        self.show = not self._show
        self.isclicked.emit(self._show)

    def display(self) -> None:
        """
        Change appearance : toggle hide/view displayed
        :return:
        """
        if self._show:
            eye_icon = qta.icon("fa5.eye", color="white")

        else:
            eye_icon = qta.icon("fa5.eye-slash", color="gray")

        self.setIcon(eye_icon)
        self.setStyleSheet("QToolButton{background-color:transparent;}")

    @property
    def show(self) -> bool:
        return self._show

    @show.setter
    def show(self, value: bool):
        self._show = value
        self.display()


class HoveredButton(QPushButton):
    def __init__(self, qta_icon: str, first_color: str = "white", second_color: str = "#346792",
                 q_size: QSize = QSize(30, 30), icon_factor: float = 1.5, parent=None):
        """
        Return button which is displaying a left arrow
        """
        super().__init__(parent)
        self.setMouseTracking(True)
        self.is_hover = False
        self.setStyleSheet("background: None;")
        self.setFixedSize(q_size)

        self.qta_icon = qta_icon
        self.first_color = first_color
        self.second_color = second_color
        self.icon_factor = icon_factor

        icon = qta.icon(qta_icon,
                        color_off=self.first_color,
                        color_active=self.first_color,
                        color=self.first_color,
                        color_disabled=self.first_color,
                        options=[{'scale_factor': self.icon_factor}])

        self.setIcon(icon)

        self.installEventFilter(self)

    def enterEvent(self, event) -> None:
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        icon = qta.icon(self.qta_icon,
                        color_off=self.second_color,
                        color=self.second_color,
                        color_active=self.second_color,
                        color_disabled=self.second_color,
                        options=[{'scale_factor': self.icon_factor}])
        self.setIcon(icon)

    def leaveEvent(self, event) -> None:
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        icon = qta.icon(self.qta_icon,
                        color_off=self.first_color,
                        color=self.first_color,
                        color_active=self.first_color,
                        color_disabled=self.first_color,
                        options=[{'scale_factor': self.icon_factor}])
        self.setIcon(icon)

    def mouseReleaseEvent(self, event, *args, **kwargs):
        icon = qta.icon(self.qta_icon,
                        color_off=self.first_color,
                        color=self.second_color,
                        color_active=self.second_color,
                        color_disabled=self.second_color,
                        options=[{'scale_factor': self.icon_factor}])
        self.setIcon(icon)
        QApplication.restoreOverrideCursor()
        super(HoveredButton, self).mouseReleaseEvent(event)


def get_project_root() -> Path:
    """
    Get path of project root
    :return: path of project root
    """
    return Path(__file__).parent.parent


class CustomDockWidget(QDockWidget):
    '''
    Widget de base de la plateforme image
    '''

    def __init__(self, title, parent=None):
        super(CustomDockWidget, self).__init__(title, parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.display()

    def display(self):
        title_bar_height = self.style().pixelMetric(QStyle.PM_TitleBarHeight)
        if title_bar_height < 35:
            self.setStyleSheet("QDockWidget::title{padding-top: 10px;}")

    def ignore_title_bar(self):
        self.setTitleBarWidget(QWidget())
        self.titleBarWidget().hide()


def get_map_cursor() -> QCursor:
    icon = qta.icon('fa.map-marker', color='gray')
    pixmap = icon.pixmap(icon.actualSize(QSize(32, 32)))
    return QCursor(pixmap)
