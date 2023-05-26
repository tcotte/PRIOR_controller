import sys
from typing import List

import qdarkstyle
import qtawesome as qta
import yaml
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QHBoxLayout, QListWidget, QPushButton, \
    QVBoxLayout, QDialog, QLineEdit, QDialogButtonBox, QApplication, QFormLayout, QSpinBox, \
    QAbstractItemView

from app.go_to_windows import X_RANGE, Y_RANGE, Z_RANGE
from app.notifications import Warn
from app.ui_utils import QHLine, HideShowButton, HoveredButton


class PositionObject:
    def __init__(self, name: str, x: int, y: int, z: int):
        self._name = name
        self._x = x
        self._y = y
        self._z = z

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        self._y = value

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        self._x = value

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, value: int) -> None:
        self._z = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def __str__(self):
        return f"{self.name} - {self._x} {self._y} {self._z}"


class PositionWidget(QWidget):
    remove_element_signal = pyqtSignal(str)
    go_to_signal = pyqtSignal(object)

    def __init__(self, position: PositionObject, parent=None):
        """
        This class is a widget which displays an element. It is only composed in a trash (to delete the widget) and a
        label which displays the element's name
        :param element_name: name of the element
        :param parent: Element manager
        """
        super(PositionWidget, self).__init__()
        # self.resize(500, 50)

        self.parent = parent

        self.hide_show_cb = HideShowButton()

        self.trash_btn = HoveredButton(qta_icon='fa5.trash-alt', first_color="gray", icon_factor=1)
        self.play_btn = HoveredButton(qta_icon='fa5s.play', first_color="gray", second_color="green", icon_factor=1)

        self.name_label = QLabel()
        self.x_label = QLabel()
        self.y_label = QLabel()
        self.z_label = QLabel()
        self.name_label.setStyleSheet("background:transparent;")

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.trash_btn)
        main_layout.addWidget(self.name_label, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.x_label, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.y_label, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.z_label, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.play_btn)
        self.setLayout(main_layout)

        # construct
        self._position = None
        self.position = position

        self.connect_actions()

        self.display()

    def go2position(self):
        self.go_to_signal.emit(self.position)

    def display(self):
        self.setStyleSheet("QLabel {background: transparent;}")

    def connect_actions(self) -> None:
        self.trash_btn.clicked.connect(self.remove_item)
        self.play_btn.clicked.connect(self.go2position)

    def remove_item(self) -> None:
        """
        Emit a signal when the trash is clicked. This signal send the name of the element and the list will delete this
        element.
        """
        self.remove_element_signal.emit(self.position.name)

    # properties
    @property
    def position(self) -> PositionObject:
        return self._position

    @position.setter
    def position(self, value: position) -> None:
        """
        Set new position
        :param value: position value.
        """
        self._position = value
        self.name_label.setText(value.name)
        self.x_label.setText(str(value.x))
        self.y_label.setText(str(value.y))
        self.z_label.setText(str(value.z))

    # @property
    # def element_name(self) -> str:
    #     return self._element_name
    #
    # @element_name.setter
    # def element_name(self, value: str) -> None:
    #     """
    #     Set new element name into respective label.
    #     :param value: element name
    #     """
    #     self._element_name = value
    #     self.position_name_label.setText(value)


