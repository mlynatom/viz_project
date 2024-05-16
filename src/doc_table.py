import sys
from typing import Literal, Union

import numpy as np
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import (QAction, QBrush, QColor, QKeySequence, QPainter,
                           QPen, QSurfaceFormat, QTransform)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QComboBox, QGraphicsScene,
                               QGraphicsView, QHBoxLayout, QHeaderView, QLabel,
                               QMainWindow, QMenuBar, QSizePolicy, QSpinBox,
                               QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton)

from src.data_utils import DocumentData
from src.doc_landscape import VisGraphicsScene, VisGraphicsView

class TableView(QWidget):
    def __init__(self):
        super(TableView, self).__init__()

        #table init
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        #button init
        self.button = QPushButton("View Words")
        #TODO connect to the words selected by the compass

        self.main_layout = QVBoxLayout()
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        #upper part
        self.main_layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignTop)
        self.main_layout.setStretchFactor(self.button, 0)
        
        #lower part
        # size.setVerticalStretch(100)
        # self.table.setSizePolicy(size)
        self.main_layout.addWidget(self.table)
        self.main_layout.setStretchFactor(self.table, 100)

        self.setLayout(self.main_layout)
