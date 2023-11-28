import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLabel

from app.ui_utils import get_project_root


class ResizableImageHolder(QLabel):
    '''
    Permet d'afficher une image qui s'adapte automatiquement à la taille du widget
    '''

    def __init__(self, image, min_factor=0):
        super(ResizableImageHolder, self).__init__()

        self.image = image
        self.min_factor = min_factor

    def resizeEvent(self, event) -> None:
        super(ResizableImageHolder, self).resizeEvent(event)
        scale_factor = min(event.size().width(), event.size().height())
        scale_factor = max(scale_factor, self.min_factor)
        new_image = self.image.scaled(scale_factor, scale_factor, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(new_image)


class Logo(QWidget):

    def __init__(self, parent=None):
        super(Logo, self).__init__(parent)

        logo_sgs = QPixmap(os.path.join(get_project_root(), "Logos/Logo_SGS.png"))
        logo_label = ResizableImageHolder(logo_sgs, min_factor=200)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        layout = QVBoxLayout()
        layout.addWidget(logo_label)
        self.setLayout(layout)

    #     self.display()
    #
    # def display(self):
    #     self.setFixedHeight(170)