class PositionManager(QDialog):
    def __init__(self, parent=None, init_elements=None):
        """
        This class aims to manage all CategoryWidget (element widgets):
        :param init_elements: name of initial elements which have to appeared in the list when the window is shown.
        """
        super(PositionManager, self).__init__(parent)
        if init_elements is None:
            init_elements = []
        self.title = "Category Selection"

        self.parent = parent

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            '''
            QListWidget::item:selected {
                background: None;
            }
            QListWidget QWidget[widgetItem=true] {
                background: transparent;
            }
            ''')
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)

        self.resize(400, 500)

        plus_icon = qta.icon('mdi6.plus-circle')
        edit_icon = qta.icon('mdi6.pencil-outline')

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok, self)

        self.button_box.accepted.connect(self.accept)

        self.add_btn = QPushButton(plus_icon, '')
        self.edit_btn = QPushButton(edit_icon, '')

        empty_label = QLabel("")
        # empty_label.setFixedWidth(2)

        labels_layout = QHBoxLayout()
        labels_layout.addWidget(empty_label, alignment=Qt.AlignHCenter)
        labels_layout.addWidget(QLabel("Name"), alignment=Qt.AlignHCenter)
        labels_layout.addWidget(QLabel("X"), alignment=Qt.AlignHCenter)
        labels_layout.addWidget(QLabel("Y"), alignment=Qt.AlignHCenter)
        labels_layout.addWidget(QLabel("Z"), alignment=Qt.AlignHCenter)
        labels_layout.addWidget(empty_label, alignment=Qt.AlignHCenter)

        # type_label.setAlignment(QtCore.Qt.AlignCenter)
        # size_label.setAlignment(QtCore.Qt.AlignCenter)
        labels_layout.setAlignment(QtCore.Qt.AlignTop)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(labels_layout)
        main_layout.addWidget(self.list_widget)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(QHLine())
        main_layout.addWidget(self.button_box)

        # main_layout.setSpacing(20)
        # labels_layout.setSpacing(20)

        self.add_btn.clicked.connect(self.enter_new_position)
        self.edit_btn.clicked.connect(self.edit_position)
        self.list_widget.itemSelectionChanged.connect(self.toggle_edition_access)

        # Construct
        self.toggle_edition_access()
        self.add_elements(elements=init_elements)

    def accept(self) -> None:
        self.save_positions(filename=r"C:\Users\tristan_cotte\PycharmProjects\PRIOR_controller\positions_cfg.yaml")
        self.close()

    def save_positions(self, filename: str) -> None:
        data = [{"name": pos.name, "x": pos.x, "y": pos.y, "z": pos.z} for pos in self.get_positions()]
        with open(filename, 'w') as file:
            yaml.dump(data, file)

    def toggle_edition_access(self) -> None:
        if len(self.list_widget.selectedItems()) > 0:
            self.edit_btn.setEnabled(True)
        else:
            self.edit_btn.setEnabled(False)

    def edit_position(self) -> None:
        item = self.list_widget.itemFromIndex(self.list_widget.selectedIndexes()[0])
        item_widget = self.list_widget.itemWidget(item)

        led = PositionEditDialog(description="Edit position", input_position=item_widget.position)

        if led.exec_() == QDialog.Accepted:
            item_widget.position = led.get_new_position()

    def add_elements(self, elements: List[PositionObject]) -> None:
        """
        Add new elements in self.list_widget
        :param elements: list of elements
        """
        for x in elements:
            widget = PositionWidget(position=x, parent=self)
            widget.remove_element_signal.connect(self.rm_element_in_list)
            widget.go_to_signal.connect(self.go2position)
            item = QListWidgetItem()
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            item.setSizeHint(widget.sizeHint())

    def go2position(self, value: PositionObject):
        print(value.x, value.y, value.z)

    def get_elements(self) -> List[str]:
        """
        Retrieve all elements in the widgets disposed in self.list_widget (QListWidget)
        :return: name of elements in list
        """
        element_list = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(item)
            element_list.append(item_widget.position.name)
        return element_list

    def get_positions(self) -> List[PositionObject]:
        """
        Retrieve all elements in the widgets disposed in self.list_widget (QListWidget)
        :return: name of elements in list
        """
        position_list = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(item)
            position_list.append(item_widget.position)
        return position_list

    def enter_new_position(self) -> None:
        """
        When the user clicks on "add button", it shows a QDialog where the user can set a new element into the list.
        If the user clicks on "Ok" and the element is not already in the list -> add this element else do anything.
        """
        led = PositionEditDialog(description="Enter new position")

        if led.exec_() == QDialog.Accepted:
            new_element = led.get_text()
            if new_element not in self.get_elements():
                self.add_elements(elements=[led.get_new_position()])
            else:
                Warn("This item already exist")

    def rm_element_in_list(self, value: str) -> None:
        """
        Remove element from QListWidget once it had been delete clicking on the trash icon.
        :param value: name of the element removed by the user.
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(item)

            if item_widget.position.name == value:
                self.list_widget.takeItem(i)
                break


class PositionEditDialog(QDialog):
    def __init__(self, description: str, input_position: PositionObject = None, parent=None):
        """
        QDialog where the user can set a new element into the list (QListWidget) of elements.
        :param description: QDialog's description
        """
        super(PositionEditDialog, self).__init__(parent)
        # self.title = "Add position"

        self.input_position = input_position

        layout = QVBoxLayout(self)
        description_label = QLabel(description)

        form_layout = QFormLayout()

        self.name_le = QLineEdit()
        self.x_sp = QSpinBox()
        self.y_sp = QSpinBox()
        self.z_sp = QSpinBox()
        for sp, range in zip([self.x_sp, self.y_sp, self.z_sp], [X_RANGE, Y_RANGE, Z_RANGE]):
            sp.setRange(*range)

        if input_position is not None:
            self.name_le.setText(input_position.name)
            self.x_sp.setValue(input_position.x)
            self.y_sp.setValue(input_position.y)
            self.z_sp.setValue(input_position.z)

        self.name_le.setMaxLength(15)
        layout.addWidget(description_label)

        form_layout.addRow(QLabel("Name"), self.name_le)
        form_layout.addRow(QLabel("X"), self.x_sp)
        form_layout.addRow(QLabel("Y"), self.y_sp)
        form_layout.addRow(QLabel("Z"), self.z_sp)
        # layout.addWidget(self.name_le)
        layout.addLayout(form_layout)

        # Ok and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)

        if self.input_position is None:
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        layout.addWidget(self.buttons)

        self.connect_actions()

    def connect_actions(self):
        if self.input_position is None:
            self.name_le.textChanged.connect(self.enable_ok_btn)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def enable_ok_btn(self) -> None:
        """
        Enable the "Ok" button if the QLineEdit where user enters new element is not empty.
        """
        if self.get_text() != "":
            enable = True
        else:
            enable = False
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(enable)

    def get_text(self) -> str:
        """
        Get the entered in QLineEdit
        :return: str
        """
        return self.name_le.text()

    def get_new_position(self) -> PositionObject:
        return PositionObject(name=self.name_le.text(), x=self.x_sp.value(), y=self.y_sp.value(), z=self.z_sp.value())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    # list_pos = [
    #     PositionObject(name="Sample 1", x=200, y=300, z=5000),
    #     PositionObject(name="Sample 2", x=200, y=300, z=5000),
    #     PositionObject(name="Sample 3", x=200, y=300, z=3000)
    # ]

    with open(r"C:\Users\tristan_cotte\PycharmProjects\PRIOR_controller\positions_cfg.yaml", 'r') as file:
        positions = yaml.safe_load(file)

    list_pos = [PositionObject(**pos) for pos in positions]

    window = PositionManager(init_elements=list_pos)
    window.show()
    app.exec_()
