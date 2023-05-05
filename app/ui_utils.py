from PyQt5.QtWidgets import QFrame


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