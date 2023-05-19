import sys

import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QListView, QApplication, QDialog

from app.defined_positions import PositionObject


class CustomWidget(QWidget):
    def __init__(self, parent=None):
        super(CustomWidget, self).__init__(parent)
        self.button = QPushButton("button")
        lay = QHBoxLayout(self)
        lay.addWidget(self.button, alignment=QtCore.Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent=parent)
        vLayout = QVBoxLayout(self)
        self.list_view = QListView(self)
        vLayout.addWidget(self.list_view)
        # self.model = TableModel(self.list_view)
        self.model = TableModel([])
        # self.model.setHeaderData()
        codes = [
            'windows',
            'windows xp',
            'windows7',
            'hai',
            'habit',
            'hack',
            'good'
        ]
        self.list_view.setModel(self.model)

        # self.setHeaderData(1, Qt.Horizontal, "Range")
        # for code in codes:
        #     item = QStandardItem(code)
        #     self.model.appendRow(item)
        #     self.list_view.setIndexWidget(item.index(), CustomWidget())


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()

        self.horizontalHeaders = [''] * 2

        self.setHeaderData(0, Qt.Horizontal, "Driver")
        self.setHeaderData(1, Qt.Horizontal, "Range")

        self._data = data
        print(data)

    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        print(data)
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.horizontalHeaders[section]
            except:
                pass
        return super().headerData(section, orientation, role)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    list_pos = [
        PositionObject(name="Sample 1", x=200, y=300, z=5000),
        PositionObject(name="Sample 2", x=200, y=300, z=5000),
        PositionObject(name="Sample 3", x=200, y=300, z=3000)
    ]
    window = Dialog()
    # window.x = 5000
    # window.y = 5000
    # window.z = 5000
    window.show()
    app.exec_()
