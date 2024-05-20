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
from src.wordcloud import WordCloudWindow
from src.data_utils import DocumentData

class TableView(QWidget):
    def __init__(self):
        super(TableView, self).__init__()

        #table init
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        #button init
        self.button1 = QPushButton("Generate Wordcloud")
        self.button1.clicked.connect(self.open_selection_wordcloud) #on init open window

        # self.button2 = QPushButton("Prevailing topic wordcloud")
        # self.button2.clicked.connect(self.open_topic_wordcloud)  # on init open window

        self.main_layout = QVBoxLayout()
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        #upper part
        self.main_layout.addWidget(self.button1, alignment=Qt.AlignmentFlag.AlignTop)
        self.main_layout.setStretchFactor(self.button1, 0)
        # self.main_layout.addWidget(self.button2, alignment=Qt.AlignmentFlag.AlignTop)
        # self.main_layout.setStretchFactor(self.button2, 0)
        
        #lower part
        # size.setVerticalStretch(100)
        # self.table.setSizePolicy(size)
        self.main_layout.addWidget(self.table)
        self.main_layout.setStretchFactor(self.table, 100)

        self.setLayout(self.main_layout)

        self.document_data = None


    def open_selection_wordcloud(self):
        self.new_window = WordCloudWindow(self.document_data)
        self.new_window.show()

    # def open_topic_wordcloud(self):
    #     self.new_window = WordCloudWindow(self.document_data, use_topic=True)
    #     self.new_window.show()
